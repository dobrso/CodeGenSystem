from langgraph.graph import StateGraph, END

from models.schemas import AgentState
from agents.architect import architect_node
from agents.router import router_node
from agents.developer import developer_node
from agents.reviewer import reviewer_node
from workflow.input import input_node
from workflow.output import output_node
from memory.memory_recall import memory_recall_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("input", input_node)
    graph.add_node("memory_recall", memory_recall_node)
    graph.add_node("architect", architect_node)
    graph.add_node("router", router_node)
    graph.add_node("developer", developer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("output", output_node)

    graph.set_entry_point("input")

    graph.add_edge("input", "memory_recall")
    graph.add_edge("memory_recall", "architect")
    graph.add_edge("architect", "router")
    graph.add_edge("router", "developer")
    graph.add_edge("developer", "reviewer")
    graph.add_edge("reviewer", "output")
    graph.add_edge("output", END)

    return graph.compile()