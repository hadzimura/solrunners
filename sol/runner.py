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
import io
from os.path import isfile
import platform
from pprint import pprint
import uvicorn

from ruamel.yaml import YAML

from modules.Audio import AudioLibrary
from modules.Config import Configuration
from modules.Config import arg_parser
from modules.VideoPlayer import tate_linear
from modules.VideoPlayer import heads
from modules.VideoPlayer import entropy

from pydantic import BaseModel

class Queue(BaseModel):
    play_time: datetime.datetime
    track_id: int

# Parse the runtime arguments to decide 'who we are'
arg = arg_parser()

# FastApi startup and shutdown procedures
@asynccontextmanager
async def runtime_lifespan(app: FastAPI):
    """ Lifespan of the FastAPI application """
    print('Initializing SoL Runner ...')
    app.c = Configuration(room=int(arg.room), master=bool(arg.master))

    # Application startup: blue blinx
    peripherals = True
    if platform.system() != 'Darwin' or app.c.pinout['enabled'] is False:
        peripherals = False

    if peripherals is True:
        app.c.green.blink(background=True, on_time=0.2, off_time=0.2)

    app.a = AudioLibrary(audio_path=app.c.audio_path, tracks_info=app.c.tracks)
    app.mount("/static", StaticFiles(directory=app.c.fastapi_static), name="static")
    app.templates = Jinja2Templates(directory=app.c.fastapi_templates)

    # Create Asyncio Tasks
    print('Creating background asyncio tasks...')

    # OpenCV Player
    room = int(arg.room)
    if room == 1:
        # asyncio.create_task(tate_linear(app.c, app.a))
        asyncio.create_task(tate_linear(app.c, app.a))
    elif room == 2:
        # asyncio.create_task(tate_linear(app.c, app.a))
        asyncio.create_task(tate_linear(app.c, app.a))
    elif room == 3:
        # asyncio.create_task(tate_linear(app.c, app.a))
        asyncio.create_task(entropy(app.c, app.a))
    elif room == 4:
        # asyncio.create_task(tate_linear(app.c, app.a))
        asyncio.create_task(tate_linear(app.c, app.a))
    elif room == 5:
        # asyncio.create_task(tate_linear(app.c, app.a))
        asyncio.create_task(heads(app.c, app.a))

    if peripherals is True:
        asyncio.create_task(read_sensors())

    # asyncio.create_task(actions())
    print('Asyncio background tasks initiated')

    # Blue light means we are ready
    if peripherals is True:
        app.c.green.blink(background=True, on_time=1, off_time=1)

    print('All SoL Runner lifespan events initialized')
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
app.presence = None
app.presence_counter = 0

app.presence_delay = False
app.button_delay = dt.now()
app.next_presence = dt.now()

async def actions():

    print('Initiating Runtime Background Loop...')
    last_second = None
    tick = False
    elapsed = 0
    last_queue = dict()

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
            if app.c.master is True:
                app.c.dispatcher()

            # elapsed += 1
            # print('T: {} | A: {} | P: {} ({})'.format(elapsed,
            #                                           str(app.armed),
            #                                           str(app.presence),
            #                                           str(app.presence_counter)))
            tick = False


        if app.c.audio_queue != last_queue:
            pprint(app.c.audio_queue, indent=2)



        last_queue = app.c.audio_queue

        #
        # if app.armed:
        #     if app.presence and app.c.blue.is_active is False:
        #         app.c.blue.on()
        #     elif not app.presence and app.c.blue.is_active:
        #         app.c.blue.off()
        #
        # if app.armed is not True:
        #     # Do nothing if App is not armed
        #     await asyncio.sleep(0.05)
        #     continue

        # if (current_time.second - app.presence.second) <

        # if app.presence is True:
        #     if app.a.p is None:
        #         print('Playing...')
        #         # app.a.play_audio(6)

        await asyncio.sleep(0.01)

async def read_sensors():

    print('Initiating Read Sensors Background Loop...')
    presence_ticker = dt.now()
    while True:

        # Current cycle
        current_time = dt.now()

        # Initialize the App Presence itself
        if app.presence is None:
            presence_ticker = current_time + timedelta(seconds=app.c.jitter_presence)
            app.presence = False

        # Button: STANDBY / READY (jitter)
        if app.c.button.is_active:

            if current_time <= app.button_delay:
                # Button safety jitter
                # print('Button skipped? {} - {}'.format(current_time, app.button_delay))
                pass
            elif app.armed is False:
                # Arm the Sensors runtime
                app.c.green.on()
                app.armed = True
                app.presence_counter = -150
                app.button_delay = current_time + timedelta(seconds=app.c.jitter_button)
                print('System activated: {}'.format(current_time))
            elif app.armed is True:
                # Disarm the Sensors Runtime
                app.c.green.off()
                print('System de-activated: {}'.format(current_time))
                # reset all the stateful data
                app.armed = False
                app.presence = None
                app.presence_counter = 0
                app.presence_delay = False
                app.button_delay = current_time + timedelta(seconds=app.c.jitter_button)

        if app.c.pir.is_active:
            app.presence_counter += 1

        if current_time > presence_ticker:
            if app.presence_counter > 0:
                app.presence = True
            else:
                app.presence = False
            app.presence_counter = 0
            presence_ticker = current_time + timedelta(seconds=app.c.jitter_presence)

        # PIR presence detection
        # if app.armed:
        #
        #     # PIR status
        #     if app.c.pir.is_active:
        #         app.last_presence = current_time
        #         app.c.blue.on()
        #         print('*')
        #     else:
        #         app.c.blue.off()
        #         print('-')
            #
            #
            # if app.presence_delay and current_time < app.next_presence:
            #     pass
            #
            # # elif app.presence_delay and current_time >= app.next_presence:
            # #     app.presence_delay = False
            # #     print('2')
            #
            # elif not app.c.pir.is_active and app.presence and current_time >= app.last_presence + timedelta(seconds=app.c.jitter_presence):
            #     print('*')
            #     # # Starting the Presence Fader
            #     # if not app.c.blue.is_active:
            #     #     app.c.blue.blink(background=True, on_time=0.3, off_time=0.3)
            #
            # elif not app.c.pir.is_active and app.presence:
            #
            #     print('Presence stopped')
            #     app.presence = False
            #     app.presence_delay = True
            #     # Start timer for next presence activity
            #     app.next_presence = current_time + timedelta(seconds=app.c.presence_delay)
            #     app.c.blue.off()
            #
            # elif app.c.pir.is_active and not app.presence:
            #     app.presence = True
            #     app.presence_delay = False
            #     # app.c.blue.on()
            #     print('Presence started')


        await asyncio.sleep(0.01)
@app.get("/")
async def index(request: Request):
    """ Index page """
    return app.templates.TemplateResponse(
        "index.html", {
            "request": request,
            "playing": app.a.metadata,
            "heads": app.a.heads,
            "entropy": app.a.entropy,
            "summary": app.c.summary,
            "sensors": app.s }
    )

@app.get('/aplay/{category}/{track_id}')
async def play_audio(request: Request, track_id):
    """ Play audio track """
    app.a.play_audio(int(track_id))
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post('/schedule/')
async def schedule(queue: Queue):
    """ Schedule audio track playback """
    play_time = queue.play_time
    track_id = queue.track_id
    app.c.scheduler(play_time, int(track_id))
    return pprint(app.c.audio_queue, indent=2)

@app.get('/seek/{frame}')
async def seek_audio(request: Request, frame):
    """ Seek within the audio stream """
    app.a.seek_stream(frame)
    redirect_url = request.url_for('index')
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.get('/catalog')
async def catalog(request: Request):
    """ Display all the catalog info """
    heads = dict()
    yaml = YAML()
    buffer = io.BytesIO()
    yaml.dump(app.a.heads, buffer)
    heads = buffer.getvalue().decode('utf-8')
    return app.templates.TemplateResponse(
        "catalog.html", {
            "request": request,
            "summary": app.c.summary,
            "heads": heads }
    )


if __name__ == "__main__":

    if platform.system() != "Darwin":
        print('Waiting for the SHM storage to be available...')
        storage_available = False
        while storage_available is False:
            if isfile('/storage/.ready'):
                storage_available = True
                print('Storage online, starting Runner')

    api_port = 8000 + int(arg.room)
    uvicorn.run("runner:app", host="127.0.0.1", port=api_port, reload=False)
