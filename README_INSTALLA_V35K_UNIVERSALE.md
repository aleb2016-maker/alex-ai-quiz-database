# V3.5K universale

Questo pacchetto sostituisce la logica V3.5K temporanea con un cleaner finale universale.

Non fa commit e non fa push.

Installazione:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
source /Users/alessandrobarbarossa/alex-ai-workspace/backend/.venv/bin/activate
unzip -o ~/Downloads/pacchetto_v35k_universale.zip -d /Users/alessandrobarbarossa/alex-ai-workspace
python3 scripts/applica_v35k_universale.py
```

Verifica:

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
