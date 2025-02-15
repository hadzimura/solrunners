#!/usr/bin/env python3
# coding=utf-8

import mido
import logging as log
from pprint import pprint


import time

class Controller(object):
    events = [
        'program_change',
        'control_change',
        'channel',
        'program',
        'time'
        'control',
        'value'
    ]

    pads_cc = [
        'control_change',
        'channel',
        'control',
        'value',
        'time'
    ]

    pads_pc = [
        'program_change',
        'channel',
        'program',
        'time'
    ]

    pads_pad = [
        'note_on',
        'note_off',
        'channel',
        'note',
        'velocity',
        'time'
    ]

    knobs = [
        'control_change',
        'channel',
        'control',
        'value',
        'time'
    ]

    def __init__(self, dsp):

        self.display = dsp
        self.m = mido
        self.port = self.m.get_input_names()[1]

        self.message_sent = time.time()
        self.last_message = str()

        self.msg_queue = list()
        self.dps_blocked = False

        self.state = {'knob': dict(), 'pad': dict()}

        log.info('Controller: {}'.format(self.m.get_input_names()))

    def run(self):

        msg = {
            'type': str(),
            'nr': int(),
            'value': int()
        }
        last_state = dict()
        with self.m.open_input(self.port) as inport:
            # https://mido.readthedocs.io/en/latest/message_types.html
            log.info('Reading MIDI events...')
            for msg in inport:

                if msg.is_cc():
                    # Control Message

                    # Volume
                    if getattr(msg, 'control'):
                        log.info('knob | {} | {}'.format(msg.control, msg.value))
                        self.state['knob'][msg.control] = msg.value
                else:
                    if getattr(msg, 'note'):
                        # print('PAD on ({}) - {}'.format(, msg.type))
                        pad = msg.note - 35
                        log.info('pad | {} | {}'.format(pad, msg.type))
                        self.state['pad'][pad] = msg.type

                if self.state != last_state:
                    pprint(self.state, indent=2)
                    last_state = self.state

    def show_lcd(self):

        # print(round(time.time() - self.message_sent, 4))
        print(round(time.time() - self.message_sent, 4), self.msg_queue)
        if round(time.time() - self.message_sent, 2) > 0.07 and len(self.msg_queue) > 0:
            self.message_sent = time.time()
            self.display.print(self.msg_queue.pop())
            self.msg_queue = list()
            self.dps_blocked = False
        elif round(time.time() - self.message_sent, 2) > 0.07 and len(self.msg_queue) == 0:
            self.display.print(self.last_message)
            self.dps_blocked = False
        else:
            print('blocked: {}'.format(round(time.time() - self.message_sent, 4)))
            self.dps_blocked = True

