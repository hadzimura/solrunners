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

        self.catalog = dict()
        self.media = list()
        self.tracks_info = tracks_info

        # Metadata of currently playing
        self.metadata = dict()
        self.heads = dict()
        self.entropy = {'music': {'left': dict(), 'right': dict()}, 'vocals': {'left': dict(), 'right': dict()}}

        # This is where the voice frames are
        self.timeline = dict()

        # Player storage
        self.p = None

        # Load audio tracks using tracks metadata
        for album in self.tracks_info:
            if album == 'heads':
                self.load_heads(audio_path / Path(album))
            elif album == 'entropy':
                self.load_entropy(audio_path / Path(album))
            else:
                self.load_tracks(album, audio_path / Path(album))
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
            for track, data in tracks.items():
                if data['id'] == track_id:
                    return self.catalog[album][track]

    def load_heads(self, library_path):

        """
        Structure:
        self.heads -> sample (info) -> version (roman-1) -> left/right (info)
        """

        print("Importing 'heads' audio files: '{}'".format(library_path))
        heads_meta = self.tracks_info['heads']

        # Iterate over WAV samples and enrich
        for channel in ['left', 'right']:
            for filepath in sorted(glob('{}/{}/*.wav'.format(library_path, channel))):

                file_name = filepath.split('/')[-1].split('.')[0]
                sample, actor, take = file_name.split('-')

                version = '{}-{}'.format(actor, take)

                if sample not in self.heads:
                    self.heads[sample] = self.tracks_info['heads'][sample]
                    self.heads[sample]['v'] = dict()

                if version not in self.heads[sample]['v']:
                    self.heads[sample]['v'][version] = dict()

                print('Loading file: {}'.format(filepath))

                self.media.append(pyglet.media.StaticSource(pyglet.media.load(filepath, streaming=False)))

                self.heads[sample]['v'][version][channel] = dict()

                self.heads[sample]['v'][version][channel]['id'] = len(self.media) - 1
                self.heads[sample]['v'][version][channel]['duration'] = self.media[-1].duration
                self.heads[sample]['v'][version][channel]['filename'] = filepath
        # pprint(self.metadata['heads'], indent=2)


    def load_entropy(self, library_path):

        print("Importing 'entropy' audio files: '{}'".format(library_path))

        for file_name in sorted(self.tracks_info['entropy']):

            info = self.tracks_info['entropy'][file_name]
            file_path = '{}/{}'.format(library_path, Path('{}.wav'.format(file_name)))

            print('Loading file: {}'.format(file_path))
            self.media.append(pyglet.media.StaticSource(pyglet.media.load(file_path, streaming=False)))
            record = {
                'id':  len(self.media) - 1,
                'duration':  self.media[-1].duration,
                'filename': file_path
            }

            self.entropy[info['name']][info['channel']] = record
            # if 'voice.left' in file:
            #     print('Analyzing file: {}'.format(file))
            #     self.timeline = self.analyze(file)
        # pprint(self.entropy, indent=2)

    def load_tracks(self, album, library_path):

        print("Importing '{}' audio files: '{}'".format(album, library_path))
        self.catalog[album] = dict()

        for file_name in sorted(self.tracks_info[album]):

            info = self.tracks_info[album][file_name]
            file_path = '{}/{}'.format(library_path, Path('{}.wav'.format(file_name)))

            if file_name not in self.catalog[album]:
                self.catalog[album][file_name] = dict()
            print('Loading file: {}'.format(file_path))

            self.media.append(pyglet.media.StaticSource(pyglet.media.load(file_path, streaming=False)))
            self.catalog[album][file_name] = info
            self.catalog[album][file_name]['id'] = len(self.media) - 1
            self.catalog[album][file_name]['duration'] = self.media[-1].duration
            self.catalog[album][file_name]['filename'] = file_path

            # if 'voice.left' in file:
            #     print('Analyzing file: {}'.format(file))
            #     self.timeline = self.analyze(file)
        # pprint(self.catalog, indent=2)

    def prepare_audio(self, album, library_path):

        result = dict()
        pprint(result, indent=2)

    def stop_audio(self):
        self.p.pause()

    def play_audio(self, track_id, overlay=False):

        """ Play selected track and channel through destined stereo position """

        if self.p is not None and overlay is False:
            print('Stopping current stream')
            self.p.pause()

        # self.metadata = self._lookup(track_id)
        self.p = self.media[track_id].play()
        # print('Playing track ID {}: {} ({})'.format(self.metadata['id'],
        #                                                   self.metadata['name'],
        #                                                   str(self.metadata['tags'])))

    # def play_audio(self, track_id, continuous=True):
    #
    #     """ Play selected track and channel through destined stereo position """
    #
    #     continuity_timer = 0
    #     if self.p is not None:
    #         print('Stopping current stream')
    #         if continuous is True:
    #             continuity_timer = self.p.time
    #         self.p.pause()
    #     self.metadata = self._lookup(track_id)
    #     self.p = self.media[track_id].play()
    #     if continuous is True:
    #         self.p.seek(continuity_timer)
    #     print('Playing track ID {}: {} ({})'.format(self.metadata['id'],
    #                                                       self.metadata['name'],
    #                                                       str(self.metadata['tags'])))

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

    @staticmethod
    def play_sound(self):
        sound = pyglet.media.synthesis.Sine(0.1, frequency=440, sample_rate=44800)
        sound.play()