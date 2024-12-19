import os
import json
import requests
import io
from typing import List, Dict, Any, Optional, TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field
from pydub import AudioSegment
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import Graph, StateGraph, START,END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser

load_dotenv()
# Output models remain the same
class PodcastSegment(BaseModel):
    speaker: str
    text: str
    expression: Optional[str] = None

# Update the GraphState class to make script properly Optional
class GraphState(BaseModel):
    messages: List[BaseMessage]
    topic: str
    script: Optional[str] = None 
    current_stage: str

# Add this after PodcastSegment class and before GraphState class
class PodcastScript(BaseModel):
    segments: List[PodcastSegment] = Field(description="List of podcast segments")

# Add the new REFINE_SCRIPT_PROMPT
TOPIC_EXPANSION_PROMPT = """You are an expert podcast planner. Given a topic, create a detailed outline 
for a 3-5 minute podcast discussion between two speakers. The outline should include key points, 
questions, and discussion flow.

Topic: {topic}

Focus on:
1. Breaking down complex concepts
2. Including real-world examples
3. Natural conversation flow
4. Interesting tangents and follow-up questions

Current conversation: {messages}
"""

SCRIPT_GENERATION_PROMPT = """You are a professional podcast script writer. Using the outline and discussion
points, create a natural conversation between two speakers. Make it engaging and educational.

Guidelines:
- Speaker 1 is the expert/host
- Speaker 2 is curious and asks good questions
- Include natural elements like "umm", "hmm" for Speaker 2
- Add [laughs], [sighs] for emotional moments
- Keep the tone conversational and friendly
- Ensure the script runs 3-5 minutes when read aloud

Previous messages: {messages}
Outline: {outline}
"""

REFINE_SCRIPT_PROMPT = """Refine and enhance this podcast script while maintaining its exact structure:
1. Keep the Speaker 1: and Speaker 2: format
2. Add appropriate pauses and emphasis
3. Ensure natural flow between segments
4. Maintain all expression markers like [laughs], [sighs]
5. Keep the same basic content but make it more engaging

Current script:
{script}

Return the enhanced script only, maintaining the exact same format."""

class PodcastGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_ids = {
            "Speaker 1": os.getenv("ELEVENLABS_VOICE_ID_1"),
            "Speaker 2": os.getenv("ELEVENLABS_VOICE_ID_2")
        }
        
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set in the environment variables.")
        if not all(self.voice_ids.values()):
            raise ValueError("Both ELEVENLABS_VOICE_ID_1 and ELEVENLABS_VOICE_ID_2 must be set.")
    
    def create_graph(self):
        workflow = StateGraph(GraphState)
        
        # Add nodes including new TTS node
        workflow.add_node("topic_expansion", self.expand_topic)
        workflow.add_node("script_generation", self.generate_script)
        workflow.add_node("script_refinement", self.refine_script)
        workflow.add_node("tts_generation", self.generate_tts)
        
        # Define edges including new TTS stage
        workflow.add_edge("topic_expansion", "script_generation")
        workflow.add_edge("script_generation", "script_refinement")
        workflow.add_edge("script_refinement", "tts_generation")
        
        workflow.set_entry_point("topic_expansion")
        return workflow.compile()
        

    def expand_topic(self, state: GraphState) -> GraphState:
        """Expand the topic into detailed discussion points."""
        prompt = ChatPromptTemplate.from_template(TOPIC_EXPANSION_PROMPT)
        formatted_prompt = prompt.format_messages(
            topic=state.topic,
            messages="\n".join([msg.content for msg in state.messages])
        )
        response = self.llm.invoke(formatted_prompt)
        state.messages.append(AIMessage(content=response.content))
        state.current_stage = "topic_expansion"
        return state

    def generate_script(self, state: GraphState) -> GraphState:
        """Generate the initial podcast script."""
        prompt = ChatPromptTemplate.from_template(SCRIPT_GENERATION_PROMPT)
        formatted_prompt = prompt.format_messages(
            messages="\n".join([msg.content for msg in state.messages]),
            outline=state.messages[-1].content
        )
        response = self.llm.invoke(formatted_prompt)
        
        try:
            script_structured = PodcastScript.parse_raw(response.content)
            state.script = script_structured.json()
        except:
            state.script = response.content
            
        state.messages.append(AIMessage(content=response.content))
        state.current_stage = "script_generation"
        return state

    def refine_script(self, state: GraphState) -> GraphState:
        """Refine and polish the script."""
        prompt = ChatPromptTemplate.from_template(REFINE_SCRIPT_PROMPT)
        formatted_prompt = prompt.format_messages(script=state.script)
        response = self.llm.invoke(formatted_prompt)
        
        state.script = response.content
        state.messages.append(AIMessage(content=response.content))
        state.current_stage = "script_refinement"
        return state

    def generate_tts(self, state: GraphState) -> GraphState:
        """Generate TTS audio for the podcast script."""
        if not state.script:
            raise ValueError("No script available for TTS generation.")
        
        try:
            script = PodcastScript.parse_raw(state.script)
        except:
            script = self.parse_unstructured_script(state.script)
        
        audio_segments = []
        
        for segment in script.segments:
            voice_id = self.voice_ids.get(segment.speaker)
            if not voice_id:
                raise ValueError(f"Voice ID for {segment.speaker} not configured.")
            
            audio_data = self.synthesize_speech(segment.text, voice_id)
            audio_segments.append(audio_data)
        
        combined_audio = AudioSegment.empty()
        for audio in audio_segments:
            combined_audio += audio + AudioSegment.silent(duration=500)
        
        output_path = "podcast_episode.mp3"
        combined_audio.export(output_path, format="mp3")
        
        state.messages.append(AIMessage(content=f"Podcast audio generated and saved to {output_path}."))
        state.current_stage = "complete"
        return state

    def parse_unstructured_script(self, script_text: str) -> PodcastScript:
        """Parse unstructured script into PodcastScript format."""
        segments = []
        for line in script_text.split('\n'):
            if line.strip() == "":
                continue
            if line.startswith("Speaker 1:"):
                speaker = "Speaker 1"
                text = line.replace("Speaker 1:", "").strip()
            elif line.startswith("Speaker 2:"):
                speaker = "Speaker 2"
                text = line.replace("Speaker 2:", "").strip()
            else:
                speaker = "Speaker 1"
                text = line.strip()
            segments.append(PodcastSegment(speaker=speaker, text=text))
        return PodcastScript(segments=segments)

    def synthesize_speech(self, text: str, voice_id: str) -> AudioSegment:
        """Synthesize speech using ElevenLabs API."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            raise ValueError(f"ElevenLabs API Error: {response.status_code} - {response.text}")
        
        audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        return audio

# The generate_podcast function remains the same, but now it will work properly
def generate_podcast(topic: str) -> Dict[str, Any]:
    """Generate a complete podcast script and audio from a topic."""
    generator = PodcastGenerator()
    graph = generator.create_graph()
    
    # Initialize state - this will now work correctly
    initial_state = GraphState(
        messages=[HumanMessage(content=f"Create a podcast about: {topic}")],
        topic=topic,
        script=None,
        current_stage="start"
    )
    
    # Run the graph
    final_state = graph.invoke(initial_state)
    
    return {
        "topic": topic,
        "script": final_state["script"],
        "conversation_history": [m.content for m in final_state["messages"]]
    }

if __name__ == "__main__":
    topic = "The Future of Artificial Intelligence"
    try:
        result = generate_podcast(topic)
        print("\nPodcast generation completed successfully.")
        print("\nFinal Script:")
        print("-" * 80)
        print(result["script"])
        
        with open("podcast_script.json", "w") as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"An error occurred: {e}")