import os
import uuid
import subprocess
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="LaTeX Compiler API")

class LatexRequest(BaseModel):
    latex: str

@app.post("/compile", response_class=FileResponse)
def compile_latex(req: LatexRequest):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory(prefix=f"latex_{job_id}_") as tmpdir:
        tex_file = os.path.join(tmpdir, "main.tex")
        pdf_file = os.path.join(tmpdir, "main.pdf")

        # Write LaTeX
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(req.latex)

        # Compile
        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "main.tex"
        ]

        result = subprocess.run(
            cmd,
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0 or not os.path.exists(pdf_file):
            raise HTTPException(
                status_code=400,
                detail=result.stdout.decode(errors="ignore")
            )

        # Return PDF directly
        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename="output.pdf"
        )
