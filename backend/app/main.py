from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.core.config import settings
from app.database import Base, engine
from app.routers import auth, users, chat, memory, planner, summary, audio


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.API_V1_PREFIX

app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(chat.router, prefix=api_prefix)
app.include_router(memory.router, prefix=api_prefix)
app.include_router(planner.router, prefix=api_prefix)
app.include_router(summary.router, prefix=api_prefix)

# Web UI
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    return {"message": "Aziz AI Full backend ishlayapti!"}


@app.get("/ui")
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
