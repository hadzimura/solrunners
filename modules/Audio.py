#!/usr/bin/env python3
# coding=utf-8
# Springs of Life (2025)# rkucera@gmail.com

from glob import glob
from os.path import isfile
from pathlib import Path
from pprint import pprint
import pyglet
from random import random, choice
from scipy.io import wavfile
import time

# Run pyglet in headless mode
pyglet.options['headless'] = True
# pyglet.options['headless_device'] = 0
# pyglet.options['audio'] = 'pulse'


class AudioLibrary(object):

    # For analysis purposes
    frame_summary = {'on': int(), 'off': int()}

    # Scripting of the playtime
    script = {
        5.0: True,
        7.0: False,
        10.0: True,
        15.0: False
    }

    def __init__(self, audio_path=None, tracks_info=None):

        #
        self.catalog = dict()
        self.media = list()

        # Metadata of currently playing
        self.metadata = dict()

        # This is where the voice frames are
        self.timeline = dict()

        # Player storage
        self.p = None
        self.load_media('entropy', audio_path / Path('entropy'), None)
        self.load_media('nasa', audio_path / Path('nasa/waves'), tracks_info)
        self.swap = False

    def analyze(self, wav_file, video_fps=23.98, sampling=44100, generate=False):

        """ Convert audio playtime to seconds and frames,
         with voice on/off states
         Resulting array looks like:
         "0.041700680272108846;0"
         - first number: time
         - second number: state (boolean)
         Array index itself matches the video-frame inferred from the 'video_fps' parameter
         """

        # Look for already analyzed dataset for WAV
        existing_source = wav_file.replace('.wav', '.log')
        frames_timeline = list()
        seconds_timeline = dict()
        time_sample = 1

        # If the analysis has been done before, read the results
        if generate is False:
            if isfile(existing_source):
                print("Found existing analyse file: '{}'".format(existing_source))
                try:
                    with open(existing_source, 'r') as anal_file:
                        for a_data in anal_file.readlines():
                            aline = a_data.strip().split(';')
                            frames_timeline.append(bool(int(aline[1])))
                            seconds_timeline[round(float(aline[0]), time_sample)] = bool(int(aline[1]))
                        print('Imported the analyse file')
                        # return frames_timeline, seconds_timeline
                        return seconds_timeline

                except Exception as anal_read_error:
                    print("Reading the analyse file failed: '{}'".format(existing_source))
                    print(anal_read_error)
                    print('Trying to re-analyze...')
            else:
                print("Analyze file not found: '{}'".format(existing_source))

        # Read WAV file for analysis
        try:
            rate, data = wavfile.read(wav_file)
            print("Wave file for analysis imported: '{}'".format(existing_source))
        except KeyError as error:
            print("Failed to read audio file for analysis: '{}'".format(existing_source))
            print(error)
            return None

        # TODO: this is maybe ugly AF
        audio_sample = 0
        video_frame = 0
        frame_window = 0
        frame_cue = int(rate / video_fps)
        playline = list()
        frame_summary = self.frame_summary.copy()

        for current_sample in data:

            # Current state
            audio_sample += 1
            frame_window += 1

            # Track video frames
            if frame_window == frame_cue:
                video_frame += 1
                frame_window = 0

            # Is there a sound?
            if abs(current_sample[0]) + abs(current_sample[1]) != 0:
                current_state = True
                frame_summary['on'] += 1
            else:
                current_state = False
                frame_summary['off'] += 1

            # Finished processing of the previous frame, show status
            if frame_window == 0:
                state = frame_summary['on'] - frame_summary['off']
                if state > 0:
                    playline.append([float(audio_sample / sampling), 1])
                else:
                    playline.append([float(audio_sample / sampling), 0])
                frame_summary = self.frame_summary.copy()

        print('Finished the analyse')
        print("Saving analyse log as: '{}'".format(existing_source))
        with open(existing_source, 'w') as anal_file:
            for anal_line in playline:
                anal_file.write("{};{}\n".format(str(anal_line[0]), str(anal_line[1])))
                # frames_timeline.append(bool(int(anal_line[1])))
                seconds_timeline[round(float(anal_line[0]), time_sample)] = bool(int(anal_line[1]))

        print('Successfully saved analyse file')
        return seconds_timeline

    def _lookup(self, track_id):

        # self.catalog[album][track][channel]['id']
        for album, tracks in self.catalog.items():
            for track, channels in tracks.items():
                pprint(channels)
                for channel_name, channel_data in channels.items():
                    if channel_data['id'] == track_id:
                        return self.catalog[album][track][channel_name]

    def load_media(self, album, library_path, tracks_info):

        print("Importing '{}' audio files: '{}'".format(album, library_path))

        if album == 'entropy':

            self.catalog[album] = dict()

            for file in glob('{}/*.wav'.format(library_path)):

                track = file.split('/')[-1].split('.')[0]
                channel = file.split('/')[-1].split('.')[1]

                if track not in self.catalog[album]:
                    self.catalog[album][track] = dict()
                if channel not in self.catalog[album][track]:
                    self.catalog[album][track][channel] = dict()

                print('Loading file: {}'.format(file))
                print('Importing track: {} ({})'.format(track, channel))

                self.media.append(pyglet.media.StaticSource(pyglet.media.load(file, streaming=False)))
                self.catalog[album][track][channel]['id'] = len(self.media) - 1
                self.catalog[album][track][channel]['duration'] = self.media[-1].duration
                self.catalog[album][track][channel]['file'] = file

                if 'voice.left' in file:
                    print('Analyzing file: {}'.format(file))
                    self.timeline = self.analyze(file)

        elif album == 'nasa':

            self.catalog[album] = dict()

            for file in sorted(tracks_info[album]):

                info = tracks_info[album][file]
                filename = '{}/{}'.format(library_path, Path('{}.wav'.format(file)))
                channel = 'stereo'
                track = 'nasa-{}'.format(file)

                if track not in self.catalog[album]:
                    self.catalog[album][track] = dict()
                if channel not in self.catalog[album][track]:
                    self.catalog[album][track][channel] = dict()

                print('Loading file: {}'.format(filename))
                print('Importing track: {} ({})'.format(track, channel))

                self.media.append(pyglet.media.StaticSource(pyglet.media.load(filename, streaming=False)))
                self.catalog[album][track][channel]['id'] = len(self.media) - 1
                self.catalog[album][track][channel]['name'] = info['name']
                self.catalog[album][track][channel]['tags'] = info['tags']
                self.catalog[album][track][channel]['duration'] = self.media[-1].duration
                self.catalog[album][track][channel]['filename'] = filename

            # pprint(self.timeline, indent=2)
            pprint(self.catalog, indent=2)
            print('Imported all audio')

    def play_audio(self, track_id, continuous=True):

        """ Play selected track and channel through destined stereo position """

        continuity_timer = 0
        if self.p is not None:
            print('Stopping current stream')
            if continuous is True:
                continuity_timer = self.p.time
            self.p.pause()
        self.metadata = self._lookup(track_id)
        self.p = self.media[track_id].play()
        if continuous is True:
            self.p.seek(continuity_timer)
        print('Playing track ID {}: {} ({})'.format(self.metadata['id'],
                                                          self.metadata['name'],
                                                          str(self.metadata['tags'])))

    def seek_stream(self, frame):
        if self.p is None:
            print('Nothing playing, seek void')
            return

        goto = int(frame)
        # if self.p.duration < goto:
        #     print('Too short, seek void')
        #     return
        previous = self.p.time
        # self.p.seek(self.p.time + 10)
        self.p.seek(goto)
        print('Playhead moved from {} to {}'.format(previous, goto))

    def tracker(self):

        current_playhead = round(float(self.p.time), 1)
        event = False
        # sol.library.play_id(tn, sol.data)
        # await asyncio.sleep(1)
        # if current_playhead in self.timeline:
        if current_playhead in self.script:
            if self.swap != self.script[current_playhead]:
                self.swap = not self.swap

                if self.metadata['channel'] == 'left':
                    self.play_stream(self.metadata['track'], 'right')
                else:
                    self.play_stream(self.metadata['track'], 'left')


            # print('match: {} = {}'.format(current_playhead, self.timeline[current_playhead]))
        # else:

            # print('NO match: {}'.format(current_playhead))

        return event
