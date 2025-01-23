import sys
import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
load_dotenv()

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from api.api import get_newest_episode, transcribe_episode


app = FastAPI(
    title="Podcast Transcription API",
    description="API for transcribing podcast episodes",
    version="1.0.0"
)


@app.get("/api/transcribe_episode/")
def transcribe_episode(commons: dict = Depends(transcribe_episode)):
    return commons


@app.get("/api/get_newest_episode/")
def get_newest_episode(commons: dict = Depends(get_newest_episode)):
    return commons

@app.get("/")
async def root():
    html_content = """
    <html>
        <head>
            <title></title>
        </head>
        <body>
            Check <a href="/docs">the link</a> for more details. <br>
            Copyright © 2022 <a href=""></a>. All rights reserved.
        </body>
    </html>
    """
    return HTMLResponse(html_content)


def main():
    uvicorn.run(
        "app.app:app", 
        host=os.environ.get("HOST", "127.0.0.1"),  
        port=int(os.environ.get("PORT", 8000)),  
        reload=os.environ.get("SERVER_ENV") == "debug" 
    )

if __name__ == "__main__":
    main()
