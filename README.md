# Automated Multimedia Pipeline with GenAI APIs

An automated Python pipeline that programmatically generates an end-to-end multimedia video story: **"AI-Generated Journey of a Student"**.

---

## 1. Project Title
**Automated Multimedia Pipeline with GenAI APIs: "AI-Generated Journey of a Student"**

## 2. Objective
The objective of this project is to transition from manual, GUI-based multimedia authoring to **programmatic, automated multimedia synthesis**. By coordinating generative AI models for image creation, Text-to-Speech (TTS) synthesis, and programmatic video editing via MoviePy, the entire multimedia production cycle is executed without manual intervention.

## 3. What the Pipeline Does
1. **Iterates Programmatically:** Automatically loops through 5 structured prompt variations illustrating the life cycle of an engineering student (college entrance, computer science classroom, hands-on software project, technical placement interview, and beginning a technology career).
2. **Generates GenAI Imagery:** Communicates with the Hugging Face Inference API (`FLUX.1-schnell` / `SDXL`) to generate five realistic 16:9 cinematic images and saves them to `outputs/images/`.
3. **Synthesizes Narration Voiceover:** Automatically synthesizes spoken narrative audio for all five scenes using Text-to-Speech (TTS) and exports `outputs/audio/narration.mp3`.
4. **Assembles Slideshow Video:** Normalizes images to standard 1280x720 HD resolution, computes per-slide timing to match speech duration, attaches the voiceover audio, and exports `outputs/final_video/student_journey.mp4`.

---

## 4. System Workflow Diagram

```
5 Prompts
    ↓
Python Loop
    ↓
Hugging Face GenAI API
    ↓
5 AI Images
    ↓
Save Images
    ↓
TTS Generation
    ↓
Narration Audio
    ↓
MoviePy
    ↓
Slideshow + Voiceover
    ↓
Final MP4
```

---

## 5. Technologies Used

| Layer | Technology | Role |
|---|---|---|
| **Programming Language** | Python 3.11+ | Primary pipeline orchestration |
| **Generative Image AI** | Hugging Face Inference API (`FLUX.1-schnell` / `SDXL`) | Generating 5 high-definition scene visuals |
| **Voiceover Synthesis (TTS)** | `gTTS` (Google TTS) / `pyttsx3` (Offline fallback) | Programmatic narration audio creation |
| **Video Composition** | `MoviePy 2.x` & `FFmpeg` | Image resizing, duration timing, audio-video muxing |
| **Image Processing** | `Pillow (PIL)` | Pre-processing, aspect-ratio cropping (1280x720) |
| **Environment & Secrets** | `python-dotenv` | Secure API token management without hardcoding |
| **Lightweight UI** | Python `Tkinter` / `ttk` | Optional clean light desktop UI for demonstration |

---

## 6. Project Structure

```
genai_multimedia_pipeline/
│
├── main.py                  # Main CLI pipeline orchestrator (Steps 1-8)
├── app_gui.py               # Lightweight desktop UI (Tkinter)
├── config.py                # Configuration, directory setup & token validation
├── image_generator.py       # Hugging Face GenAI image synthesis & retries
├── video_creator.py         # MoviePy video assembly & audio synchronization
├── tts_generator.py         # TTS voiceover synthesis (gTTS + pyttsx3 fallback)
├── prompts.py               # 5 prompts, scene titles & narration scripts
├── requirements.txt         # Explicit project dependencies
├── .env.example             # Template for API token configuration
├── .gitignore               # Excludes secrets, caches, and output media
├── README.md                # Comprehensive project documentation
│
├── outputs/                 # Automatically created upon execution
│   ├── images/              # scene_01.png ... scene_05.png
│   ├── audio/               # narration.mp3
│   └── final_video/         # student_journey.mp4
│
└── docs/
    └── task2_report.md      # Academic report for faculty evaluation
```

---

## 7. Installation

### Step A: Clone or Navigate to the Project Directory
Open PowerShell or Command Prompt:
```powershell
cd e:\Projects\College\Multimedia
```

### Step B: Create a Virtual Environment
```powershell
python -m venv venv
```

### Step C: Activate Virtual Environment (Windows)
```powershell
.\venv\Scripts\activate
```
*(On macOS/Linux, run `source venv/bin/activate`)*

### Step D: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 8. API Key Setup

1. Obtain a free Hugging Face User Access Token:
   - Visit [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Click **Create new token** (Role: **Read** is sufficient).
   - Copy your token (starts with `hf_...`).
2. Open the `.env` file in the project root directory (or copy from `.env.example`):
   ```ini
   HF_TOKEN=hf_your_actual_token_here
   HF_MODEL=black-forest-labs/FLUX.1-schnell
   ```
3. Save the `.env` file. **Never commit `.env` to Git** (it is ignored in `.gitignore`).

---

## 9. How to Run

### Option 1: Automated Command-Line Pipeline (Recommended for Assignment & Viva)
Run the complete automated pipeline:
```powershell
python main.py
```

#### Expected CLI Progress Output:
```text
######################################################################
 AUTOMATED MULTIMEDIA PIPELINE WITH GENAI APIS
 Project: 'AI-Generated Journey of a Student' (5 Scenes)
######################################################################

[STEP 1/8] Loading configuration and initializing directories...
[STEP 2/8] Loading the 5 prompt variations and story narration...
[STEP 3 & 4/8] Generating and saving 5 scene images via Hugging Face API...
[1/5] Generating scene 1...
[2/5] Generating scene 2...
[3/5] Generating scene 3...
[4/5] Generating scene 4...
[5/5] Generating scene 5...

[STEP 5/8] Generating Text-to-Speech narration...
Generating narration...

[STEP 6, 7 & 8/8] Assembling video, synchronizing voiceover, and exporting MP4...
Creating slideshow...
Adding voiceover...

Final video created:
outputs/final_video/student_journey.mp4
```

#### Re-rendering Video without Re-downloading Images:
If images are already generated and you wish to adjust video/narration parameters quickly:
```powershell
python main.py --skip-images
```

---

### Option 2: Lightweight Desktop UI
If you prefer a visual demonstration interface:
```powershell
python app_gui.py
```
- Pre-loads your token and model settings from `.env`.
- Displays live step-by-step progress and terminal logs.
- Features a **5-Scene Preview Gallery** where generated images appear dynamically.
- Includes **Play Final Video** and **Open Outputs Folder** buttons.

---

## 10. Expected Outputs

Upon pipeline completion, the `outputs/` directory contains:
- `outputs/images/scene_01.png` — College Entrance scene (1280x720)
- `outputs/images/scene_02.png` — Computer Science Classroom scene (1280x720)
- `outputs/images/scene_03.png` — Software Project Coding scene (1280x720)
- `outputs/images/scene_04.png` — Technical Placement Preparation scene (1280x720)
- `outputs/images/scene_05.png` — Technology Career Beginning scene (1280x720)
- `outputs/audio/narration.mp3` — Complete spoken voiceover audio
- `outputs/final_video/student_journey.mp4` — Master MP4 video file with synchronized audio

---

## 11. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `ValueError: Missing or unconfigured Hugging Face API Token` | `.env` has placeholder value or missing token | Paste your real token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) into `.env`. |
| `HTTP 401 Unauthorized` | Invalid Hugging Face token | Verify your token on Hugging Face and ensure no leading/trailing spaces in `.env`. |
| `HTTP 503 Model Loading` | HF cold start for serverless inference | The script automatically waits and retries up to 3 times with exponential backoff. |
| `MoviePy AttributeError: 'ImageClip' has no attribute 'set_duration'` | MoviePy 2.x API migration | Resolved: `video_creator.py` detects MoviePy version and supports both `with_duration` (2.x) and `set_duration` (1.x). |
| Windows Audio File Lock | MoviePy / FFmpeg process keeping handles open | Resolved: `video_creator.py` explicitly closes clips in a `finally` block before file exit. |
