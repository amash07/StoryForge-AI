# Academic Project Report: Automated Multimedia Pipeline with GenAI APIs

---

## 1. Title
**Automated Multimedia Pipeline with GenAI APIs: "AI-Generated Journey of a Student"**

## 2. Objective
The primary objective of this project is to implement programmatic control over multimedia synthesis by transitioning away from manual, GUI-dependent tools (such as Premiere Pro, Canva, or manual web downloads). The resulting automated Python pipeline orchestrates:
- Generative AI image synthesis using the Hugging Face Inference API.
- Programmatic Text-to-Speech (TTS) voiceover creation.
- Dynamic duration synchronization and video composition via MoviePy and FFmpeg to output an MP4 video.

---

## 3. Problem Statement
Traditional multimedia creation relies on manual, fragmented workflows:
1. Manually crafting prompts and individually downloading images from web interfaces.
2. Manually synthesizing audio via online speech tools.
3. Manually importing assets into editing software, dragging timeline clips, resizing images, and exporting video files.

This manual process is repetitive, difficult to reproduce, non-scalable, and prone to human error. The challenge is to replace this entire workflow with an end-to-end automated Python script that accepts structured narrative prompts and automatically yields a finished, broadcast-ready MP4 multimedia artifact.

---

## 4. Approach
The system follows a modular architectural pipeline:
1. **Decoupled Architecture:** Each concern (configuration, prompt management, image generation, speech synthesis, and video authoring) is separated into specialized modules (`config.py`, `prompts.py`, `image_generator.py`, `tts_generator.py`, and `video_creator.py`).
2. **Deterministic Sequencing:** The master script `main.py` orchestrates execution sequentially across 8 atomic stages.
3. **Resilient Network Handling:** GenAI API interactions incorporate retry mechanisms with exponential backoff and alternate model fallbacks.
4. **Adaptive Time Allocation:** Slide duration is dynamically computed based on the synthesized audio duration so that narration and visuals remain in synchronization.

---

## 5. System Workflow

```
5 Prompts (prompts.py)
         ↓
Python Loop (main.py)
         ↓
Hugging Face GenAI API (FLUX.1-schnell / SDXL)
         ↓
5 Scene Images (outputs/images/scene_01.png - scene_05.png)
         ↓
Text-to-Speech Synthesis (gTTS / pyttsx3)
         ↓
Narration Audio (outputs/audio/narration.mp3)
         ↓
MoviePy Video Assembly & Aspect-Ratio Normalization (1280x720)
         ↓
Slideshow + Voiceover Synchronization
         ↓
Final Master MP4 (outputs/final_video/student_journey.mp4)
```

---

## 6. Technologies Used

- **Python 3.11:** Core execution environment.
- **Hugging Face Inference API / `huggingface_hub`:** Cloud-based text-to-image diffusion model (`black-forest-labs/FLUX.1-schnell` with fallback to `stabilityai/stable-diffusion-xl-base-1.0`).
- **Google Text-to-Speech (`gTTS`) & `pyttsx3`:** Programmatic voiceover generation with offline redundancy.
- **MoviePy 2.x:** Programmatic video composition, clip concatenation, and audio-video multiplexing.
- **FFmpeg 8.0:** Underlying multimedia encoding engine (`libx264` video codec, `aac` audio codec).
- **Pillow (PIL):** High-fidelity Lanczos image aspect-ratio scaling and cropping.
- **python-dotenv:** Safe environment variable loading without hardcoding credentials.
- **Tkinter / ttk:** Lightweight desktop UI for interactive demonstrations.

---

## 7. Design Choices

1. **Modular Code Structure Over Monolithic Script:**
   Splitting the codebase into single-responsibility modules makes each stage testable in isolation and easy to explain during a viva examination.
2. **Pre-processing via Pillow Before MoviePy Ingestion:**
   Rather than relying solely on MoviePy's internal resizing filters, images are pre-processed and center-cropped to 1280x720 using Pillow with `Image.Resampling.LANCZOS`. This prevents video distortion, eliminates black letterbox bars, and speeds up rendering.
3. **Dynamic Speech-Proportional Timing:**
   Instead of using arbitrary hardcoded image display times (e.g., 5 seconds per image), the system measures the exact duration of the generated audio track (`AudioFileClip.duration`) and distributes the timeline evenly across the 5 scenes plus an 0.8-second buffer.
4. **Zero-Cost, Keyless Primary TTS:**
   Using `gTTS` provides natural-sounding voice synthesis without requiring an additional paid API key or third-party service subscription, keeping the project accessible for academic demonstration.
5. **No Heavy Frontend Frameworks:**
   The primary pipeline operates purely in the terminal via `python main.py`. An optional lightweight Tkinter GUI (`app_gui.py`) is provided using Python's standard library, avoiding heavy web frameworks like Streamlit, Flask, or Next.js.

---

## 8. Prompt Strategy
To maintain visual consistency across all five narrative scenes, the prompts follow a unified descriptive schema:
- **Consistent Subject:** *"The same young engineering student..."* is maintained across all prompts.
- **Atmospheric Keywords:** Realistic photography style, modern engineering environment, cinematic composition, and 16:9 aspect ratio are explicitly specified.
- **Chronological Progression:**
  - *Scene 1 (Entrance):* Arriving at a modern engineering college campus, carrying a backpack, excited and hopeful.
  - *Scene 2 (Classroom):* Attending a computer science lecture, sitting with peers in front of modern computers.
  - *Scene 3 (Project):* Focused on coding and software development inside an innovative computer laboratory.
  - *Scene 4 (Interview):* Preparing technical interview notes and practicing coding interview questions.
  - *Scene 5 (Career):* Working as a professional software engineer inside a technology workplace.

---

## 9. Parameters Selected

| Parameter | Selected Value | Justification |
|---|---|---|
| **Video Resolution** | 1280 x 720 (720p HD) | Standard 16:9 aspect ratio; balances high visual clarity with rapid rendering speed on student machines. |
| **Video Framerate** | 24 FPS | Standard cinematic framerate; ensures smooth audio-video synchronization without excessive computational overhead. |
| **Video Codec** | `libx264` (H.264) | Universal compatibility across Windows Media Player, QuickTime, VLC, and web browsers. |
| **Audio Codec** | `aac` | Standard stereo audio format paired with H.264 MP4 containers. |
| **Image Sampling** | Lanczos Resampling | Preserves sharp text on computer screens and facial details in generated photos. |
| **Audio Tail Buffer** | 0.8 seconds | Prevents the video from abruptly cutting off immediately when the narrator finishes speaking the last syllable. |

---

## 10. Error Handling
The pipeline enforces defense-in-depth error handling across all layers:
1. **Missing or Default API Key:** `config.py` validates `HF_TOKEN` against common placeholders (`your_token_here`). It halts execution before API calls are made and prints step-by-step token acquisition instructions.
2. **API Cold Starts (HTTP 503):** Hugging Face serverless models may take 15–30 seconds to load into memory. The generator detects HTTP 503, reads the `estimated_time` header, and retries with exponential backoff.
3. **Rate Limits & Failovers (HTTP 429 / 404):** If a model is unavailable or rate-limited, the system falls back to alternate models (`stabilityai/stable-diffusion-xl-base-1.0`, `runwayml/stable-diffusion-v1-5`).
4. **TTS Network Failure:** If `gTTS` fails due to network disruption, `tts_generator.py` falls back to the local, offline `pyttsx3` speech engine.
5. **Missing File Verification:** Video composition verifies the existence of all 5 image files and the audio file before initializing MoviePy objects.
6. **Resource Disposal on Windows:** Windows file handles frequently lock media files during FFmpeg operations. All clips are enclosed in `try...finally` blocks with explicit `.close()` calls.

---

## 11. Observed Issues During Development

During initial testing and development on the actual runtime environment, four specific technical issues were observed:
1. **MoviePy 2.x API Migration Breakage:**
   The environment installed `moviepy==2.1.2`. In MoviePy 2.x, legacy methods (`.set_duration()`, `.set_audio()`, and `.resize()`) were removed/deprecated in favor of `.with_duration()`, `.with_audio()`, and `.resized()`. Calling legacy methods triggered immediate `AttributeError: 'ImageClip' object has no attribute 'set_duration'`.
2. **Windows Terminal Character Encoding (`charmap` / `cp1252`):**
   Standard PowerShell on Windows defaults to code page 1252. Outputting Unicode checkmark symbols (`\u2713`) in console logs triggered a fatal `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'`.
3. **Hugging Face Fine-Grained Token Permission Scopes (HTTP 403):**
   When utilizing a fine-grained token created with only repository read privileges (`repo.content.read`), the Hugging Face Router rejected requests with `403 Forbidden: This authentication method does not have sufficient permissions to call Inference Providers`.
4. **Windows Media File Locking:**
   When re-running the video pipeline, Windows threw `PermissionError: [WinError 32]` because underlying FFmpeg sub-processes retained locks on `narration.mp3` and `student_journey.mp4`.

---

## 12. How the Problems Were Handled

1. **Dual-Version MoviePy Compatibility:**
   Helper functions (`_set_clip_duration`, `_set_clip_audio`) were implemented with dynamic introspection (`hasattr`). If `with_duration` exists (MoviePy 2.x), it is called; otherwise, it seamlessly falls back to `set_duration` (MoviePy 1.x), ensuring cross-version compatibility.
2. **ASCII-Safe Console Output:**
   All Unicode checkmarks and non-ASCII glyphs were replaced with universal ASCII badges (e.g. `[OK]`, `[!]`), preventing any `UnicodeEncodeError` across Windows terminals.
3. **Token Permission Diagnostics & Caching:**
   The image generator parses HTTP 403 responses specifically, printing clear instructions for enabling "Inference Providers" on `https://huggingface.co/settings/tokens`. Furthermore, the pipeline automatically caches verified scene images to disk, allowing video rendering and verification to proceed uninterrupted.
4. **Deterministic Resource Cleanup:**
   All MoviePy clip objects (`AudioFileClip`, `ImageClip`, and `CompositeVideoClip`) are wrapped inside structured `try...finally` blocks with explicit `.close()` calls to guarantee immediate file handle release on Windows.

---

## 13. Final Output
The automated pipeline produces:
- **5 High-Resolution Images:** `outputs/images/scene_01.png` through `scene_05.png`.
- **1 Master Audio Voiceover:** `outputs/audio/narration.mp3`.
- **1 Broadcast-Ready MP4 Video:** `outputs/final_video/student_journey.mp4` (1280x720, 24 FPS, synchronized H.264/AAC).

---

## 14. Conclusion
This project successfully demonstrates a fully automated, programmatic multimedia generation pipeline. By combining generative AI APIs for content creation with programmatic video editing libraries, the entire production workflow—from prompt ingestion to final MP4 video export—is completed without manual intervention. The modular design, comprehensive error handling, and robust cross-version compatibility make the system reliable, repeatable, and well-suited for academic demonstration.
