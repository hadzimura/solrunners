#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025) / rkucera@gmail.com

import asyncio
import datetime
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import datetime as dt
from datetime import timedelta
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
        app.c.green.blink(background=True, on_time=0.1, off_time=0.3)

    app.a = AudioLibrary(audio_path=app.c.audio_path, tracks_info=app.c.tracks)
    app.mount("/static", StaticFiles(directory=app.c.fastapi_static), name="static")
    app.templates = Jinja2Templates(directory=app.c.fastapi_templates)

    # Create Asyncio Tasks
    print('Creating background asyncio tasks...')
    asyncio.create_task(read_sensors())
    asyncio.create_task(actions())
    print('Asyncio background tasks initiated')

    # Blue light means we are ready
    if platform.system() != 'Darwin':
        app.c.green.on()

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
# Runtimes
app.armed = False
app.presence = False
app.presence_delay = False
app.button_delay = dt.now()
app.next_presence = dt.now()

async def actions():

    print('Initiating Runtime Background Loop...')
    last_second = None
    tick = False
    elapsed = 0
    while True:

        current_time = dt.now()

        if last_second is None:
            last_second = current_time.second
        if current_time.second == 0 and last_second == 59:
            tick = True
            last_second = current_time.second
        elif current_time.second > last_second:
            tick = True
            last_second = current_time.second

        if tick is True:
            elapsed += 1
            print('Elapsed: {} seconds; presence: {}; presence_delay={}'.format(elapsed,
                                                                                str(app.presence),
                                                                                str(app.presence_delay)))
            tick = False

        if app.armed is not True:
            # Do nothing if App is not armed
            await asyncio.sleep(0.05)
            continue

        # if (current_time.second - app.presence.second) <

        # if app.presence is True:
        #     if app.a.p is None:
        #         print('Playing...')
        #         # app.a.play_audio(6)

        await asyncio.sleep(0.05)

async def read_sensors():

    print('Initiating Read Sensors Background Loop...')
    while True:

        # Current cycle
        current_time = dt.now()

        # Button: STANDBY / READY (jitter)
        if app.c.button.is_active:

            if current_time <= app.button_delay:
                # Button safety jitter
                # print('Button skipped? {} - {}'.format(current_time, app.button_delay))
                pass
            elif app.armed is False:
                # Arm the Sensors runtime
                app.c.green.blink(background=True, on_time=0.5, off_time=3)
                app.armed = True
                app.button_delay = current_time + timedelta(seconds=app.c.jitter_button)
                print('System activated: {}'.format(current_time))
            elif app.armed is True:
                # Disarm the Sensors Runtime
                app.c.green.off()
                print('System de-activated: {}'.format(current_time))
                # reset all the stateful data
                app.armed = False
                app.presence = False
                app.presence_fader = False
                app.presence_delay = False
                app.button_delay = current_time + timedelta(seconds=app.c.jitter_button)
                app.c.blue.off()

        # PIR presence detection
        if app.armed:

            if app.presence_delay and current_time <= app.next_presence:
                pass

            elif app.c.pir.is_active and not app.presence:

                # Keep the presence timer updated
                app.last_presence = current_time
                app.presence = True
                app.c.blue.on()
                print('Presence started')

            elif not app.c.pir.is_active and app.presence and current_time > app.last_presence + timedelta(seconds=app.c.jitter_presence):

                # Starting the Presence Fader
                app.c.blue.blink(background=True, on_time=0.3, off_time=0.3)
                app.presence_delay = True
                app.last_presence = current_time

            elif not app.c.pir.is_active and app.presence:

                print('Presence stopped')
                app.presence = False
                app.presence_fader = False
                app.presence_delay = True
                # Start timer for next presence activity
                app.next_presence = current_time + timedelta(seconds=app.c.presence_delay)
                app.c.blue.off()

        await asyncio.sleep(0.01)
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
