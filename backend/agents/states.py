from typing import TypedDict, Optional, Dict, List
from langchain_core.messages import AIMessage

class BaseState(TypedDict, total=False):
    messages: list[AIMessage]
    
class ResearchState(BaseState):
    """Research agent state"""
    tool_outputs: Optional[Dict[str, List[Dict]]]
    web_research: Optional[Dict]
    academic_research: Optional[Dict]
    final_report: Optional[str]