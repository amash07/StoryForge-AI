"""
Text-to-Speech (TTS) Generation Module.
Synthesizes speech narration for the 5-scene student journey story.
Uses gTTS (Google Text-to-Speech) as primary high-quality engine,
with offline pyttsx3 fallback support.
"""

import os
from pathlib import Path
from config import NARRATION_FILE, AUDIO_DIR, ensure_directories
from prompts import NARRATION_SCRIPTS, get_full_narration_text


def _generate_with_gtts(text: str, output_path: Path) -> Path:
    """
    Generates narration using gTTS (Google Text-to-Speech).
    Produces a natural-sounding MP3 file.
    """
    from gtts import gTTS
    # slow=False gives a professional cadence
    tts = gTTS(text=text, lang="en", tld="com", slow=False)
    tts.save(str(output_path))
    return output_path


def _generate_with_pyttsx3(text: str, output_path: Path) -> Path:
    """
    Offline fallback using pyttsx3 (SAPI5 on Windows).
    """
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)     # Natural speaking pace
    engine.setProperty("volume", 1.0)   # Full volume
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    return output_path


def generate_narration(
    narration_text: str = None,
    output_path: Path = NARRATION_FILE
) -> Path:
    """
    Generates a single continuous narration audio file for the 5 scenes.
    
    Args:
        narration_text: Optional custom text. If None, uses get_full_narration_text().
        output_path: Destination path for the audio file (.mp3 or .wav).
        
    Returns:
        Path: The absolute path to the generated audio file.
    """
    ensure_directories()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if narration_text is None:
        # Form clean narrative with clear punctuation pauses between scenes
        narration_text = "\n\n".join(NARRATION_SCRIPTS)

    print("\n" + "=" * 60)
    print("Generating narration...")
    print("=" * 60)
    print(f"Narration text length: {len(narration_text)} characters across 5 scenes.")

    # Attempt primary TTS engine (gTTS)
    try:
        print("Synthesizing speech with primary TTS engine (gTTS)...")
        _generate_with_gtts(narration_text, output_path)
    except Exception as gtts_err:
        print(f"[!] Primary TTS (gTTS) encountered an issue: {gtts_err}")
        print("    Switching to offline fallback TTS engine (pyttsx3)...")
        try:
            # If MP3 not supported natively by pyttsx3, save as wav or direct
            _generate_with_pyttsx3(narration_text, output_path)
        except Exception as offline_err:
            raise RuntimeError(
                f"Both TTS engines failed to generate narration audio:\n"
                f"  gTTS error: {gtts_err}\n"
                f"  pyttsx3 error: {offline_err}"
            )

    # Validate output
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise FileNotFoundError(f"Failed to generate valid audio file at: {output_path}")

    file_size_kb = output_path.stat().st_size / 1024
    print(f"[OK] Narration audio saved successfully: {output_path} ({file_size_kb:.1f} KB)")
    return output_path
