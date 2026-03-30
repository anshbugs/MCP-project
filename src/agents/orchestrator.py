from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.config import get_llm
from src.agents.fundamental import analyze_fundamentals
from src.agents.technical import analyze_technicals
from src.agents.sentiment import analyze_sentiment

class AnalystState(TypedDict):
    """The state dictionary for the LangGraph orchestrator."""
    ticker: str
    asset_type: Optional[str]
    fundamental_data: Optional[Dict[str, Any]]
    technical_data: Optional[Dict[str, Any]]
    sentiment_data: Optional[Dict[str, Any]]
    
    fundamental_score: Optional[float]
    fundamental_summary: Optional[str]
    
    technical_score: Optional[float]
    technical_summary: Optional[str]
    
    sentiment_score: Optional[float]
    sentiment_summary: Optional[str]
    
    final_score: Optional[float]
    recommendation: Optional[str]
    final_summary: Optional[str]

class FinalDecisionOutput(BaseModel):
    final_summary: str = Field(description="A comprehensive executive summary detailing the rationale and final output.")

def aggregator_node(state: AnalystState) -> dict:
    """Calculates exactly the deterministic final score & recommendation."""
    f_score = state.get("fundamental_score", 5.0)
    t_score = state.get("technical_score", 5.0)
    s_score = state.get("sentiment_score", 5.0)
    
    final_score = (0.4 * f_score) + (0.35 * t_score) + (0.25 * s_score)
    final_score = round(final_score, 2)
    
    if final_score > 8:
        recommendation = "Strong Buy"
    elif final_score >= 6:
        recommendation = "Buy"
    elif final_score >= 4:
        recommendation = "Hold"
    else:
        recommendation = "Avoid"
        
    return {
        "final_score": final_score,
        "recommendation": recommendation
    }

def final_generator_node(state: AnalystState) -> dict:
    """Generates the PM-level qualitative report summarizing the decision."""
    llm = get_llm().with_structured_output(FinalDecisionOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Master Orchestrator (PM) of an AI equity research desk. Provide a PM-level final comprehensive decision snippet. Ensure it reads like a crisp decision intelligence report. Do not change the calculated recommendation or final score. Just write the 'why'."),
        ("user", "Ticker: {ticker}\nFundamental: Score {f_score}. {f_summary}\nTechnical: Score {t_score}. {t_summary}\nSentiment: Score {s_score}. {s_summary}\nCalculated Final Score: {final_score}/10\nCalculated Recommendation: {rec}")
    ])
    
    chain = prompt | llm
    try:
        response = chain.invoke({
            "ticker": state["ticker"],
            "f_score": state.get("fundamental_score", 0),
            "f_summary": state.get("fundamental_summary", ""),
            "t_score": state.get("technical_score", 0),
            "t_summary": state.get("technical_summary", ""),
            "s_score": state.get("sentiment_score", 0),
            "s_summary": state.get("sentiment_summary", ""),
            "final_score": state.get("final_score", 0),
            "rec": state.get("recommendation", "")
        })
        return {"final_summary": response.final_summary}
    except Exception as e:
        return {"final_summary": f"Final report generation failed: {str(e)}"}

def build_analyst_graph():
    """Builds and wires the parallel Multi-Agent LangGraph."""
    builder = StateGraph(AnalystState)
    
    # 1. Add all nodes
    builder.add_node("fundamental_node", analyze_fundamentals)
    builder.add_node("technical_node", analyze_technicals)
    builder.add_node("sentiment_node", analyze_sentiment)
    builder.add_node("aggregator_node", aggregator_node)
    builder.add_node("final_report_node", final_generator_node)
    
    # 2. Add edges mapping the flow -> Parallel fan-out
    builder.add_edge(START, "fundamental_node")
    builder.add_edge(START, "technical_node")
    builder.add_edge(START, "sentiment_node")
    
    # 3. Fan-in to the aggregator
    builder.add_edge("fundamental_node", "aggregator_node")
    builder.add_edge("technical_node", "aggregator_node")
    builder.add_edge("sentiment_node", "aggregator_node")
    
    # 4. Finish the flow
    builder.add_edge("aggregator_node", "final_report_node")
    builder.add_edge("final_report_node", END)
    
    # Optional logic: we can compile!
    graph = builder.compile()
    return graph

# Export a usable instance
analyst_graph = build_analyst_graph()
