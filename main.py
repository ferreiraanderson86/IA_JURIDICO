from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from analisador import ler_arquivo, gerar_analise

app = FastAPI(title="API Jurídica IA", version="1.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analisar_contrato")
async def analisar_contrato(file: UploadFile = File(...)):
    try:
        caminho = os.path.join(UPLOAD_DIR, file.filename)
        with open(caminho, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        texto = ler_arquivo(caminho)
        analise = gerar_analise(texto)

        return JSONResponse(content={"analise": analise})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
