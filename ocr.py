import subprocess
import tempfile
import base64
import os
import json
import re


def extract_vocab_with_ai(image_bytes: bytes, filename: str) -> dict:
    """Use Claude CLI to analyze an image and extract Vietnamese vocabulary."""
    suffix = os.path.splitext(filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    prompt = """Analyse cette image. C'est une lecon ou liste de vocabulaire vietnamien.

Extrais TOUS les mots et phrases de vocabulaire que tu trouves.
Pour chaque mot/phrase, donne la traduction francaise.

Reponds UNIQUEMENT avec du JSON valide, sans markdown, sans ```json, juste le JSON brut.
Format exact:
{
  "entries": [
    {"vietnamese": "mot en vietnamien", "french": "traduction francaise", "category": "categorie"},
    ...
  ],
  "description": "description courte du contenu de l'image"
}

Pour la categorie, deduis-la du contexte (ex: "Salutations", "Nourriture", "Nombres", "Verbes", "Phrases courantes", etc.)

Si tu vois des phrases completes, inclus-les aussi.
Si tu vois des tons ou de la phonetique, inclus-les dans le champ vietnamese.
Extrais TOUT ce qui est pertinent pour apprendre le vietnamien."""

    try:
        result = subprocess.run(
            [
                "/home/claude-user/.local/bin/claude",
                "--print",
                prompt,
                tmp_path,
            ],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PATH": "/home/claude-user/.local/bin:" + os.environ.get("PATH", "")}
        )

        raw_output = result.stdout.strip()

        # Try to parse JSON from output
        entries = _parse_ai_response(raw_output)

        return {
            "raw_text": raw_output,
            "entries": entries.get("entries", []),
            "description": entries.get("description", ""),
            "method": "ai"
        }
    except subprocess.TimeoutExpired:
        # Fallback to tesseract
        return _fallback_tesseract(tmp_path)
    except Exception as e:
        return _fallback_tesseract(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _parse_ai_response(text: str) -> dict:
    """Parse JSON from Claude's response, handling various formats."""
    # Remove markdown code blocks if present
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last resort: return empty
    return {"entries": [], "description": "Erreur de parsing"}


def _fallback_tesseract(tmp_path: str) -> dict:
    """Fallback to Tesseract OCR if AI fails."""
    try:
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "-l", "vie+fra"],
            capture_output=True, text=True, timeout=30
        )
        raw_text = result.stdout.strip()
        entries = _parse_vocabulary_lines(raw_text)
        return {
            "raw_text": raw_text,
            "entries": entries,
            "description": "Extraction OCR (fallback)",
            "method": "tesseract"
        }
    except Exception:
        return {
            "raw_text": "",
            "entries": [],
            "description": "Echec de l'extraction",
            "method": "error"
        }


def _parse_vocabulary_lines(raw_text: str) -> list[dict]:
    """Parse OCR text into vocabulary entries."""
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    entries = []

    for line in lines:
        for sep in ["=", ":", " - ", "\t", "   "]:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    entries.append({
                        "vietnamese": parts[0].strip(),
                        "french": parts[1].strip(),
                        "category": "",
                    })
                    break

    return entries
