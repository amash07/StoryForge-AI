"""
Video Creation Module using MoviePy.
Assembles generated images into a synchronized slideshow video with TTS voiceover narration.
"""

from pathlib import Path
from PIL import Image, ImageOps
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    VIDEO_FPS,
    NARRATION_FILE,
    FINAL_VIDEO_FILE,
    ensure_directories
)


def _prepare_image_for_video(img_path: Path, target_size=(VIDEO_WIDTH, VIDEO_HEIGHT)) -> Path:
    """
    Ensures the image is consistently scaled and cropped to 1280x720 (16:9)
    using high-quality Lanczos resampling.
    """
    img_path = Path(img_path)
    with Image.open(img_path) as img:
        img = img.convert("RGB")
        # Center-crop and fit to exact target dimensions
        fitted_img = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS)
        # Save back to ensure uniform dimensions
        fitted_img.save(img_path, "PNG")
    return img_path


def _set_clip_duration(clip, duration):
    """
    Sets clip duration supporting both MoviePy 2.x (with_duration) and 1.x (set_duration).
    """
    if hasattr(clip, "with_duration"):
        return clip.with_duration(duration)
    elif hasattr(clip, "set_duration"):
        return clip.set_duration(duration)
    clip.duration = duration
    return clip


def _set_clip_audio(clip, audio):
    """
    Attaches audio supporting both MoviePy 2.x (with_audio) and 1.x (set_audio).
    """
    if hasattr(clip, "with_audio"):
        return clip.with_audio(audio)
    elif hasattr(clip, "set_audio"):
        return clip.set_audio(audio)
    clip.audio = audio
    return clip


def create_slideshow_video(
    image_paths: list,
    audio_path: Path = NARRATION_FILE,
    output_video_path: Path = FINAL_VIDEO_FILE
) -> Path:
    """
    Loads images, resizes them to 1280x720, calculates slide durations matching
    the audio narration length, attaches audio, and exports the final MP4 video.
    
    Args:
        image_paths: List of file paths to the 5 scene images.
        audio_path: Path to the narration MP3 file.
        output_video_path: Destination path for the final MP4 file.
        
    Returns:
        Path: Path to the exported MP4 video.
    """
    ensure_directories()
    output_video_path = Path(output_video_path)
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path = Path(audio_path)

    # 1. Validation
    if not image_paths:
        raise ValueError("No images provided for video creation.")

    for p in image_paths:
        p = Path(p)
        if not p.exists():
            raise FileNotFoundError(f"Missing required image file: {p}")

    if not audio_path.exists():
        raise FileNotFoundError(f"Missing narration audio file: {audio_path}")

    print("\n" + "=" * 60)
    print("Creating slideshow...")
    print("=" * 60)

    # 2. Inspect audio duration
    audio_clip = AudioFileClip(str(audio_path))
    total_audio_duration = audio_clip.duration
    print(f"Loaded voiceover audio. Duration: {total_audio_duration:.2f} seconds.")

    # 3. Calculate slide duration
    # Distribute the audio duration evenly across the 5 images, plus a small 0.8s tail
    # to let the viewer absorb the final scene before the video closes.
    num_scenes = len(image_paths)
    tail_buffer = 0.8
    total_video_duration = total_audio_duration + tail_buffer
    per_slide_duration = total_video_duration / num_scenes
    print(f"Calculated per-slide duration: {per_slide_duration:.2f}s for {num_scenes} scenes.")

    # 4. Process images and build ImageClips
    clips = []
    try:
        for idx, img_path in enumerate(image_paths, start=1):
            print(f"  Formatting scene {idx}/{num_scenes}: {img_path.name} -> {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
            prepared_path = _prepare_image_for_video(img_path, (VIDEO_WIDTH, VIDEO_HEIGHT))
            clip = ImageClip(str(prepared_path))
            clip = _set_clip_duration(clip, per_slide_duration)
            clips.append(clip)

        # 5. Concatenate video clips
        print("Concatenating scenes into video stream...")
        video = concatenate_videoclips(clips, method="compose")

        # 6. Add voiceover
        print("\n" + "=" * 60)
        print("Adding voiceover...")
        print("=" * 60)
        video = _set_clip_audio(video, audio_clip)

        # 7. Render & export MP4
        print(f"Rendering final MP4 to: {output_video_path.name}")
        video.write_videofile(
            str(output_video_path),
            fps=VIDEO_FPS,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            logger="bar"
        )

    finally:
        # Cleanly release file locks on Windows
        try:
            audio_clip.close()
        except Exception:
            pass
        for c in clips:
            try:
                c.close()
            except Exception:
                pass
        try:
            video.close()
        except Exception:
            pass

    # Verify final output file
    if not output_video_path.exists() or output_video_path.stat().st_size == 0:
        raise RuntimeError(f"Video file generation failed or produced 0 bytes: {output_video_path}")

    file_size_mb = output_video_path.stat().st_size / (1024 * 1024)
    print("\n" + "=" * 60)
    print("Final video created:")
    print(f"{output_video_path} ({file_size_mb:.2f} MB)")
    print("=" * 60 + "\n")

    return output_video_path
