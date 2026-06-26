# RAG Documento Studio V4.4 - PDF exact capture

Installa un fix che cattura esattamente il materiale generato nella pagina e lo salva in PDF come immagini paginate.

Comandi:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
source backend/.venv/bin/activate

unzip ~/Downloads/rag_documento_studio_v44_pdf_exact_pack.zip -d .

python3 scripts/installa_rag_documento_studio_v44_pdf_exact.py --root .

python3 scripts/verifica_rag_documento_studio_v44_pdf_exact.py

python3 -m http.server 8000
```

Apri:

```text
http://localhost:8000/demo-rag/test-rag-documento-studio-v44.html
```

Hard refresh:

```text
Cmd + Shift + R
```
