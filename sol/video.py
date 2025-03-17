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

from modules.SolVideo import SolVideoConfig
from modules.Config import arg_parser
from modules.VideoPlayer import ocv
from modules.VideoPlayer import ppl

# Parse the runtime arguments to decide 'who we are'
arg = arg_parser()

# FastApi startup and shutdown procedures
@asynccontextmanager
async def runtime_lifespan(app: FastAPI):
    """ Lifespan of the FastAPI application """
    print('Initializing SoL Video Runner...')
    app.c = SolVideoConfig(audio=arg.audio, video=arg.video, room=int(arg.room), master=bool(arg.master))

    # if platform.system() != 'Darwin':
    #     app.c.blue.light.blink(background=True, on_time=0.1, off_time=0.3)
    #     app.c.green.light.on()

    # app.audio = AudioLibrary(entropy=app.c.entropy_audio)
    app.mount("/static", StaticFiles(directory=app.c.fastapi_static), name="static")
    app.templates = Jinja2Templates(directory=app.c.fastapi_templates)

    # OpenCV Player
    asyncio.create_task(ocv(app.c, player_name='Tate'))

    # # Choose player for the runtime
    # if app.c.entropy:
    #     # OpenCV Player
    #     asyncio.create_task(ocv(app.c))
    # elif app.c.tate:
    #     # Pyglet Player
    #     asyncio.create_task(ppl(app.c))

    asyncio.create_task(actions())

    # if platform.system() != 'Darwin':
    #     app.c.blue.light.blink(background=True, on_time=1, off_time=1)
    #     app.c.green.light.off()

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
        # if app.audio.p is not None:
        #     try:
        #         print(app.audio.p.time)
        #     except Exception as e:
        #         print(e)
        await asyncio.sleep(0.05)

async def read_sensors():
    print('Initiating Read Sensors Background Loop...')
    while True:
        # try:
        #     if app.c.button.red.is_active:
        #         app.c.green.light.on()
        #     else:
        #         if app.c.green.light.is_active is True:
        #             app.c.green.light.off()
        # except Exception:
        #     pass
        await asyncio.sleep(0.1)


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

    api_port = 9000 + int(arg.room)
    uvicorn.run("video:app", host="0.0.0.0", port=api_port, reload=False)
