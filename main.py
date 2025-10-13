import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional

app = FastAPI(
    title="Lesson Plan Generator API",
    description="Generate lesson plans using AI for any topic",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LessonPlanRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="The topic for the lesson plan")
    grade_level: Optional[str] = Field(None, description="Grade level (e.g., 5th grade)")
    
class LessonPlanResponse(BaseModel):
    lesson_plan: str
    topic: str
    
def generate_lesson_plan(topic: str, grade_level: Optional[str] = None) -> str:
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise HTTPException(status_code=500, detail="HF_TOKEN environment variable is not set. Please configure your Hugging Face API token.")
    
    try:
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
        
        prompt = f"Generate a comprehensive lesson plan for {topic}"
        if grade_level:
            prompt = f"Generate a comprehensive lesson plan for {grade_level} on {topic}"
        prompt += ", include two exam questions from the generated lesson plan. Ensure you do not bold any text in your response"
        
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct:fireworks-ai",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        
        content = completion.choices[0].message.content
        if content is None:
            raise HTTPException(status_code=500, detail="Failed to generate lesson plan: No content received from AI")
        return content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson plan: {str(e)}")

@app.post("/api/generate-lesson-plan", response_model=LessonPlanResponse)
async def create_lesson_plan(request: LessonPlanRequest):
    """
    Generate a lesson plan for the given topic.
    
    - **topic**: The topic for the lesson plan (required, 1-500 characters)
    - **grade_level**: Optional grade level specification (e.g., "5th grade")
    
    Returns a structured lesson plan with exam questions.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    lesson_plan = generate_lesson_plan(request.topic.strip(), request.grade_level)
    
    return LessonPlanResponse(
        lesson_plan=lesson_plan,
        topic=request.topic.strip()
    )

@app.get("/api/docs-info")
async def api_documentation():
    """
    Get API documentation information
    """
    return {
        "title": "Lesson Plan Generator API",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/api/generate-lesson-plan",
                "method": "POST",
                "description": "Generate a lesson plan for a given topic",
                "request_body": {
                    "topic": "string (required, 1-500 chars)",
                    "grade_level": "string (optional)"
                },
                "response": {
                    "lesson_plan": "string",
                    "topic": "string"
                },
                "example_request": {
                    "topic": "fractions",
                    "grade_level": "5th grade"
                }
            }
        ],
        "interactive_docs": "/docs"
    }

@app.get("/plain-text", response_class=HTMLResponse)
async def read_root():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>Lesson Plan Generator</h1>
                <p>Frontend is being set up...</p>
            </body>
        </html>
        """

@app.get("/")
async def read_root():
    try:
        # Optional: read the file if you still want to check for it
        with open("static/index.html", "r") as f:
            message = "Lesson Plan Generator frontend is available."
    except FileNotFoundError:
        message = "Lesson Plan Generator frontend is being set up."

    return JSONResponse(
        content={
            "app_name": "Lesson Plan Generator API",
            "status": "running",
            "version": "1.0.0",
            "message": message,
            "docs_url": "/docs",
            "generate_endpoint": "/api/generate-lesson-plan"
        }
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
