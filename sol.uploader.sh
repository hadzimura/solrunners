#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

set -e

scp media/video/tate/* zero@10.0.0.211:/home/zero/solrunners/media/video/tate/
scp -r media/static/ zero@10.0.0.211:/home/zero/solrunners/media/static
scp -r media/templates/ zero@10.0.0.211:/home/zero/solrunners/media/templates

scp media/audio/tate/* zero@10.0.0.211:/home/zero/solrunners/media/audio/tate/
