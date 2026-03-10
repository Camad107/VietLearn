import subprocess
import tempfile
import os
import re


def extract_text_from_image(image_bytes: bytes, filename: str) -> str:
    """Extract text from image using tesseract CLI."""
    suffix = os.path.splitext(filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "-l", "vie+fra"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except FileNotFoundError:
        # Fallback without Vietnamese language pack
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    finally:
        os.unlink(tmp_path)


def parse_vocabulary_lines(raw_text: str) -> list[dict]:
    """Parse OCR text into vocabulary entries.

    Tries to detect patterns like:
    - "vietnamese = french"
    - "vietnamese : french"
    - "vietnamese - french"
    - "vietnamese    french" (tab/spaces separated)
    """
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    entries = []

    for line in lines:
        # Try common separators
        for sep in ["=", ":", " - ", "\t", "   "]:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    entries.append({
                        "vietnamese": parts[0].strip(),
                        "french": parts[1].strip(),
                    })
                    break

    return entries
