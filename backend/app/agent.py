from typing import TypedDict, Annotated, List, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import operator
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    symptoms: List[str]
    reports_uploaded: bool
    diagnosis_ready: bool
    next_step: str

def consultant_node(state: AgentState):
    """Main conversation node that interacts with the patient."""
    messages = state["messages"]
    
    # System prompt to guide the consultant
    system_prompt = SystemMessage(content="""You are an AI medical consultant. 
    Your goal is to gather symptoms from the patient and guide them.
    1. Ask clear questions about their symptoms (duration, severity, etc.).
    2. If you have enough information, suggest they upload a lab report if relevant, or provide general guidance.
    3. Be empathetic and professional.
    4. DO NOT provide definitive medical diagnoses. Always advise seeing a real doctor.
    """)
    
    # Add system prompt if not present (or just prepend it for the call)
    # For simplicity, we just pass it in the invoke
    response = llm.invoke([system_prompt] + messages)
    
    return {"messages": [response]}

def symptom_checker_node(state: AgentState):
    """Analyzes the conversation to extract symptoms and decide next steps."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Simple logic: ask LLM to analyze the state
    analysis_prompt = SystemMessage(content="""Analyze the conversation. 
    Return a JSON-like string (or just a keyword) indicating the next step:
    - 'ASK_MORE': Need more info about symptoms.
    - 'REQUEST_REPORT': Symptoms suggest a lab test is needed.
    - 'ADVISE': Enough info to give advice.
    """)
    
    # This is a simplification. In a real app, we'd use structured output.
    # For now, we'll just let the consultant node handle the flow mostly, 
    # and this node just updates state metadata if needed.
    
    return {}

def router(state: AgentState) -> Literal["consultant", "__end__"]:
    # Simple router: always go back to consultant unless user says "bye"
    last_message = state["messages"][-1]
    if isinstance(last_message, HumanMessage) and "bye" in last_message.content.lower():
        return "__end__"
    return "__end__" # For now, we just do one turn per API call, so we end the graph run.

# We need a graph that persists state or we pass full history each time.
# Since we are building a REST API, we will pass the full history in the request,
# so the graph runs for one turn (User -> Agent).

workflow = StateGraph(AgentState)

workflow.add_node("consultant", consultant_node)

workflow.set_entry_point("consultant")
workflow.add_edge("consultant", END)

app = workflow.compile()
