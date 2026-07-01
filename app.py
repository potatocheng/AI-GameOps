from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AI智能游戏运营系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from database import init_db
from routes import feedback_router, agent_router, stats_router, announcements_router

init_db()

app.include_router(feedback_router, prefix="/api/feedback")
app.include_router(agent_router, prefix="/api/agent")
app.include_router(stats_router, prefix="/api/stats")
app.include_router(announcements_router, prefix="/api/announcements")

@app.get("/")
async def root():
    return {"message": "AI智能游戏运营系统"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)