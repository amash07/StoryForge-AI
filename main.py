"""
Main Orchestration Pipeline for Automated Multimedia Generation.
Title: "AI-Generated Journey of a Student"

Executes the 8-step programmatic pipeline:
  STEP 1: Load configuration.
  STEP 2: Load the 5 prompts.
  STEP 3: Generate 5 images using the GenAI API.
  STEP 4: Save all images.
  STEP 5: Generate the TTS narration.
  STEP 6: Create the slideshow video.
  STEP 7: Add the narration.
  STEP 8: Export the final MP4.
"""

import sys
import argparse
from pathlib import Path

from config import (
    ensure_directories,
    validate_hf_token,
    IMAGES_DIR,
    AUDIO_DIR,
    VIDEO_DIR,
    NARRATION_FILE,
    FINAL_VIDEO_FILE,
    HF_MODEL
)
from prompts import IMAGE_PROMPTS, NARRATION_SCRIPTS
from image_generator import generate_all_images
from tts_generator import generate_narration
from video_creator import create_slideshow_video


def run_pipeline(skip_image_generation: bool = False):
    """
    Executes the entire automated multimedia pipeline from end to end.
    """
    print("\n" + "#" * 70)
    print(" AUTOMATED MULTIMEDIA PIPELINE WITH GENAI APIS")
    print(" Project: 'AI-Generated Journey of a Student' (5 Scenes)")
    print("#" * 70 + "\n")

    # =========================================================================
    # STEP 1: Load configuration and ensure directory structure
    # =========================================================================
    print("[STEP 1/8] Loading configuration and initializing directories...")
    ensure_directories()
    print(f"  Target Image Directory : {IMAGES_DIR}")
    print(f"  Target Audio Directory : {AUDIO_DIR}")
    print(f"  Target Video Directory : {VIDEO_DIR}")
    print(f"  Active Model           : {HF_MODEL}")

    # =========================================================================
    # STEP 2: Load the 5 prompts
    # =========================================================================
    print("\n[STEP 2/8] Loading the 5 prompt variations and story narration...")
    prompts = IMAGE_PROMPTS
    if len(prompts) != 5:
        raise ValueError(f"Expected exactly 5 prompts, found {len(prompts)}.")
    print(f"  Loaded {len(prompts)} scene prompts successfully.")

    # =========================================================================
    # STEPS 3 & 4: Generate 5 images using GenAI API and save them
    # =========================================================================
    expected_image_paths = [IMAGES_DIR / f"scene_{i:02d}.png" for i in range(1, 6)]

    if skip_image_generation:
        print("\n[STEP 3 & 4/8] Skipping image generation flag detected (--skip-images).")
        print("  Checking for existing scene images...")
        missing_images = [p for p in expected_image_paths if not p.exists()]
        if missing_images:
            raise FileNotFoundError(
                f"Cannot skip image generation because the following images are missing:\n"
                + "\n".join(f"  - {p}" for p in missing_images)
            )
        image_paths = expected_image_paths
        print("  Using existing 5 scene images from disk.")
    else:
        print("\n[STEP 3 & 4/8] Generating and saving 5 scene images via Hugging Face API...")
        # Validate that HF_TOKEN is configured before firing API calls
        validate_hf_token(raise_error=True)
        image_paths = generate_all_images(prompts=prompts, output_dir=IMAGES_DIR)

    # =========================================================================
    # STEP 5: Generate the TTS narration voiceover
    # =========================================================================
    print("\n[STEP 5/8] Generating Text-to-Speech narration...")
    audio_path = generate_narration(output_path=NARRATION_FILE)

    # =========================================================================
    # STEPS 6, 7 & 8: Assemble slideshow, attach narration, and export MP4
    # =========================================================================
    print("\n[STEP 6, 7 & 8/8] Assembling video, synchronizing voiceover, and exporting MP4...")
    final_video_path = create_slideshow_video(
        image_paths=image_paths,
        audio_path=audio_path,
        output_video_path=FINAL_VIDEO_FILE
    )

    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"Final MP4 Video Available at:\n  --> {final_video_path.resolve()}\n")
    return final_video_path


def main():
    parser = argparse.ArgumentParser(
        description="Automated Multimedia Pipeline with GenAI APIs - AI Student Journey"
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip API image generation if scenes 01-05 already exist on disk."
    )
    args = parser.parse_args()

    try:
        run_pipeline(skip_image_generation=args.skip_images)
    except Exception as e:
        sys.stdout.flush()
        print("\n" + "!" * 70, file=sys.stderr)
        print("PIPELINE EXECUTION FAILED WITH ERROR:", file=sys.stderr)
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        print("!" * 70, file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
