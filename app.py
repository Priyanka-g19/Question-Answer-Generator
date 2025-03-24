import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables and initialize the language model
def initialize_llm_with_env():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")  # Add model to environment variables

    if not api_key or not model:
        raise ValueError("API key and model must be set in the environment variables")

    return ChatGoogleGenerativeAI(google_api_key=api_key, model=model)

llm = initialize_llm_with_env()

# Initialize FastAPI app
app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for request bodies
class CombinedRequest(BaseModel):
    subject: str = None
    topic: str = None
    subtopic: str = None
    prompt: str = None

# Route for combined QA and general prompt
@app.post("/generate_response")
async def generate_response_endpoint(request: CombinedRequest):
    try:
        if request.subject and request.topic and request.subtopic:
            response_content = generate_qa(request.subject, request.topic, request.subtopic, llm)
        elif request.prompt:
            response_content = generate_general_prompt(request.prompt, llm)
        else:
            raise HTTPException(status_code=400, detail="Invalid request parameters")
        return {"response": response_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route for serving the main page
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Route to render response.html with query parameter
@app.get("/response")
async def render_response(request: Request, response: str = None):
    return templates.TemplateResponse("response.html", {"request": request, "response": response})

# Function for generating QA
def generate_qa(subject, topic, subtopic, llm):
    brief_qa_prompt = """You are a Question-answer generator assistant.
    Your role is to provide the question on given subject: {subject}, topic: {topic} and subtopic: {subtopic}.
    Also provide the solution for the question."""

    formatted_prompt = brief_qa_prompt.format(subject=subject, topic=topic, subtopic=subtopic)
    response = llm.invoke(formatted_prompt)
    return response.content

# Function for generating response to a general prompt
def generate_general_prompt(prompt, llm):
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
