import os
from groq import Groq
from fastapi import HTTPException
from typing import TypedDict
from pydantic import BaseModel, Field

# LangChain & LangGraph imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# --- 1. Basic Groq Client for Whisper ---
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured.")
    return Groq(api_key=api_key)

def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Groq's Whisper API directly (since it's a raw audio endpoint)."""
    client = get_groq_client()
    model_name = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3")
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model=model_name,
        )
    return transcription.text


# --- 2. LangGraph & LangChain for LLM Analysis ---

# Define the expected output structure using Pydantic
class AnalysisOutput(BaseModel):
    questions_asked: str = Field(description="Summary of questions asked in the interview")
    answers_given: str = Field(description="Summary of answers given by the candidate")
    strengths: str = Field(description="Candidate's strengths")
    weaknesses: str = Field(description="Candidate's weaknesses")
    technical_skills: str = Field(description="Evaluation of technical skills")
    communication_skills: str = Field(description="Evaluation of communication skills")
    overall_score: int = Field(description="Overall integer score out of 100")

# Define the state of our LangGraph workflow
class InterviewState(TypedDict):
    transcript: str
    analysis_dict: dict

# Define the node that does the LangChain LLM processing
def analyze_node(state: InterviewState):
    # Initialize the LangChain Groq model
    api_key = os.getenv("GROQ_API_KEY")
    llm_model_name = os.getenv("GROQ_LLM_MODEL", "llama3-8b-8192")
    llm = ChatGroq(api_key=api_key, temperature=0, model_name=llm_model_name)
    
    # Bind the LLM to our Pydantic schema for strict JSON output
    structured_llm = llm.with_structured_output(AnalysisOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert technical interviewer and AI assessor. Evaluate the candidate based on the transcript."),
        ("user", "Analyze this interview transcript and evaluate the candidate.\n\nTranscript:\n{transcript}")
    ])
    
    # Create the LangChain pipeline
    chain = prompt | structured_llm
    
    # Execute the chain
    result = chain.invoke({"transcript": state["transcript"]})
    
    # Return the updated state
    return {"analysis_dict": result.model_dump()}

# Build the LangGraph
workflow = StateGraph(InterviewState)
workflow.add_node("analyze", analyze_node)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", END)

# Compile the graph into an executable application
analysis_app = workflow.compile()


def analyze_transcript(transcript: str) -> dict:
    """Analyze the transcript using the compiled LangGraph workflow."""
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured.")
        
    try:
        # Run the LangGraph
        result = analysis_app.invoke({"transcript": transcript})
        return result["analysis_dict"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangGraph analysis failed: {str(e)}")
