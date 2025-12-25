# LaTeX Compiler API (Resume_optimizer)

This repository exposes a small FastAPI app in `latex_api.py` that compiles LaTeX to PDF using `pdflatex`.

Prerequisites

- Python 3.8+ installed and on PATH.
- A LaTeX distribution with `pdflatex` installed and on PATH (MiKTeX or TeX Live) for Windows.

Quick start (PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
# Activate in PowerShell
.\ .venv\Scripts\Activate.ps1
# If activation is blocked, run as admin or use:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the API with uvicorn (from repository root):

```powershell
python -m uvicorn latex_api:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

Test the `/compile` endpoint (PowerShell example)

```powershell
$latex = '{"latex":"\\documentclass{article}\\begin{document}Hello\\end{document}"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/compile -Method Post -ContentType 'application/json' -Body $latex -OutFile output.pdf
# The response will be saved to output.pdf
```

Notes and troubleshooting

- `pdflatex` must be installed. On Windows, install MiKTeX (https://miktex.org) or TeX Live and ensure `pdflatex` is on PATH.
- If the API returns an error, check the server logs printed by uvicorn; the LaTeX compiler output will be sent in the error detail.
- Consider restricting LaTeX input or running the compiler in a sandbox for production systems to avoid arbitrary code execution risks.
