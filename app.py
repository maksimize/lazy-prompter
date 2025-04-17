from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from ai import Ai



app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key"  # In production, use a secure secret key
)

templates = Jinja2Templates(directory="templates")
templates.env.globals['enumerate'] = enumerate
ai = Ai()

class Question(BaseModel):
    question: str
    answer: str
class Prompt(BaseModel):
    user_prompt: str
    questions: Optional[List[Question]] = []
    
    def get_prompt(self):
        result = self.user_prompt
        if len(self.questions) > 0:
            result = f" {result} and here is my answers to these quesions\n"
            for q in self.questions:
                result = f"{result} {q.question}: {q.answer}\n"        
        return result
    
# Define routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.j2", {"request": request})

@app.post("/submit-prompt")
async def submit_prompt(request: Request, user_prompt: str = Form(...)):
    prompt_model = Prompt(user_prompt=user_prompt)
    request.session["prompt_model"] = prompt_model.model_dump_json()
    return RedirectResponse(url="/next", status_code=303)

@app.get("/next", response_class=HTMLResponse)
async def next_page(request: Request):
    if "prompt_model" not in request.session:
        return RedirectResponse(url="/", status_code=303)
    
    prompt_model = Prompt.model_validate_json(request.session['prompt_model'])
    questions = ai.get_questions(prompt_model.user_prompt)
    request.session['questions'] = questions
    
    return templates.TemplateResponse(
        "questions.j2", 
        {"request": request, "questions": questions,
         "prompt_model": prompt_model}
    )

@app.post("/submit-answers/{more}")
async def submit_answers(request: Request, more: str):
    form_data = await request.form()
    questions = request.session['questions']
    prompt_model = Prompt.model_validate_json(request.session['prompt_model'])
    for k, q in enumerate(questions):
        q = Question(question=q["question"], answer=form_data[f"q{k}"])
        prompt_model.questions.append(q)
    request.session["prompt_model"] = prompt_model.model_dump_json()
    if more == "more":
        return RedirectResponse(url="/next", status_code=303)
        
    return RedirectResponse(url="/result", status_code=303)

@app.get("/result", response_class=HTMLResponse)
async def result(request: Request):
    if "user_prompt" not in request.session or "answers" not in request.session:
        return RedirectResponse(url="/", status_code=303)

    prompt_model = Prompt.model_validate_json(request.session['prompt_model'])
    answer = ai.get_answer(prompt_model.get_prompt())
    return templates.TemplateResponse(
        "result.j2", 
        {
            "request": request, 
            "prompt_model": prompt_model,
            "answer": answer
        }
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)