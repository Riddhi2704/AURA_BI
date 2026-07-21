import uvicorn
from app.config import Config

if __name__ == "__main__":
    print(f"Starting AI Business Intelligence backend on {Config.HOST}:{Config.PORT}...")
    uvicorn.run("app.main:app", host=Config.HOST, port=Config.PORT, reload=True)
