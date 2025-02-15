

from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
#reading the sample audio rate and the data
rate, data = wavfile.read('/Users/zero/Develop/github.com/hadzimura/projectsol/sol-audio/sounds/springsoflife/entropy-vocals-WAV.wav')
length = data.shape[0] / rate
print(f"length = {length}s")

print(rate)




new_frame = 0



timing = 0
sec = 0
playline = list()

last = bool()

# ----
sample = 0
video_frame = 0
frame_window = 0

video_fps = 23.98
frame_cue = int(rate / video_fps)

last_state = False
current_state = False

frame_summary = {'on': int(), 'off': int()}

print(frame_cue)

for a in data:

    # Current state
    sample += 1
    frame_window += 1

    # Count seconds
    if sample % rate == 0:
        sec += 1
        # print(sec, video_frame, sample)

    # Track video frames
    if frame_window == frame_cue:
        # print('f',video_frame)
        video_frame += 1
        frame_window = 0

    # Is there a sound?
    if abs(a[0]) + abs(a[1]) != 0:
        current_state = True
        frame_summary['on'] += 1
    else:
        current_state = False
        frame_summary['off'] += 1

    # Evaluation

    # Finished processing of the previous frame, show status
    if frame_window == 0:
        state = frame_summary['on'] - frame_summary['off']
        if state > 0:
            playline.append([sec, video_frame - 1, True, state, frame_summary])
        else:
            playline.append([sec, video_frame - 1, False, state, frame_summary])
        # playline.append([sec, video_frame, sample, current_state, a])
        frame_summary = {'on': int(), 'off': int()}

    # if current_state != last_state:
    #     playline.append([sec, video_frame, sample, current_state, a])

    # Save last state
    last_state = current_state

    if sec > 140:
        break

pprint(playline)
exit(0)
print(f"number of channels = {data}")
length = data.shape[0] / rate
print(f"length = {length}s")
#plotting the audio time and amplitude
time = np.linspace(0., length, data.shape[0])

print(time)
exit(0)
plt.plot(time, data, label="Audio")
plt.legend()
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.show()


44100 - 1 sec
88200 - 2 sec