#!/usr/bin/env bash
# © 2025 Radim Kučera (rkucera@gmail.com)

if [[ -d .solenv ]]; then
  echo -e "source .solenv/bin/activate"
else
  python3 -m venv .solenv
fi