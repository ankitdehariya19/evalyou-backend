from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, interview

# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(title="FastAPI Auth Backend")

# Add CORS middleware to allow frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for local development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router)
app.include_router(interview.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend! Visit /docs for the API documentation."}
