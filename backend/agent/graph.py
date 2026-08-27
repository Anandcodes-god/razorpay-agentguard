from langgraph.graph import StateGraph, END
from backend.agent.state import AgentGuardState
from backend.agent.nodes import (
    verify_agent_node, check_intent_node, check_signals_node,
    llm_reasoning_node, policy_gate_node, agent_valid_router
)

def create_agent_graph():
    """Create and compile the AgentGuard investigation graph."""
    graph = StateGraph(AgentGuardState)
    
    # Add nodes
    graph.add_node('verify_agent', verify_agent_node)
    graph.add_node('check_intent', check_intent_node)
    graph.add_node('check_signals', check_signals_node)
    graph.add_node('llm_reasoning', llm_reasoning_node)
    graph.add_node('policy_gate', policy_gate_node)
    
    # Add edges
    graph.set_entry_point('verify_agent')
    graph.add_conditional_edges('verify_agent', agent_valid_router, {
        'valid': 'check_intent',
        'invalid': 'policy_gate'
    })
    graph.add_edge('check_intent', 'check_signals')
    graph.add_edge('check_signals', 'llm_reasoning')
    graph.add_edge('llm_reasoning', 'policy_gate')
    graph.add_edge('policy_gate', END)
    
    return graph.compile()
