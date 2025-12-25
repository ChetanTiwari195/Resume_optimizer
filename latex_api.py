import base64
import subprocess
import tempfile
import os
import uuid
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------------- LOGGING SETUP ----------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "latex_api.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------- APP ----------------
app = FastAPI()

class LatexRequest(BaseModel):
    latex: str
    return_logs: bool = False  # useful for debugging in n8n

# ---------------- HELPERS ----------------
def extract_latex_error(output: str) -> str:
    """
    Extract first meaningful LaTeX error.
    """
    for line in output.splitlines():
        if line.startswith("!"):
            return line
    return "Unknown LaTeX compilation error"

# ---------------- API ----------------
@app.post("/compile")
def compile_latex(req: LatexRequest):
    request_id = str(uuid.uuid4())
    logging.info(f"[{request_id}] Compilation request received")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "document.tex")
        pdf_path = os.path.join(tmpdir, "document.pdf")
        log_path = os.path.join(tmpdir, "document.log")

        # Write LaTeX
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(req.latex)

        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "document.tex"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=20,
                text=True
            )
        except subprocess.TimeoutExpired:
            logging.error(f"[{request_id}] pdflatex timeout")
            raise HTTPException(408, "LaTeX compilation timed out")

        combined_output = (result.stdout or "") + "\n" + (result.stderr or "")

        # Save raw log per request
        request_log_file = os.path.join(LOG_DIR, f"{request_id}.log")
        with open(request_log_file, "w", encoding="utf-8") as f:
            f.write(combined_output)

        # Compilation failed
        if result.returncode != 0 or not os.path.exists(pdf_path):
            error_msg = extract_latex_error(combined_output)
            logging.error(f"[{request_id}] Compilation failed: {error_msg}")

            response = {
                "status": "error",
                "request_id": request_id,
                "error": error_msg
            }

            if req.return_logs:
                response["logs"] = combined_output[-4000:]  # last 4KB

            raise HTTPException(status_code=400, detail=response)

        # Encode PDF
        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode()

        logging.info(f"[{request_id}] Compilation success")

        response = {
            "status": "success",
            "request_id": request_id,
            "pdf_base64": pdf_base64
        }

        if req.return_logs:
            response["logs"] = combined_output[-4000:]

        return response
