from typing import Optional, List
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph

class BaseAgent:
    """Simple base agent class"""
    def __init__(self, state_class, tools=None):
        self.agent = StateGraph(state_class)
        self.tools = tools or []

    def setup(self):
        """Setup agent graph"""
        self.setup_nodes()
        self.setup_edges()
        return self.agent.compile()

    def setup_nodes(self):
        raise NotImplementedError

    def setup_edges(self):
        raise NotImplementedError
