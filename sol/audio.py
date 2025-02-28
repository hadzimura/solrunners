#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025) / rkucera@gmail.com

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Request
from fastapi import status
# from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import platform
import uvicorn

from modules.Audio import AudioLibrary
from modules.SolAudio import SolAudioConfig
from modules.Config import arg_parser

# Parse the runtime arguments to decide 'who we are'
arg = arg_parser()

# FastApi startup and shutdown procedures
@asynccontextmanager
async def runtime_lifespan(app: FastAPI):
    """ Lifespan of the FastAPI application """
    print('Initializing SoL Runner...')
    app.c = SolAudioConfig(audio=arg.audio, video=arg.video, room=int(arg.room), master=bool(arg.master))

    # Application startup: blue blinx
    if platform.system() != 'Darwin':
        app.c.blue.blink(background=True, on_time=0.1, off_time=0.3)

    app.a = AudioLibrary(audio_path=app.c.audio_path, tracks_info=app.c.tracks)
    app.mount("/static", StaticFiles(directory=app.c.fastapi_static), name="static")
    app.templates = Jinja2Templates(directory=app.c.fastapi_templates)

    # Create Asyncio Tasks
    print('Creating background asyncio tasks...')
    asyncio.create_task(read_sensors())
    asyncio.create_task(actions())
    print('Asyncio background tasks initiated')

    if platform.system() != 'Darwin':
        app.c.blue.off()

    print('SoL Runner lifespan events initialized')
    yield
    # Clean up
    pass

# App: FastApi
app = FastAPI(lifespan=runtime_lifespan)
# App: AudioLibrary
app.a = dict()
# App: Config
app.c = dict()
# App: Sensors
app.s = dict()

async def actions():
    print('Initiating Runtime Background Loop...')
    tn = 0
    while True:
        # if app.a.p is not None:
        #     try:
        #         print(app.a.p.time)
        #     except Exception as e:
        #         print(e)
        await asyncio.sleep(0.05)

async def read_sensors():
    print('Initiating Read Sensors Background Loop...')
    while True:
        try:
            if app.c.button.is_active:
                app.c.green.on()
            else:
                if app.c.green.is_active is True:
                    app.c.green.off()
        except Exception:
            pass

        try:
            if app.c.pir.is_active and not app.c.green.is_active:
                app.c.green.on()
            else:
                app.c.green.off()
        except Exception:
            pass

        await asyncio.sleep(0.1)
@app.get("/")
async def index(request: Request):
    """ Index page """
    return app.templates.TemplateResponse(
        "index.html", {
            "request": request,
            "playing": app.a.metadata,
            "library": app.a.catalog,
            "config": app.c.summary,
            "sensors": app.s }
    )

@app.get('/play_audio/{track_id}')
async def play_audio(request: Request, track_id):
    """ Play audio track """
    app.a.play_audio(int(track_id))
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.get('/seek/{frame}')
async def seek_audio(request: Request, frame):
    """ Seek within the audio stream """
    app.a.seek_stream(frame)
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":

    api_port = 8000 + int(arg.room)
    uvicorn.run("audio:app", host="0.0.0.0", port=api_port, reload=False)
