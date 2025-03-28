#!/bin/bash

# xrandr --newmode "1920x1080_60.00" 173.00 1920 2048 2248 2576 1080 1083 1088 1120 -hsync +vsync
xrandr --newmode "640x480_59.9" 25.18  640 656 752 800  480 490 492 525 -hsync -vsync
xrandr --addmode HDMI-2 "640x480_59.9"
xrandr -s 640x480_59.9