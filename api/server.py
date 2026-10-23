"""REST wrapper leve sobre o kernel ZEPHIRUM (issue #33).

POST /decide {"program": "(decide ...)"}  -> executa no kernel trivalente
GET  /health                             -> status
Docker: docker/docker run da imagem deste repo (docker/Dockerfile).
"""
import tempfile, os
from fastapi import FastAPI
from pydantic import BaseModel
from zyql_lisp import run

app = FastAPI(title="ZEPHIRUM decision kernel", version="1.7.5")

class Program(BaseModel):
    program: str

@app.get("/health")
def health():
    return {"status": "ok", "kernel": "zephirum", "verdicts": ["1", "0", "REFUSED"]}

@app.post("/decide")
def decide(p: Program):
    with tempfile.NamedTemporaryFile("w", suffix=".zph", delete=False) as f:
        f.write(p.program); path = f.name
    try:
        run(path)
        return {"decision": "executed", "verdicts": ["1", "0", "REFUSED"], "program": p.program}
    finally:
        os.unlink(path)
