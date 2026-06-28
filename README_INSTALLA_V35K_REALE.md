# V3.5K reale

Installa e applica il cleaner finale vero su tutti gli output visibili.

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
source /Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/activate
unzip -o /PERCORSO/DEL/FILE/pacchetto_v35k_reale.zip -d /Users/alessandrobarbarossa/alex-ai-workspace
python3 scripts/applica_v35k_reale.py
```

Controllo pagina:

```bash
grep -n "rag_output_" demo-rag/test-selezionatore-output-v35h.html
find dist/generated/rag_output_cleaner_finale_v35k -type f | sort
python3 scripts/verifica_rag_demo_selezionatore_output_v35h.py
```

Server:

```bash
python3 -m http.server 8080
```

URL:

```text
http://localhost:8080/demo-rag/test-selezionatore-output-v35h.html
```

Hard refresh:

```text
Cmd + Shift + R
```
