"""
Lightweight Desktop UI for the Automated Multimedia Pipeline.
Provides a clean, simple, light-themed interface to run and monitor the pipeline.
No heavy web frameworks or servers required — built with standard Python Tkinter.
"""

import os
import sys
import threading
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Project modules
from config import (
    BASE_DIR,
    OUTPUTS_DIR,
    IMAGES_DIR,
    AUDIO_DIR,
    VIDEO_DIR,
    FINAL_VIDEO_FILE,
    NARRATION_FILE,
    HF_TOKEN,
    HF_MODEL,
    HF_MODELS_POOL,
    ensure_directories,
    validate_hf_token
)
from prompts import IMAGE_PROMPTS, SCENE_TITLES, NARRATION_SCRIPTS
from image_generator import generate_image
from tts_generator import generate_narration
from video_creator import create_slideshow_video


class MultimediaPipelineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GenAI Multimedia Pipeline — Student Journey")
        self.root.geometry("960x780")
        self.root.minsize(860, 680)

        # Apply clean light theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color palette
        self.bg_color = "#f8f9fa"
        self.panel_bg = "#ffffff"
        self.primary_color = "#0d6efd"
        self.text_color = "#212529"
        self.border_color = "#dee2e6"

        self.root.configure(bg=self.bg_color)
        self.style.configure(".", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.panel_bg, relief="solid", borderwidth=1)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("Card.TLabel", background=self.panel_bg, foreground=self.text_color)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1e293b", background=self.bg_color)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10), foreground="#64748b", background=self.bg_color)
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=self.primary_color, foreground="#ffffff")

        self.scene_labels = []
        self.scene_images = []
        self.is_running = False

        self._build_ui()
        self._load_existing_previews()

    def _build_ui(self):
        # Main scrollable canvas or packed frames
        container = ttk.Frame(self.root, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Header Section
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_lbl = ttk.Label(header_frame, text="Automated Multimedia Pipeline with GenAI", style="Header.TLabel")
        title_lbl.pack(anchor="w")
        sub_lbl = ttk.Label(
            header_frame,
            text="Programmatic end-to-end multimedia creation: GenAI Images → TTS Narration → Synchronized MP4 Slideshow",
            style="SubHeader.TLabel"
        )
        sub_lbl.pack(anchor="w")

        # 2. Config & Controls Card
        ctrl_card = ttk.Frame(container, style="Card.TFrame", padding="12")
        ctrl_card.pack(fill=tk.X, pady=(0, 10))

        # Row 1: Token & Model
        cfg_grid = ttk.Frame(ctrl_card, style="Card.TFrame")
        cfg_grid.pack(fill=tk.X)

        ttk.Label(cfg_grid, text="Hugging Face Token:", style="Card.TLabel", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.token_var = tk.StringVar(value=HF_TOKEN)
        self.token_entry = ttk.Entry(cfg_grid, textvariable=self.token_var, width=32, show="*")
        self.token_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        show_token_btn = ttk.Button(cfg_grid, text="Show", width=6, command=self._toggle_token_visibility)
        show_token_btn.grid(row=0, column=2, padx=5, pady=3)

        ttk.Label(cfg_grid, text="Model:", style="Card.TLabel", font=("Segoe UI", 9, "bold")).grid(row=0, column=3, sticky="w", padx=(20, 5), pady=3)
        self.model_var = tk.StringVar(value=HF_MODEL)
        self.model_combo = ttk.Combobox(cfg_grid, textvariable=self.model_var, values=HF_MODELS_POOL, width=35, state="readonly")
        self.model_combo.grid(row=0, column=4, sticky="w", padx=5, pady=3)

        # Action Buttons
        btn_frame = ttk.Frame(ctrl_card, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(8, 0))

        self.run_btn = ttk.Button(
            btn_frame,
            text="▶ Start Automated Pipeline",
            style="Primary.TButton",
            command=self._start_pipeline_thread
        )
        self.run_btn.pack(side=tk.LEFT, padx=5)

        self.skip_img_var = tk.BooleanVar(value=False)
        self.skip_chk = ttk.Checkbutton(
            btn_frame,
            text="Skip image generation (use existing images)",
            variable=self.skip_img_var
        )
        self.skip_chk.pack(side=tk.LEFT, padx=15)

        self.play_btn = ttk.Button(
            btn_frame,
            text="▶ Play Final Video",
            command=self._play_final_video
        )
        self.play_btn.pack(side=tk.RIGHT, padx=5)

        self.open_dir_btn = ttk.Button(
            btn_frame,
            text="📁 Open Outputs Folder",
            command=self._open_output_folder
        )
        self.open_dir_btn.pack(side=tk.RIGHT, padx=5)

        # 3. Progress Bar & Status
        prog_frame = ttk.Frame(container)
        prog_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_lbl = ttk.Label(prog_frame, text="Status: Ready to execute.", font=("Segoe UI", 9, "bold"))
        self.status_lbl.pack(anchor="w", pady=(0, 2))

        self.progress_bar = ttk.Progressbar(prog_frame, orient=tk.HORIZONTAL, mode="determinate", maximum=8)
        self.progress_bar.pack(fill=tk.X)

        # 4. 5-Scene Image Preview Gallery
        preview_card = ttk.Frame(container, style="Card.TFrame", padding="10")
        preview_card.pack(fill=tk.X, pady=(0, 10))

        gallery_title = ttk.Label(preview_card, text="Story Scenes (AI-Generated Journey of a Student)", style="Card.TLabel", font=("Segoe UI", 10, "bold"))
        gallery_title.pack(anchor="w", pady=(0, 6))

        gallery_grid = ttk.Frame(preview_card, style="Card.TFrame")
        gallery_grid.pack(fill=tk.X)

        for i in range(5):
            col_frame = ttk.Frame(gallery_grid, style="Card.TFrame", padding="4")
            col_frame.grid(row=0, column=i, padx=5, sticky="nsew")
            gallery_grid.columnconfigure(i, weight=1)

            lbl_title = ttk.Label(col_frame, text=f"Scene {i+1}", font=("Segoe UI", 8, "bold"), style="Card.TLabel")
            lbl_title.pack(anchor="center")

            # Image canvas / placeholder
            img_lbl = tk.Label(col_frame, text="[No Image]", bg="#e9ecef", fg="#6c757d", width=20, height=6, relief="groove")
            img_lbl.pack(pady=4)
            self.scene_labels.append(img_lbl)

        # 5. Live Console Log Box
        log_frame = ttk.Frame(container)
        log_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(log_frame, text="Pipeline Execution Log:", font=("Segoe UI", 9, "bold")).pack(anchor="w")

        self.log_text = tk.Text(log_frame, height=9, bg="#ffffff", fg="#212529", font=("Consolas", 9), relief="solid", borderwidth=1)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text["yscrollcommand"] = scrollbar.set

    def log(self, message: str):
        """Append log message safely to GUI text box."""
        def _append():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, _append)

    def set_status(self, text: str, step: int = None):
        """Update status label and progress bar safely."""
        def _update():
            self.status_lbl.config(text=f"Status: {text}")
            if step is not None:
                self.progress_bar["value"] = step
        self.root.after(0, _update)

    def _toggle_token_visibility(self):
        current = self.token_entry.cget("show")
        self.token_entry.config(show="" if current == "*" else "*")

    def _load_existing_previews(self):
        """Loads thumbnails if scene images already exist on disk."""
        for i in range(1, 6):
            img_file = IMAGES_DIR / f"scene_{i:02d}.png"
            if img_file.exists():
                self._update_preview(i, img_file)

    def _update_preview(self, scene_idx: int, img_path: Path):
        """Updates a specific scene slot thumbnail."""
        try:
            with Image.open(img_path) as img:
                thumb = img.resize((150, 84), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(thumb)
                # Keep reference to avoid garbage collection
                self.scene_images.append(photo)
                lbl = self.scene_labels[scene_idx - 1]
                lbl.config(image=photo, text="", width=150, height=84)
        except Exception as e:
            self.log(f"Warning: Could not update preview for Scene {scene_idx}: {e}")

    def _open_output_folder(self):
        ensure_directories()
        os.startfile(OUTPUTS_DIR)

    def _play_final_video(self):
        if not FINAL_VIDEO_FILE.exists():
            messagebox.showwarning("Video Not Found", "The final video has not been generated yet. Please run the pipeline first.")
            return
        os.startfile(FINAL_VIDEO_FILE)

    def _start_pipeline_thread(self):
        if self.is_running:
            return
        token = self.token_var.get().strip()
        os.environ["HF_TOKEN"] = token
        os.environ["HF_MODEL"] = self.model_var.get().strip()

        # Check token if not skipping images
        if not self.skip_img_var.get():
            if not token or token in {"your_token_here", "your_huggingface_token_here"}:
                messagebox.showerror(
                    "Missing Token",
                    "Please provide a valid Hugging Face Access Token to generate images.\n"
                    "Get a free token at https://huggingface.co/settings/tokens\n"
                    "Or enable 'Skip image generation' to test video assembly."
                )
                return

        self.is_running = True
        self.run_btn.config(state=tk.DISABLED)
        self.log_text.delete("1.0", tk.END)
        threading.Thread(target=self._run_pipeline_worker, daemon=True).start()

    def _run_pipeline_worker(self):
        try:
            ensure_directories()
            self.set_status("Initializing directories...", 1)
            self.log("=" * 60)
            self.log("Starting Automated Multimedia Pipeline")
            self.log("=" * 60)

            prompts = IMAGE_PROMPTS
            self.set_status("Loaded prompts. Starting image generation...", 2)

            skip_images = self.skip_img_var.get()
            image_paths = []

            for idx, prompt in enumerate(prompts, start=1):
                img_path = IMAGES_DIR / f"scene_{idx:02d}.png"
                if skip_images and img_path.exists():
                    self.log(f"Scene {idx}: Using existing file {img_path.name}")
                    image_paths.append(img_path)
                else:
                    self.set_status(f"Generating image {idx}/5...", 2 + idx * 0.4)
                    self.log(f"[{idx}/5] Generating scene {idx}...")
                    self.log(f"  Prompt: {prompt[:75]}...")
                    saved_img = generate_image(prompt, img_path)
                    image_paths.append(saved_img)

                # Update thumbnail in UI
                self.root.after(0, lambda i=idx, p=img_path: self._update_preview(i, p))

            self.set_status("Generating TTS narration audio...", 5)
            self.log("\nGenerating narration...")
            audio_path = generate_narration(output_path=NARRATION_FILE)
            self.log(f"Voiceover saved: {audio_path.name}")

            self.set_status("Creating slideshow with MoviePy...", 6)
            self.log("\nCreating slideshow...")
            self.log("Adding voiceover...")

            final_video = create_slideshow_video(
                image_paths=image_paths,
                audio_path=audio_path,
                output_video_path=FINAL_VIDEO_FILE
            )

            self.set_status("Completed! Final MP4 ready.", 8)
            self.log("\n" + "=" * 60)
            self.log("Final video created:")
            self.log(str(final_video))
            self.log("=" * 60)

            self.root.after(0, lambda: messagebox.showinfo(
                "Pipeline Complete",
                f"Automated multimedia pipeline executed successfully!\n\nVideo saved to:\n{final_video}"
            ))

        except Exception as e:
            self.set_status(f"Error: {e}", 0)
            self.log(f"\n[ERROR] Pipeline failed: {e}")
            self.root.after(0, lambda: messagebox.showerror("Execution Error", str(e)))

        finally:
            self.is_running = False
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))


def main():
    root = tk.Tk()
    app = MultimediaPipelineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
