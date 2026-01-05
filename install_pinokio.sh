#!/bin/bash
set -e

echo "=== Installing system dependencies for Choral LLM Workbench ==="

# Update package list
sudo apt update

# Python and dev tools
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip git

# SDL2 libraries for pygame audio
sudo apt install -y libsdl2-2.0-0 libsdl2-mixer-2.0-0

# FluidSynth for MIDI -> WAV rendering
sudo apt install -y fluidsynth

# Create virtual environment
echo "=== Creating virtual environment ==="
python3.12 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "=== Installing Python packages ==="
pip install -r requirements.txt

# Download default SoundFont
echo "=== Downloading default SoundFont ==="
mkdir -p ~/.fluidsynth
wget https://member.keymusician.com/Member/FluidR3_GM/FluidR3_GM.sf2 -O ~/.fluidsynth/default_sound_font.sf2

echo "=== Installation complete ==="
echo "Activate virtual environment with: source .venv/bin/activate"
