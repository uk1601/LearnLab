import os
from typing import List, Dict, Any, Optional, TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import Graph, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json

load_dotenv()

# Define the state type
class GraphState(TypedDict):
    messages: List[BaseMessage]
    topic: str
    script: Optional[str]
    current_stage: str

# Define output models for structure
class PodcastSegment(BaseModel):
    speaker: str
    text: str
    expression: Optional[str] = None

class PodcastScript(BaseModel):
    segments: List[PodcastSegment] = Field(description="List of podcast segments")

# System prompts
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

class PodcastGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.7)
        
    def create_graph(self):
        # Initialize the graph
        workflow = StateGraph(GraphState)
        
        # Define nodes
        workflow.add_node("topic_expansion", self.expand_topic)
        workflow.add_node("script_generation", self.generate_script)
        workflow.add_node("script_refinement", self.refine_script)
        
        # Define edges
        workflow.add_edge("topic_expansion", "script_generation")
        workflow.add_edge("script_generation", "script_refinement")
        
        # Set entry point
        workflow.set_entry_point("topic_expansion")
        
        # Compile graph
        return workflow.compile()
    
    def expand_topic(self, state: GraphState) -> GraphState:
        """Expand the topic into detailed discussion points."""
        prompt = ChatPromptTemplate.from_template(TOPIC_EXPANSION_PROMPT)
        messages = prompt.format_messages(
            topic=state["topic"],
            messages=state["messages"]
        )
        response = self.llm.invoke(messages)
        state["messages"].append(AIMessage(content=response.content))
        state["current_stage"] = "topic_expansion"
        return state
    
    def generate_script(self, state: GraphState) -> GraphState:
        """Generate the initial podcast script."""
        prompt = ChatPromptTemplate.from_template(SCRIPT_GENERATION_PROMPT)
        messages = prompt.format_messages(
            messages=state["messages"],
            outline=state["messages"][-1].content
        )
        response = self.llm.invoke(messages)
        
        # Parse into structured format
        parser = PydanticOutputParser(pydantic_object=PodcastScript)
        try:
            script_structured = parser.parse(response.content)
            state["script"] = script_structured.json()
        except:
            # Fallback to raw text if parsing fails
            state["script"] = response.content
            
        state["messages"].append(AIMessage(content=response.content))
        state["current_stage"] = "script_generation"
        return state
    
    def refine_script(self, state: GraphState) -> GraphState:
        """Refine and polish the script."""
        refine_prompt = """Enhance this podcast script to make it more engaging and natural.
        Add more personality, emotional cues, and ensure timing is appropriate for 3-5 minutes.
        
        Current script: {script}
        """
        
        prompt = ChatPromptTemplate.from_template(refine_prompt)
        messages = prompt.format_messages(script=state["script"])
        response = self.llm.invoke(messages)
        
        state["script"] = response.content
        state["messages"].append(AIMessage(content=response.content))
        state["current_stage"] = "complete"
        return state

def generate_podcast(topic: str) -> Dict[str, Any]:
    """Generate a complete podcast script from a topic."""
    generator = PodcastGenerator()
    graph = generator.create_graph()
    
    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=f"Create a podcast about: {topic}")],
        "topic": topic,
        "script": None,
        "current_stage": "start"
    }
    
    # Run the graph
    final_state = graph.invoke(initial_state)
    
    return {
        "topic": topic,
        "script": final_state["script"],
        "conversation_history": [m.content for m in final_state["messages"]]
    }

# Example usage
if __name__ == "__main__":
    topic = "Knowledge Distillation in Machine Learning"
    result = generate_podcast(topic)
    
    print("\nFinal Script:")
    print("-" * 80)
    print(result["script"])
    
    # Save the output
    with open("podcast_script.json", "w") as f:
        json.dump(result, f, indent=2)
