from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

# Define the shared memory state between nodes
class GraphState(TypedDict):
    messages: List
    needs_more_info: bool

# LLM initialization
llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key="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")

# === NODES ===

def ask_question(state: GraphState) -> GraphState:
    question = input("User question: ")  # simulate user input
    state["messages"].append(HumanMessage(content=question))
    state["messages"].append(SystemMessage("please make sure to contain the exact phrase 'insufficient info' in your answer if you are unsure you cannot provide a suffiecent answer. This is for technical reasons."))
    return state

def agent_thinks(state: GraphState) -> GraphState:
    response = llm.invoke(state["messages"])
    state["messages"].append(response)

    # Decide if the answer is confident or not
    if "insufficient info" in response.content:
        state["needs_more_info"] = True
    else:
        state["needs_more_info"] = False
    return state

def ask_for_more_info(state: GraphState) -> GraphState:
    print("Agent: I need more info.")
    extra = input("Provide more info: ")
    state["messages"].append(HumanMessage(content=extra))
    return state

def final_answer(state: GraphState) -> GraphState:
    print("Final Answer:", state["messages"][-1].content)
    return state

# === GRAPH ===

workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("ask_question", ask_question)
workflow.add_node("agent_thinks", agent_thinks)
workflow.add_node("ask_for_more_info", ask_for_more_info)
workflow.add_node("final_answer", final_answer)

# Define flow
workflow.set_entry_point("ask_question")
workflow.add_edge("ask_question", "agent_thinks")

# Conditional branching based on agent's confidence
workflow.add_conditional_edges(
    "agent_thinks",
    lambda state: "ask_for_more_info" if state["needs_more_info"] else "final_answer"
)

workflow.add_edge("ask_for_more_info", "agent_thinks")
workflow.add_edge("final_answer", END)

# Compile and run
graph = workflow.compile()

# Initialize state and execute
initial_state = {
    "messages": [],
    "needs_more_info": False
}
graph.invoke(initial_state)