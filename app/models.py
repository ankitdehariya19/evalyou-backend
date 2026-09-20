from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class InterviewAnalysis(Base):
    __tablename__ = "interview_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transcript = Column(String)
    questions_asked = Column(String)
    answers_given = Column(String)
    strengths = Column(String)
    weaknesses = Column(String)
    technical_skills = Column(String)
    communication_skills = Column(String)
    overall_score = Column(Integer)
