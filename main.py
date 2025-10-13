import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional

app = FastAPI(
    title="Lesson Plan Generator API",
    description="Generate structured lesson plans using AI for any topic",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and response models
class LessonPlanRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="The topic for the lesson plan")
    grade_level: Optional[str] = Field(None, description="Grade level (e.g., 5th grade)")


def generate_lesson_plan(topic: str, grade_level: Optional[str] = None) -> str:
    """Generates a raw lesson plan string using the Hugging Face Llama model."""
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
        prompt += ", include two exam questions and their answers. Do not use bold text in your response."

        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct:fireworks-ai",
            messages=[{"role": "user", "content": prompt}],
        )

        content = completion.choices[0].message.content
        if content is None:
            raise HTTPException(status_code=500, detail="Failed to generate lesson plan: No content received from AI")
        return content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson plan: {str(e)}")


@app.post("/api/generate-lesson-plan")
async def create_lesson_plan(request: LessonPlanRequest):
    """
    Generate a structured lesson plan for the given topic and grade level.
    Returns data in clean JSON format.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    # Generate lesson plan text from model
    lesson_plan_text = generate_lesson_plan(request.topic.strip(), request.grade_level)

    # Convert text into structured JSON
    lines = lesson_plan_text.split('\n')
    formatted_plan = {
        "lesson_plan": {
            "title": "",
            "objectives": [],
            "materials": [],
            "activities": [],
            "exam_questions": [],
            "exam_answers": []
        },
        "topic": request.topic.strip()
    }

    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("Lesson Title:"):
            formatted_plan["lesson_plan"]["title"] = line.replace("Lesson Title:", "").strip()
        elif line.startswith("Objectives:"):
            current_section = "objectives"
        elif line.startswith("Materials:"):
            current_section = "materials"
        elif line.startswith("Lesson Plan:"):
            current_section = "activities"
        elif line.startswith("Exam Questions:"):
            current_section = "exam_questions"
        elif line.startswith("Exam Answers:"):
            current_section = "exam_answers"
        elif line and current_section:
            formatted_plan["lesson_plan"][current_section].append(line.lstrip("*- "))

    return formatted_plan


@app.get("/api/docs-info")
async def api_documentation():
    """Returns endpoint documentation info."""
    return {
        "title": "Lesson Plan Generator API",
        "version": "1.1.0",
        "endpoints": [
            {
                "path": "/api/generate-lesson-plan",
                "method": "POST",
                "description": "Generate a structured lesson plan for a given topic",
                "request_body": {
                    "topic": "string (required, 1-500 chars)",
                    "grade_level": "string (optional)"
                },
                "response": {
                    "lesson_plan": {
                        "title": "string",
                        "objectives": ["list of objectives"],
                        "materials": ["list of materials"],
                        "activities": ["list of activities"],
                        "exam_questions": ["list of questions"],
                        "exam_answers": ["list of answers"]
                    },
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


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve static index.html if available."""
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

app.mount("/static", StaticFiles(directory="static"), name="static")
