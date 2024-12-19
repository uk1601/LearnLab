
import os
import json
import requests
import io
from typing import List, Dict, Any, Optional, TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field
from pydub import AudioSegment
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import Graph, StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from utils.rag_application import RAGApplication
from langchain_groq import ChatGroq
from datetime import datetime

from utils.podcast_s3_storage import S3Storage
from utils.semantic_cache import PodcastCache


load_dotenv()

# Enhanced state models
class RAGContext(BaseModel):
    question: str
    pdf_title: str
    answer: Optional[str] = None
    evidence: List[str] = []

class PodcastSegment(BaseModel):
    speaker: str
    text: str
    expression: Optional[str] = None

class GraphState(BaseModel):
    messages: List[BaseMessage]
    topic: str
    script: Optional[str] = None 
    current_stage: str
    rag_context: Optional[RAGContext] = None
    pdf_title: Optional[str] = None

class PodcastScript(BaseModel):
    segments: List[PodcastSegment] = Field(description="List of podcast segments")

# Updated prompts
TOPIC_EXPANSION_PROMPT = """You are an expert podcast planner. Create a detailed outline for a 3-5 minute 
podcast discussion between two speakers using the provided research context.

Topic: {topic}

Research Context:
{rag_context}

Focus on:
1. Breaking down complex concepts from the research
2. Including specific examples from the provided context
3. Natural conversation flow
4. Key insights and their implications

Current conversation: {messages}
"""

SCRIPT_GENERATION_PROMPT = """You are a professional podcast script writer. Create a natural conversation 
between two speakers based on the research context and outline provided.

Research Context:
{rag_context}

Guidelines:
- Speaker 1 is the expert/host who explains the research findings
- Speaker 2 asks insightful questions and seeks clarification
- Include natural elements like "umm", "hmm" for Speaker 2
- Add [laughs], [sighs] for emotional moments
- Reference specific findings from the research
- Keep the tone conversational yet informative
- Ensure the script runs 3-5 minutes when read aloud

Keep it as Speaker 1 and Speaker 2 only because don't add any names to it because I will parsing the script to make it work as 2 different Audios


Previous messages: {messages}
Outline: {outline}
"""

REFINE_SCRIPT_PROMPT = """Refine this research-based podcast script while maintaining its structure:
1. Keep the Speaker 1: and Speaker 2: format
2. Add appropriate pauses and emphasis
3. Ensure natural flow between segments
4. Maintain all expression markers like [laughs], [sighs]
5. Keep the research content accurate while making it engaging

Current script:
{script}

Return the enhanced script only, maintaining the exact same format."""

GROQ_API_KEY = os.getenv("GROQ_API_KEY")



class PodcastGenerator:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=GROQ_API_KEY)
        self.rag_app = RAGApplication()
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_ids = {
            "Speaker 1": os.getenv("ELEVENLABS_VOICE_ID_1"),
            "Speaker 2": os.getenv("ELEVENLABS_VOICE_ID_2")
        }
        
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set")
        if not all(self.voice_ids.values()):
            raise ValueError("Voice IDs not properly configured")
        
                # Add S3 initialization
        self.s3_storage = S3Storage(bucket_name=os.getenv("AWS_BUCKET_NAME"))
        
        # Verify AWS credentials
        if not all([
            os.getenv("AWS_ACCESS_KEY_ID"),
            os.getenv("AWS_SECRET_ACCESS_KEY"),
            os.getenv("AWS_BUCKET_NAME")
        ]):
            raise ValueError("AWS credentials not properly configured")
        
        if not all([
            os.getenv("UPSTASH_VECTOR_REST_URL"),
            os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        ]):
            raise ValueError("Upstash credentials not properly configured")
            
        self.cache = PodcastCache()

    def create_graph(self):
        workflow = StateGraph(GraphState)
        
        # Add RAG node at the beginning
        workflow.add_node("rag_retrieval", self.retrieve_context)
        workflow.add_node("topic_expansion", self.expand_topic)
        workflow.add_node("script_generation", self.generate_script)
        workflow.add_node("script_refinement", self.refine_script)
        workflow.add_node("tts_generation", self.generate_tts)
        
        # Update workflow to start with RAG
        workflow.add_edge("rag_retrieval", "topic_expansion")
        workflow.add_edge("topic_expansion", "script_generation")
        workflow.add_edge("script_generation", "script_refinement")
        workflow.add_edge("script_refinement", "tts_generation")
        
        workflow.set_entry_point("rag_retrieval")
        return workflow.compile()

    def retrieve_context(self, state: GraphState) -> GraphState:
        """New node for RAG context retrieval"""
        if not state.rag_context or not state.pdf_title:
            raise ValueError("RAG context or PDF title not provided")
            
        # Query the RAG system
        rag_response = self.rag_app.query_document(
            state.rag_context.question, 
            state.pdf_title
        )
        
        # Update RAG context
        state.rag_context.answer = rag_response["answer"]
        state.rag_context.evidence = rag_response["relevant_chunks"]
        
        # Add context to messages
        context_message = f"""Research Context:
        Answer: {rag_response['answer']}
        Evidence: {' '.join(rag_response['relevant_chunks'])}"""
        
        state.messages.append(AIMessage(content=context_message))
        state.current_stage = "rag_retrieval"
        return state

    def expand_topic(self, state: GraphState) -> GraphState:
        prompt = ChatPromptTemplate.from_template(TOPIC_EXPANSION_PROMPT)
        
        # Format RAG context
        rag_context = f"""Answer: {state.rag_context.answer}
        Evidence: {' '.join(state.rag_context.evidence)}"""
        
        formatted_prompt = prompt.format_messages(
            topic=state.topic,
            rag_context=rag_context,
            messages="\n".join([msg.content for msg in state.messages])
        )
        
        response = self.llm.invoke(formatted_prompt)
        state.messages.append(AIMessage(content=response.content))
        state.current_stage = "topic_expansion"
        return state

    def generate_script(self, state: GraphState) -> GraphState:
        prompt = ChatPromptTemplate.from_template(SCRIPT_GENERATION_PROMPT)
        
        rag_context = f"""Answer: {state.rag_context.answer}
        Evidence: {' '.join(state.rag_context.evidence)}"""
        
        formatted_prompt = prompt.format_messages(
            rag_context=rag_context,
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
        prompt = ChatPromptTemplate.from_template(REFINE_SCRIPT_PROMPT)
        formatted_prompt = prompt.format_messages(script=state.script)
        response = self.llm.invoke(formatted_prompt)
        
        state.script = response.content
        state.messages.append(AIMessage(content=response.content))
        state.current_stage = "script_refinement"
        return state
    
    def generate_tts(self, state: GraphState) -> GraphState:
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
        
        # Generate a temporary local file
        temp_file = f"temp_podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        combined_audio.export(temp_file, format="mp3")
        
        # Upload to S3 and get URL
        try:
            s3_url = self.s3_storage.upload_file(
                file_path=temp_file,
                podcast_title=state.topic,
                pdf_title=state.pdf_title
            )
            
            # Add S3 URL to state message
            state.messages.append(
                AIMessage(content=f"Podcast audio generated and uploaded to S3: {s3_url}")
            )
            
        except Exception as e:
            # If S3 upload fails, keep the local file as backup
            print(f"Warning: S3 upload failed - {str(e)}")
            state.messages.append(
                AIMessage(content=f"Warning: S3 upload failed. Podcast saved locally as {temp_file}")
            )
        
        state.current_stage = "complete"
        return state

    def generate_podcast(self, question: str, pdf_title: str) -> Dict[str, Any]:
        """Generate a podcast from a question and PDF"""
        graph = self.create_graph()
        
        initial_state = GraphState(
            messages=[HumanMessage(content=f"Create a podcast about: {question}")],
            topic=question,
            script=None,
            current_stage="start",
            rag_context=RAGContext(
                question=question,
                pdf_title=pdf_title
            ),
            pdf_title=pdf_title
        )
        
        final_state = graph.invoke(initial_state)
        
        # Get the S3 URL from the last message
        s3_url = None
        for message in reversed(final_state["messages"]):
            if "uploaded to S3:" in message.content:
                s3_url = message.content.split("uploaded to S3: ")[-1]
                break
        
        return {
            "topic": question,
            "script": final_state["script"],
            "conversation_history": [m.content for m in final_state["messages"]],
            "source_pdf": pdf_title,
            "s3_url": s3_url,
            "rag_context": {
                "answer": final_state["rag_context"].answer,
                "evidence": final_state["rag_context"].evidence
            }
        }
    

    def parse_unstructured_script(self, script_text: str) -> PodcastScript:
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

    def process_document(self, pdf_path: str) -> bool:
        """Process and index a new document"""
        return self.rag_app.process_document(pdf_path)

    def list_available_pdfs(self) -> List[str]:
        """Get list of available indexed PDFs"""
        return self.rag_app.list_available_pdfs()
    
    def generate_podcast(self, question: str, pdf_title: str) -> Dict[str, Any]:
        """Generate a podcast with caching"""
        # Check cache first
        cached_result = self.cache.get_cached_podcast(question, pdf_title)
        
        if cached_result:
            print(f"Found cached podcast! S3 URL: {cached_result['s3_url']}")
            return {
                **cached_result,
                'cached': True
            }
        
        # If not in cache, generate new podcast
        print("No cached version found. Generating new podcast...")
        result = self._generate_new_podcast(question, pdf_title)
        
        # Cache the result
        if result.get('s3_url'):  # Only cache if generation was successful
            self.cache.cache_podcast(question, pdf_title, result)
            
        return {
            **result,
            'cached': False
        }

    def _generate_new_podcast(self, question: str, pdf_title: str) -> Dict[str, Any]:
        """Internal method for generating new podcast"""
        graph = self.create_graph()
        
        initial_state = GraphState(
            messages=[HumanMessage(content=f"Create a podcast about: {question}")],
            topic=question,
            script=None,
            current_stage="start",
            rag_context=RAGContext(
                question=question,
                pdf_title=pdf_title
            ),
            pdf_title=pdf_title
        )
        
        final_state = graph.invoke(initial_state)
        
        # Get the S3 URL from the last message
        s3_url = None
        for message in reversed(final_state["messages"]):
            if "uploaded to S3:" in message.content:
                s3_url = message.content.split("uploaded to S3: ")[-1]
                break
        
        return {
            "topic": question,
            "script": final_state["script"],
            "conversation_history": [m.content for m in final_state["messages"]],
            "source_pdf": pdf_title,
            "s3_url": s3_url,
            "rag_context": {
                "answer": final_state["rag_context"].answer,
                "evidence": final_state["rag_context"].evidence
            }
        }

# Main execution code remains the same, but simplified since we don't need RAGPodcastGenerator class anymore
def display_menu():
    print("\nRAG Podcast Generator Menu:")
    print("1. List available documents")
    print("2. Index new document")
    print("3. Generate podcast from existing document")
    print("4. Exit")
    print("-" * 50)

def handle_index_document(generator: PodcastGenerator):
    """Handle document indexing with improved path handling"""
    pdf_path = input("\nEnter the path to the PDF file: ").strip()
    
    # Handle paths with spaces and special characters
    try:
        expanded_path = os.path.expanduser(pdf_path)
        cleaned_path = pdf_path.replace('\\', '')
        
        # Try different path variations
        for path in [pdf_path, expanded_path, cleaned_path]:
            if os.path.exists(path):
                print(f"\nProcessing document: {path}")
                if generator.process_document(path):
                    print("Document successfully indexed!")
                    return
                
        print("Error: File not found. Please check the path and try again.")
        print("Tips for entering file paths:")
        print("1. Use forward slashes (/) instead of backslashes")
        print("2. You can drag and drop the file into the terminal")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")

# Modify the main handler function
def handle_podcast_generation(generator: PodcastGenerator):
    pdfs = generator.list_available_pdfs()
    if not pdfs:
        print("\nNo documents available. Please index some documents first.")
        return
        
    print("\nAvailable PDFs:")
    for i, pdf in enumerate(pdfs, 1):
        print(f"{i}. {pdf}")
        
    while True:
        try:
            selection = int(input("\nSelect PDF number: ")) - 1
            if 0 <= selection < len(pdfs):
                selected_pdf = pdfs[selection]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
            
    question = input("\nEnter your question about the document: ").strip()
    
    print(f"\nProcessing query: {question}")
    print(f"Using PDF: {selected_pdf}")
    
    result = generator.generate_podcast(question, selected_pdf)
    
    if result.get('cached'):
        print("\nRetrieved cached podcast!")
        print(f"S3 URL: {result['s3_url']}")
    else:
        print("\nGenerated new podcast!")
        print(f"S3 URL: {result['s3_url']}")
    
    # Save result to local file for reference
    with open("podcast_output.json", "w") as f:
        json.dump(result, f, indent=2)
        
    print("\nResults saved to podcast_output.json")

def main():
    try:
        print("Initializing Podcast Generator...")
        generator = PodcastGenerator()
        
        while True:
            display_menu()
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                pdfs = generator.list_available_pdfs()
                print("\nAvailable PDFs:")
                if not pdfs:
                    print("No documents indexed yet.")
                else:
                    for pdf in pdfs:
                        print(f"- {pdf}")
                        
            elif choice == "2":
                handle_index_document(generator)
                
            elif choice == "3":
                handle_podcast_generation(generator)
                
            elif choice == "4":
                print("\nExiting Podcast Generator...")
                break
                
            else:
                print("\nInvalid choice. Please select 1-4.")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()