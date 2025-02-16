#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025)# rkucera@gmail.com

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from argparse import BooleanOptionalAction
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Request
from fastapi import status
# from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from os import environ
from pathlib import Path
import platform
import uvicorn

from modules.Audio import AudioLibrary
from modules.SolAudio import SolAudioConfig as Configuration

if platform.system() != 'Darwin':
    # Sensors only make sense when running on Raspberry Pi
    from modules.Sensors import MotionSensor

# Parse the runtime arguments to decide 'who we are'
parser = ArgumentParser(description='Sol Runner',
                        epilog='Author: rkucera@gmail.com',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-r', '--room',
                    default=None,
                    dest='room',
                    help='Which room is this Runner in?')
parser.add_argument('-s', '--sol',
                    default=None,
                    dest='sol',
                    choices=['audio', 'video'],
                    help='Which kind is this Runner of?')
parser.add_argument('-m', '--master',
                    action=BooleanOptionalAction,
                    default=False,
                    dest='master',
                    help='Master node?')

arg = parser.parse_args()

# # Running Environment location
# env_var = environ
# project_root = Path(env_var['PWD'])
# fonts = Path('fonts')
# static_pages = Path('static')
# templates_pages = Path('templates')
# entropy_audio = Path('sounds/entropy')
#
# # Development-specific initializations



# FastApi startup and shutdown procedures
@asynccontextmanager
async def runtime_lifespan(app: FastAPI):
    """ Lifespan of the FastAPI application """
    print('Initializing SoL Runner...')
    app.c = Configuration(sol=str(arg.sol), room=int(arg.room), master=bool(arg.master))
    app.c.blue.light.blink(background=True, on_time=0.2, off_time=0.2)
    app.audio = AudioLibrary(entropy=app.c.entropy_audio)
    app.mount("/static", StaticFiles(directory=app.c.fastapi_static), name="static")
    app.templates = Jinja2Templates(directory=app.c.fastapi_templates)
    asyncio.create_task(read_sensors())
    asyncio.create_task(actions())
    app.c.blue.light.blink(background=True, on_time=1, off_time=1)
    print('SoL Runner lifespan events initialized')
    yield
    # Clean up
    pass

# FastAPI runtime class
app = FastAPI(lifespan=runtime_lifespan)
app.data = dict()
app.c = dict()
app.audio = dict()

async def actions():
    print('Initializing Runtime Background Loop...')
    tn = 0
    while True:
        if app.audio.p is not None:
            try:
                print(app.audio.p.time)
            except Exception as e:
                print(e)
        await asyncio.sleep(0.05)

async def read_sensors():
    print('Initiating Read Sensors Background Loop...')
    while True:
        # if app.audio.p is not None:
        #     app.data =  app.audio.p.time
        # else:
        #     app.data = 0
        await asyncio.sleep(1)

@app.get("/")
async def index(request: Request):
    """ Index page """
    return app.templates.TemplateResponse(
        "index.html", {
            "request": request,
            "playing": app.audio.metadata,
            "library": app.audio.catalog,
            "c": app.c,
            "s": app.data }
    )

@app.get('/play_audio/{track}/{channel}')
async def play_audio(request: Request, track, channel):
    """ Play audio track """
    app.audio.play_stream(track, channel)
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.get('/seek/{frame}')
async def seek_audio(request: Request, frame):
    """ Seek within the audio stream """
    app.audio.seek_stream(frame)
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":

    api_port = 8000 + int(arg.room)
    uvicorn.run("main:app", host="0.0.0.0", port=api_port, reload=False)
