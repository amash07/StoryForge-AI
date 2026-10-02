"""
Configuration module for the Automated Multimedia Pipeline.
Loads environment variables from .env, defines project paths, and sets defaults.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file from base directory
load_dotenv(BASE_DIR / ".env")

# Output directory structure
OUTPUTS_DIR = BASE_DIR / "outputs"
IMAGES_DIR = OUTPUTS_DIR / "images"
AUDIO_DIR = OUTPUTS_DIR / "audio"
VIDEO_DIR = OUTPUTS_DIR / "final_video"

# Media file paths
NARRATION_FILE = AUDIO_DIR / "narration.mp3"
FINAL_VIDEO_FILE = VIDEO_DIR / "student_journey.mp4"

# Hugging Face GenAI API configuration
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_MODEL = os.getenv("HF_MODEL", "black-forest-labs/FLUX.1-schnell").strip()

# List of reputable free image generation models to attempt in order
HF_MODELS_POOL = [
    HF_MODEL,
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5"
]

# Video presentation settings
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))
VIDEO_RESOLUTION = (VIDEO_WIDTH, VIDEO_HEIGHT)
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "24"))
TRANSITION_DURATION = 0.5  # Crossfade duration in seconds between slides


def ensure_directories():
    """
    Ensures that all output directories exist.
    Creates: outputs/images, outputs/audio, outputs/final_video.
    """
    for directory in [IMAGES_DIR, AUDIO_DIR, VIDEO_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def validate_hf_token(raise_error=True) -> bool:
    """
    Validates whether HF_TOKEN is configured and is not a placeholder.
    Returns True if valid, otherwise raises a descriptive ValueError or returns False.
    """
    token = os.getenv("HF_TOKEN", "").strip()
    placeholder_values = {"", "your_token_here", "your_huggingface_token_here", "your_token"}
    
    if not token or token in placeholder_values:
        err_msg = (
            "\n"
            + "=" * 70 + "\n"
            + "ERROR: Missing or unconfigured Hugging Face API Token (HF_TOKEN)!\n"
            + "=" * 70 + "\n"
            + "To use the automated GenAI pipeline, you need a free Hugging Face token:\n"
            + "  1. Go to https://huggingface.co/settings/tokens\n"
            + "  2. Click 'Create new token' (Read access is sufficient)\n"
            + "  3. Open the '.env' file in your project folder\n"
            + "  4. Set HF_TOKEN=hf_your_actual_token_here\n"
            + "  5. Save and re-run python main.py\n"
            + "=" * 70
        )
        if raise_error:
            raise ValueError(err_msg)
        return False
    return True
