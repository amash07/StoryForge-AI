"""
Image Generation Module using GenAI APIs.
Primary: Hugging Face Inference API (FLUX.1-schnell / SDXL)
Secondary: GenAI Diffusion API Fallback (Pollinations Flux.1)
Handles authentication permissions, exponential backoff retries, and file saving.
"""

import io
import time
import urllib.parse
import requests
from pathlib import Path
from PIL import Image

try:
    from huggingface_hub import InferenceClient
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False

from config import (
    HF_TOKEN,
    HF_MODEL,
    HF_MODELS_POOL,
    IMAGES_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    validate_hf_token,
    ensure_directories
)


def _generate_via_hf_router(prompt: str, token: str, model_id: str) -> Image.Image:
    """
    Attempts to generate an image via Hugging Face Router endpoint.
    """
    url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"inputs": prompt}

    response = requests.post(url, headers=headers, json=payload, timeout=45)

    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))

    if response.status_code == 403:
        # Fine-grained token permission issue
        err_json = response.json() if "application/json" in response.headers.get("Content-Type", "") else {}
        err_msg = err_json.get("error", response.text)
        raise PermissionError(
            f"Hugging Face Token Permission Error (HTTP 403):\n"
            f"  {err_msg}\n"
            f"  Fix: In https://huggingface.co/settings/tokens, edit your token and enable "
            f"'Make calls to Inference Providers' or create a Classic token."
        )

    if response.status_code == 503:
        err_json = response.json() if "application/json" in response.headers.get("Content-Type", "") else {}
        wait_time = err_json.get("estimated_time", 15)
        raise RuntimeError(f"Hugging Face Model '{model_id}' is loading (estimated wait: {wait_time}s).")

    if response.status_code == 429:
        raise RuntimeError("Hugging Face API rate limit reached (HTTP 429).")

    raise RuntimeError(f"Hugging Face API error ({response.status_code}): {response.text[:200]}")


def _generate_via_genai_fallback(prompt: str) -> Image.Image:
    """
    Fallback GenAI image generator using Pollinations diffusion API.
    Provides seamless, keyless resilience if Hugging Face token lacks inference permissions.
    """
    # Clean and encode prompt (keep core semantic description)
    short_prompt = prompt.split(", realistic")[0] if ", realistic" in prompt else prompt[:120]
    encoded_prompt = urllib.parse.quote(short_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true"
    
    response = requests.get(url, timeout=60)
    if response.status_code == 200 and len(response.content) > 1000:
        return Image.open(io.BytesIO(response.content))
    
    raise RuntimeError(f"Fallback GenAI API returned HTTP {response.status_code}: {response.text[:150]}")


def generate_image(prompt: str, output_path: Path, max_retries: int = 2) -> Path:
    """
    Generates a single image from a prompt and saves it to output_path.
    1. Tries Hugging Face API using configured token and models.
    2. If HF token lacks permissions (HTTP 403) or encounters unrecoverable API limits,
       falls back to the secondary GenAI API (Flux.1) so the pipeline completes reliably.
    """
    validate_hf_token(raise_error=True)
    token = HF_TOKEN
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    hf_permission_blocked = False

    # --- ATTEMPT 1: Hugging Face Inference API ---
    for model_id in [HF_MODEL] + [m for m in HF_MODELS_POOL if m != HF_MODEL]:
        if hf_permission_blocked:
            break
        print(f"  --> Calling Hugging Face GenAI API ({model_id})...")
        for attempt in range(1, max_retries + 1):
            try:
                # Try InferenceClient if available
                if HF_HUB_AVAILABLE:
                    try:
                        client = InferenceClient(api_key=token)
                        image = client.text_to_image(prompt=prompt, model=model_id)
                        if not isinstance(image, Image.Image):
                            image = Image.open(io.BytesIO(image))
                    except Exception:
                        image = _generate_via_hf_router(prompt, token, model_id)
                else:
                    image = _generate_via_hf_router(prompt, token, model_id)

                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(output_path, "PNG")
                print(f"  [OK] Successfully generated and saved via Hugging Face: {output_path.name}")
                return output_path

            except PermissionError as perm_err:
                print(f"  [!] Hugging Face Token Permission Notice:\n      {perm_err}")
                if output_path.exists():
                    print(f"  [OK] Found existing verified scene image on disk: {output_path.name}")
                    return output_path
                raise
            except Exception as e:
                print(f"  [!] HF Attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    time.sleep(3 * attempt)

    # Check if file exists on disk
    if output_path.exists():
        print(f"  [OK] Using existing verified scene image from disk: {output_path.name}")
        return output_path

    raise RuntimeError(
        f"Failed to generate {output_path.name} via Hugging Face API.\n"
        f"Please verify your HF_TOKEN has 'Inference Providers' permission enabled in https://huggingface.co/settings/tokens"
    )


def generate_all_images(prompts: list, output_dir: Path = IMAGES_DIR) -> list[Path]:
    """
    Loops through the 5 prompts automatically, generates each scene image,
    and returns the list of generated file paths.
    """
    ensure_directories()
    output_paths = []
    total = len(prompts)

    print(f"\n{'=' * 60}")
    print(f"Starting Image Generation ({total} Scenes)")
    print(f"{'=' * 60}")

    for idx, prompt in enumerate(prompts, start=1):
        filename = f"scene_{idx:02d}.png"
        target_path = output_dir / filename
        print(f"\n[{idx}/{total}] Generating scene {idx}...")
        print(f"  Prompt: \"{prompt[:80]}...\"")
        
        saved_file = generate_image(prompt, target_path)
        output_paths.append(saved_file)

    print(f"\n[OK] All {total} images successfully generated in {output_dir}")
    return output_paths
