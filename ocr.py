import subprocess
import tempfile
import os
import json
import re
import glob as globmod


CLAUDE_PATH = "/home/claude-user/.local/bin/claude"

PROMPT = """Analyse ce document. C'est une lecon ou liste de vocabulaire vietnamien.

Extrais TOUS les mots et phrases de vocabulaire que tu trouves.
Pour chaque mot/phrase, donne la traduction francaise.

Reponds UNIQUEMENT avec du JSON valide, sans markdown, sans ```json, juste le JSON brut.
Format exact:
{
  "entries": [
    {"vietnamese": "mot en vietnamien", "french": "traduction francaise", "category": "categorie"},
    ...
  ],
  "description": "description courte du contenu"
}

Pour la categorie, deduis-la du contexte (ex: "Salutations", "Nourriture", "Nombres", "Verbes", "Phrases courantes", etc.)

Si tu vois des phrases completes, inclus-les aussi.
Si tu vois des tons ou de la phonetique, inclus-les dans le champ vietnamese.
Extrais TOUT ce qui est pertinent pour apprendre le vietnamien."""


DOCUMENT_EXTENSIONS = {".doc", ".docx", ".odt", ".rtf", ".ppt", ".pptx", ".xls", ".xlsx"}


def extract_vocab_with_ai(file_bytes: bytes, filename: str) -> dict:
    """Analyze an image, PDF or document and extract Vietnamese vocabulary."""
    suffix = os.path.splitext(filename)[1].lower() or ".png"

    if suffix == ".pdf":
        return _process_pdf(file_bytes)
    elif suffix in DOCUMENT_EXTENSIONS:
        return _process_document(file_bytes, suffix)
    else:
        return _process_image(file_bytes, suffix)


def _process_image(image_bytes: bytes, suffix: str) -> dict:
    """Process a single image with Claude."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        return _call_claude([tmp_path])
    finally:
        _safe_delete(tmp_path)


def _process_document(file_bytes: bytes, suffix: str) -> dict:
    """Convert doc/docx/odt/etc to PDF via LibreOffice, then process as PDF."""
    tmpdir = tempfile.mkdtemp(prefix="vietlearn_doc_")
    doc_path = os.path.join(tmpdir, "input" + suffix)

    with open(doc_path, "wb") as f:
        f.write(file_bytes)

    try:
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", tmpdir, doc_path],
            capture_output=True, timeout=60,
            env={**os.environ, "HOME": tmpdir}
        )

        pdf_path = os.path.join(tmpdir, "input.pdf")
        if not os.path.exists(pdf_path):
            return {
                "raw_text": "",
                "entries": [],
                "description": f"Echec de conversion {suffix} → PDF",
                "method": "error",
                "pages": 0,
            }

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        return _process_pdf(pdf_bytes)

    finally:
        for f in globmod.glob(os.path.join(tmpdir, "*")):
            _safe_delete(f)
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


def _process_pdf(pdf_bytes: bytes) -> dict:
    """Convert PDF pages to images, then process each with Claude."""
    tmpdir = tempfile.mkdtemp(prefix="vietlearn_pdf_")
    pdf_path = os.path.join(tmpdir, "input.pdf")

    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    try:
        # Convert PDF to images (150 DPI, good enough for text)
        subprocess.run(
            ["pdftoppm", "-png", "-r", "150", pdf_path, os.path.join(tmpdir, "page")],
            capture_output=True, timeout=60
        )

        page_images = sorted(globmod.glob(os.path.join(tmpdir, "page-*.png")))

        if not page_images:
            return {
                "raw_text": "",
                "entries": [],
                "description": "Aucune page extraite du PDF",
                "method": "error",
                "pages": 0,
            }

        # Send all page images to Claude in one call
        return _call_claude(page_images, page_count=len(page_images))

    finally:
        # Cleanup temp dir
        for f in globmod.glob(os.path.join(tmpdir, "*")):
            _safe_delete(f)
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


def _call_claude(image_paths: list[str], page_count: int = 1) -> dict:
    """Call Claude CLI with one or more images."""
    cmd = [CLAUDE_PATH, "--print", PROMPT] + image_paths

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=180,
            env={**os.environ, "PATH": "/home/claude-user/.local/bin:" + os.environ.get("PATH", "")}
        )

        raw_output = result.stdout.strip()
        parsed = _parse_ai_response(raw_output)

        return {
            "raw_text": parsed.get("description", raw_output[:500]),
            "entries": parsed.get("entries", []),
            "description": parsed.get("description", ""),
            "method": "ai",
            "pages": page_count,
        }
    except subprocess.TimeoutExpired:
        return {
            "raw_text": "",
            "entries": [],
            "description": "Timeout - le fichier est trop gros",
            "method": "error",
            "pages": page_count,
        }
    except Exception as e:
        return {
            "raw_text": str(e),
            "entries": [],
            "description": f"Erreur: {e}",
            "method": "error",
            "pages": page_count,
        }


def _parse_ai_response(text: str) -> dict:
    """Parse JSON from Claude's response."""
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"entries": [], "description": "Erreur de parsing"}


def _safe_delete(path: str):
    try:
        os.unlink(path)
    except OSError:
        pass
