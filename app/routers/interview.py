from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import tempfile

from app import models, schemas
from app.database import get_db
from app.routers.auth import read_users_me
from app.services.audio import compress_audio
from app.services.ai import transcribe_audio, analyze_transcript

router = APIRouter(prefix="/interview", tags=["Interview"])

@router.post("/upload-audio", response_model=schemas.TranscriptResponse)
async def process_audio(
    file: UploadFile = File(...),
    current_user: models.User = Depends(read_users_me)
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an audio file.")
        
    temp_in_path = ""
    compressed_path = ""
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_in:
            temp_in.write(await file.read())
            temp_in_path = temp_in.name
            
        compressed_path = compress_audio(temp_in_path)
        
        transcript = transcribe_audio(compressed_path)
        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Audio was too silent or no speech was detected.")
            
        if os.path.exists(temp_in_path):
            os.remove(temp_in_path)
            temp_in_path = ""
        if os.path.exists(compressed_path):
            os.remove(compressed_path)
            compressed_path = ""

        return {"transcript": transcript}
        
    finally:
        if temp_in_path and os.path.exists(temp_in_path):
            os.remove(temp_in_path)
        if compressed_path and os.path.exists(compressed_path):
            os.remove(compressed_path)


@router.post("/analyze-transcript", response_model=schemas.AnalysisResponse)
async def analyze_text(
    request: schemas.AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(read_users_me)
):
    analysis = analyze_transcript(request.transcript)
    
    new_analysis = models.InterviewAnalysis(
        user_id=current_user.id,
        transcript=request.transcript,
        questions_asked=str(analysis.get("questions_asked", "")),
        answers_given=str(analysis.get("answers_given", "")),
        strengths=str(analysis.get("strengths", "")),
        weaknesses=str(analysis.get("weaknesses", "")),
        technical_skills=str(analysis.get("technical_skills", "")),
        communication_skills=str(analysis.get("communication_skills", "")),
        overall_score=int(analysis.get("overall_score", 0))
    )
    
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)
    
    return new_analysis
