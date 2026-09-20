from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., max_length=72)

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class TranscriptResponse(BaseModel):
    transcript: str

class AnalyzeRequest(BaseModel):
    transcript: str

class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    transcript: str
    questions_asked: str
    answers_given: str
    strengths: str
    weaknesses: str
    technical_skills: str
    communication_skills: str
    overall_score: int

    class Config:
        from_attributes = True
