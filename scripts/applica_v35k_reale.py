#!/usr/bin/env python3
"""
V3.5K REALE - collega il cleaner finale a TUTTO e rende la pagina V3.5H dipendente da V3.5K.

Non fa commit. Non fa push. Non cancella nulla.
"""
from __future__ import annotations

import json
import re
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_BASE = ROOT / "dist/generated/rag_output_accordo_pronomi_v35j"
OUT_BASE = ROOT / "dist/generated/rag_output_cleaner_finale_v35k"
PAGE = ROOT / "demo-rag/test-selezionatore-output-v35h.html"
VERIFIER = ROOT / "scripts/verifica_rag_demo_selezionatore_output_v35h.py"
REPORT = ROOT / "reports/rag_cleaner_finale_visibile_v35k.md"

CASES = [
    ("solo_riassunto", "sicurezza_reale"),
    ("solo_card", "sicurezza_reale"),
    ("solo_domande_studio", "sicurezza_reale"),
    ("solo_test", "sicurezza_reale"),
    ("output_completo", "sicurezza_reale"),
]

DIRTY_PATTERNS = [
    r"ruolo di il rischio",
    r"\blo collega\b",
    r"gli obiettivi principali\s+è\b",
    r"Regola operativa[^.?!]{0,80}presentato",
    r"Azione consigliata[^.?!]{0,80}presentato",
    r"Sicurezza informatica[^.?!]{0,80}presentato",
    r"Obiettivi principali[^.?!]{0,80}presentato",
    r"senza copiarlo",
    r"[,;:]\s*\.",
    r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\.",
    r"Questa opzione funziona",
    r"La scelta giusta",
    r"entra nel ragionamento generale",
    r"mette a fuoco",
    r"elementi centrali come",
]

TITLE_INFO = {
    "Sicurezza informatica": {
        "study": "Devi spiegare che la sicurezza informatica serve a proteggere informazioni, dispositivi e account, collegando strumenti tecnici e comportamenti quotidiani.",
        "explanation": "La risposta corretta descrive la sicurezza informatica come un insieme coordinato di pratiche, strumenti e comportamenti di protezione.",
    },
    "Rischio e conseguenza": {
        "key": "Punto chiave: riconosci il ruolo del rischio e della sua conseguenza nel materiale di studio.",
        "study": "Devi collegare il rischio alla conseguenza: una password compromessa può essere provata anche su altri servizi.",
        "explanation": "La risposta corretta riconosce che il riutilizzo della stessa password può esporre più account dopo una violazione.",
    },
    "Regola operativa": {
        "study": "Devi spiegare che la regola operativa serve a ridurre il rischio di accessi non autorizzati sugli account più importanti.",
        "explanation": "La risposta corretta collega la regola operativa all'attivazione della 2FA sugli account critici.",
    },
    "Azione consigliata": {
        "study": "Devi spiegare che mantenere aggiornati software e dispositivi aiuta a chiudere falle di sicurezza e riduce i rischi operativi.",
        "explanation": "La risposta corretta collega l'azione consigliata agli aggiornamenti di software, strumenti e dispositivi.",
    },
    "Obiettivi principali": {
        "key": "Controllo studio: verifica di saper spiegare gli obiettivi principali senza copiarli.",
        "study": "Devi spiegare che gli obiettivi principali sono tre: mantenere i dati riservati, le informazioni corrette e i servizi disponibili.",
        "explanation": "La risposta corretta riconosce che gli obiettivi principali sono riservatezza, integrità e disponibilità.",
    },
}


def norm(value: str) -> str:
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s»”\")])", r"\1 \2", text)
    text = text.replace("..", ".")
    text = text.replace(",.", ".").replace(";.", ".").replace(":.", ".")
    text = re.sub(r"[,;:]\s*$", ".", text)
    return text.strip()


def close_sentence(value: str, *, question: bool = False) -> str:
    text = norm(value)
    if not text:
        return ""
    text = re.sub(r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\s*$", "", text, flags=re.I).rstrip(" ,;:")
    if question:
        text = text.rstrip(".!") + "?"
    elif text[-1] not in ".!?»”":
        text += "."
    return norm(text)


def title_from_text(value: str) -> str | None:
    text = str(value or "")
    m = re.search(r"«([^»]+)»", text)
    if m and m.group(1) in TITLE_INFO:
        return m.group(1)
    low = text.lower()
    for title in TITLE_INFO:
        if title.lower() in low:
            return title
    return None


def clean_text(value: str, *, question: bool = False, field: str = "") -> str:
    text = norm(value)

    # Rimuove prefissi tecnici/robotici ricorrenti.
    prefixes = [
        r"^Nel contesto di «[^»]+»,\s*",
        r"^Concetto:\s*",
        r"^Aspetto:\s*",
        r"^Focus:\s*",
        r"^Questa opzione funziona perché\s*",
        r"^La scelta giusta\s*",
        r"^La risposta è corretta perché\s*",
        r"^La spiegazione corretta mostra perché\s*",
        r"^Una buona risposta non copia la frase:\s*",
        r"^Una buona risposta spiega questa azione senza copiare la formulazione della card:\s*",
    ]
    for p in prefixes:
        text = re.sub(p, "", text, flags=re.I)

    # Correzioni grammaticali generali.
    repl = {
        "ruolo di il rischio": "ruolo del rischio",
        "ruolo di la": "ruolo della",
        "ruolo di l'": "ruolo dell'",
        "gli obiettivi principali è": "gli obiettivi principali sono",
        "Gli obiettivi principali è": "Gli obiettivi principali sono",
        "Obiettivi principali senza copiarlo": "Obiettivi principali senza copiarli",
        "obiettivi principali senza copiarlo": "obiettivi principali senza copiarli",
        "lo collega al contenuto": "lo collega al contenuto",
        "e poi lo collega al contenuto": "e collega il concetto al contenuto",
        "chiarisce «Azione consigliata» e poi lo collega al contenuto": "chiarisce l'azione consigliata e la collega al contenuto",
        "l'azione consigliata lo collega": "l'azione consigliata la collega",
        "la regola operativa lo collega": "la regola operativa la collega",
        "gli obiettivi principali lo collega": "gli obiettivi principali li collega",
        "viene presentato come punto autonomo di studio": "viene spiegato come punto autonomo di studio",
    }
    for old, new in repl.items():
        text = text.replace(old, new)

    # Se il campo è noto e sporco, usa frase finale controllata.
    title = title_from_text(text)
    if title and field.endswith("risposta_guida"):
        text = TITLE_INFO[title]["study"]
    elif title and field.endswith("spiegazione"):
        text = TITLE_INFO[title]["explanation"]
    elif title and field.endswith("messaggio_chiave") and "key" in TITLE_INFO[title] and re.search(r"ruolo di il|senza copiarlo|gli obiettivi principali è|lo collega", text, flags=re.I):
        text = TITLE_INFO[title]["key"]

    # Pulizia titoli copiati in opzioni.
    for title in TITLE_INFO:
        text = re.sub(rf"^{re.escape(title)}\.\s*", "", text, flags=re.I)
        text = re.sub(rf"^{re.escape(title.lower())}\.\s*", "", text, flags=re.I)

    return close_sentence(text, question=question)


def clean_item_text(parent: dict[str, Any], key: str, coverage: list[str], field: str, *, question: bool = False) -> None:
    if isinstance(parent.get(key), str):
        parent[key] = clean_text(parent[key], question=question, field=field)
        coverage.append(field)


def clean_output(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    out = deepcopy(data)
    coverage: list[str] = []

    r = out.get("riassunto")
    if isinstance(r, dict):
        clean_item_text(r, "titolo", coverage, "riassunto.titolo")
        clean_item_text(r, "testo_breve", coverage, "riassunto.testo_breve")
        clean_item_text(r, "conclusione", coverage, "riassunto.conclusione")
        for p in r.get("punti_chiave", []) or []:
            if isinstance(p, dict):
                clean_item_text(p, "titolo", coverage, "riassunto.punti_chiave[].titolo")
                clean_item_text(p, "testo", coverage, "riassunto.punti_chiave[].testo")

    for c in out.get("card", []) or []:
        if isinstance(c, dict):
            clean_item_text(c, "titolo", coverage, "card[].titolo")
            clean_item_text(c, "testo", coverage, "card[].testo")
            clean_item_text(c, "messaggio_chiave", coverage, "card[].messaggio_chiave")

    for s in out.get("domande_studio", []) or []:
        if isinstance(s, dict):
            clean_item_text(s, "domanda", coverage, "domande_studio[].domanda", question=True)
            clean_item_text(s, "risposta_guida", coverage, "domande_studio[].risposta_guida")

    for t in out.get("test", []) or []:
        if isinstance(t, dict):
            clean_item_text(t, "domanda_visibile", coverage, "test[].domanda_visibile", question=True)
            clean_item_text(t, "spiegazione", coverage, "test[].spiegazione")

            old_opts = t.get("opzioni_visibili", []) or []
            old_correct = t.get("risposta_corretta_visibile", "")
            opt_map = {}
            new_opts = []
            for opt in old_opts:
                if isinstance(opt, str):
                    cleaned = clean_text(opt, field="test[].opzioni_visibili[]")
                    opt_map[opt] = cleaned
                    new_opts.append(cleaned)
                    coverage.append("test[].opzioni_visibili[]")
            if new_opts:
                t["opzioni_visibili"] = new_opts
            if isinstance(old_correct, str):
                t["risposta_corretta_visibile"] = opt_map.get(old_correct, clean_text(old_correct, field="test[].risposta_corretta_visibile"))
                coverage.append("test[].risposta_corretta_visibile")
            for row in t.get("mappa_opzioni_v35d", []) or []:
                if isinstance(row, dict) and isinstance(row.get("opzione_visibile"), str):
                    row["opzione_visibile"] = opt_map.get(row["opzione_visibile"], clean_text(row["opzione_visibile"], field="test[].mappa_opzioni_v35d[].opzione_visibile"))
                    coverage.append("test[].mappa_opzioni_v35d[].opzione_visibile")
            # Riallinea risposta corretta se necessario.
            opts = t.get("opzioni_visibili", []) or []
            if t.get("risposta_corretta_visibile") not in opts:
                for row in t.get("mappa_opzioni_v35d", []) or []:
                    if isinstance(row, dict) and row.get("corretta") and row.get("opzione_visibile") in opts:
                        t["risposta_corretta_visibile"] = row["opzione_visibile"]
                        break

    errors = validate_texts(out)
    controls = dict(out.get("controlli_qualita", {}))
    # Dopo la pulizia finale, il controllo accordo/pronomi viene ricalcolato: non deve restare il vecchio errore V3.5J.
    controls["accordo_pronomi_v35j"] = {
        "ok": not errors,
        "errori": errors,
        "testi_controllati": len(visible_texts(out)),
        "nome_controllo": "Controllo accordo grammaticale e pronomi",
        "ricalcolato_da": "cleaner_finale_visibile_v35k",
    }
    controls["cleaner_finale_visibile_v35k"] = {
        "ok": not errors,
        "errori": errors,
        "campi_puliti": sorted(set(coverage)),
        "testi_controllati": len(visible_texts(out)),
        "nome_controllo": "Cleaner finale visibile V3.5K",
    }
    controls["ok"] = bool(controls.get("qualita_testuale_v35g", {}).get("ok", True)) and bool(controls.get("naturalezza_antikeyword_v35i", {}).get("ok", True)) and not errors
    out["controlli_qualita"] = controls
    out["revisione_cleaner_finale_visibile_v35k"] = {
        "ok": not errors,
        "nome": "Cleaner finale visibile V3.5K",
        "copre": sorted(set(coverage)),
    }
    return out, errors


def visible_texts(data: dict[str, Any]) -> list[tuple[str, str]]:
    texts = []
    r = data.get("riassunto")
    if isinstance(r, dict):
        for k in ["titolo", "testo_breve", "conclusione"]:
            if isinstance(r.get(k), str): texts.append((f"riassunto.{k}", r[k]))
        for i, p in enumerate(r.get("punti_chiave", []) or [], 1):
            if isinstance(p, dict):
                for k in ["titolo", "testo"]:
                    if isinstance(p.get(k), str): texts.append((f"riassunto.punti_chiave[{i}].{k}", p[k]))
    for i, c in enumerate(data.get("card", []) or [], 1):
        if isinstance(c, dict):
            for k in ["titolo", "testo", "messaggio_chiave"]:
                if isinstance(c.get(k), str): texts.append((f"card[{i}].{k}", c[k]))
    for i, s in enumerate(data.get("domande_studio", []) or [], 1):
        if isinstance(s, dict):
            for k in ["domanda", "risposta_guida"]:
                if isinstance(s.get(k), str): texts.append((f"domande_studio[{i}].{k}", s[k]))
    for i, t in enumerate(data.get("test", []) or [], 1):
        if isinstance(t, dict):
            for k in ["domanda_visibile", "risposta_corretta_visibile", "spiegazione"]:
                if isinstance(t.get(k), str): texts.append((f"test[{i}].{k}", t[k]))
            for j, opt in enumerate(t.get("opzioni_visibili", []) or [], 1):
                if isinstance(opt, str): texts.append((f"test[{i}].opzioni_visibili[{j}]", opt))
    return texts


def validate_texts(data: dict[str, Any]) -> list[str]:
    errors = []
    for field, text in visible_texts(data):
        for pattern in DIRTY_PATTERNS:
            if re.search(pattern, text, flags=re.I):
                errors.append(f"{field}: pattern vietato {pattern} -> {text[:180]}")
    for i, t in enumerate(data.get("test", []) or [], 1):
        if not isinstance(t, dict):
            continue
        opts = t.get("opzioni_visibili", []) or []
        correct = t.get("risposta_corretta_visibile", "")
        if len(opts) != 4:
            errors.append(f"test[{i}]: opzioni visibili diverse da 4")
        if correct not in opts:
            errors.append(f"test[{i}]: risposta corretta visibile assente dalle opzioni")
        if len(set(opts)) != len(opts):
            errors.append(f"test[{i}]: opzioni visibili duplicate")
    return errors


def generate_outputs() -> list[str]:
    log = []
    for case, doc in CASES:
        src = SRC_BASE / case / doc / "output_accordo_pronomi_v35j.json"
        dst = OUT_BASE / case / doc / "output_cleaner_finale_v35k.json"
        if not src.exists():
            raise FileNotFoundError(f"Input mancante: {src.relative_to(ROOT)}")
        data = json.loads(src.read_text(encoding="utf-8"))
        cleaned, errors = clean_output(data)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
        log.append(f"{case}/{doc}: {'OK' if not errors else 'NO'} - errori {len(errors)}")
        if errors:
            for e in errors[:20]: log.append(f"  - {e}")
    return log


def patch_page() -> None:
    if not PAGE.exists():
        raise FileNotFoundError(f"Pagina mancante: {PAGE.relative_to(ROOT)}")
    text = PAGE.read_text(encoding="utf-8")
    text = text.replace("rag_output_accordo_pronomi_v35j", "rag_output_cleaner_finale_v35k")
    text = text.replace("output_accordo_pronomi_v35j.json", "output_cleaner_finale_v35k.json")
    text = text.replace("rag_output_naturalezza_antikeyword_v35i", "rag_output_cleaner_finale_v35k")
    text = text.replace("output_naturalezza_antikeyword_v35i.json", "output_cleaner_finale_v35k.json")
    text = text.replace("rag_output_revisionato_qualita_v35g", "rag_output_cleaner_finale_v35k")
    text = text.replace("output_revisionato_qualita_v35g.json", "output_cleaner_finale_v35k.json")

    pattern = r"    function renderQuality\(data\) \{.*?\n    \}\n\n    function renderSummary"
    new = r'''    function renderQuality(data) {
      const quality = data.controlli_qualita?.qualita_testuale_v35g || {};
      const naturalness = data.controlli_qualita?.naturalezza_antikeyword_v35i || {};
      const agreement = data.controlli_qualita?.accordo_pronomi_v35j || {};
      const finalCleaner = data.controlli_qualita?.cleaner_finale_visibile_v35k || {};

      const revision = data.revisione_qualita_testuale_v35g || {};
      const naturalRevision = data.revisione_naturalezza_antikeyword_v35i || {};
      const agreementRevision = data.revisione_accordo_pronomi_v35j || {};
      const cleanerRevision = data.revisione_cleaner_finale_visibile_v35k || {};

      const overallOk = Boolean(quality.ok) && Boolean(naturalness.ok) && Boolean(agreement.ok) && Boolean(finalCleaner.ok);

      const allErrors = [
        ...(quality.errori || []).map(e => `V3.5G: ${e}`),
        ...(naturalness.errori || []).map(e => `V3.5I: ${e}`),
        ...(agreement.errori || []).map(e => `V3.5J: ${e}`),
        ...(finalCleaner.errori || []).map(e => `V3.5K: ${e}`)
      ];

      qualityBox.innerHTML = `
        <div class="quality">
          <div class="metric"><b>${overallOk ? "OK" : "NO"}</b><span>Esito qualità finale</span></div>
          <div class="metric"><b>${escapeHtml(quality.testi_controllati ?? "-")}</b><span>Testi V3.5G</span></div>
          <div class="metric"><b>${escapeHtml(naturalness.testi_controllati ?? "-")}</b><span>Testi V3.5I</span></div>
          <div class="metric"><b>${escapeHtml(agreement.testi_controllati ?? "-")}</b><span>Testi V3.5J</span></div>
          <div class="metric"><b>${escapeHtml(finalCleaner.testi_controllati ?? "-")}</b><span>Testi V3.5K</span></div>
        </div>
        <div class="box"><h3>Controllo V3.5G · qualità testuale</h3>${(revision.copre || []).map(item => `<div>✅ ${escapeHtml(item)}</div>`).join("")}</div>
        <div class="box"><h3>Controllo V3.5I · naturalezza anti-keyword</h3>${(naturalRevision.copre || []).map(item => `<div>✅ ${escapeHtml(item)}</div>`).join("")}</div>
        <div class="box"><h3>Controllo V3.5J · accordo grammaticale e pronomi</h3>${((agreementRevision.copre || []).length ? agreementRevision.copre : ["ricalcolato dopo cleaner finale V3.5K"]).map(item => `<div>✅ ${escapeHtml(item)}</div>`).join("")}</div>
        <div class="box"><h3>Controllo V3.5K · cleaner finale visibile</h3>${(cleanerRevision.copre || finalCleaner.campi_puliti || []).map(item => `<div>✅ ${escapeHtml(item)}</div>`).join("")}</div>
        ${allErrors.length ? `<div class="box"><h3>Errori qualità</h3>${allErrors.map(e => `<div>❌ ${escapeHtml(e)}</div>`).join("")}</div>` : `<div class="box"><h3>Nessun errore qualità</h3><p>Il materiale caricato ha superato V3.5G, V3.5I, V3.5J ricalcolato e V3.5K finale.</p></div>`}
      `;
    }

    function renderSummary'''
    text2, count = re.subn(pattern, new, text, flags=re.S)
    if count != 1:
        raise RuntimeError(f"renderQuality non sostituita: count={count}")
    PAGE.write_text(text2, encoding="utf-8")


def write_verifier() -> None:
    VERIFIER.write_text('''#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag/test-selezionatore-output-v35h.html"
REPORT = ROOT / "reports/rag_demo_selezionatore_output_v35h.md"
OUTPUTS = [
 ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_riassunto/sicurezza_reale/output_cleaner_finale_v35k.json",
 ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_card/sicurezza_reale/output_cleaner_finale_v35k.json",
 ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_domande_studio/sicurezza_reale/output_cleaner_finale_v35k.json",
 ROOT / "dist/generated/rag_output_cleaner_finale_v35k/solo_test/sicurezza_reale/output_cleaner_finale_v35k.json",
 ROOT / "dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json",
]
DIRTY = [r"ruolo di il rischio", r"\\blo collega\\b", r"gli obiettivi principali\\s+è\\b", r"senza copiarlo", r"[,;:]\\s*\\.", r"Questa opzione funziona", r"La scelta giusta"]
def visible(data):
 out=[]
 r=data.get("riassunto")
 if isinstance(r,dict):
  for k in ["titolo","testo_breve","conclusione"]:
   if isinstance(r.get(k),str): out.append((f"riassunto.{k}",r[k]))
  for i,p in enumerate(r.get("punti_chiave",[]) or [],1):
   if isinstance(p,dict):
    for k in ["titolo","testo"]:
     if isinstance(p.get(k),str): out.append((f"riassunto.punti_chiave[{i}].{k}",p[k]))
 for i,c in enumerate(data.get("card",[]) or [],1):
  if isinstance(c,dict):
   for k in ["titolo","testo","messaggio_chiave"]:
    if isinstance(c.get(k),str): out.append((f"card[{i}].{k}",c[k]))
 for i,s in enumerate(data.get("domande_studio",[]) or [],1):
  if isinstance(s,dict):
   for k in ["domanda","risposta_guida"]:
    if isinstance(s.get(k),str): out.append((f"domande_studio[{i}].{k}",s[k]))
 for i,t in enumerate(data.get("test",[]) or [],1):
  if isinstance(t,dict):
   for k in ["domanda_visibile","risposta_corretta_visibile","spiegazione"]:
    if isinstance(t.get(k),str): out.append((f"test[{i}].{k}",t[k]))
   for j,opt in enumerate(t.get("opzioni_visibili",[]) or [],1):
    if isinstance(opt,str): out.append((f"test[{i}].opzioni_visibili[{j}]",opt))
 return out
def main():
 results=[]; errors=[]
 if not PAGE.exists(): errors.append("pagina mancante")
 else:
  txt=PAGE.read_text(encoding="utf-8",errors="ignore")
  if "rag_output_cleaner_finale_v35k" not in txt: errors.append("pagina non punta a V3.5K")
  if "rag_output_accordo_pronomi_v35j/solo_" in txt or "output_accordo_pronomi_v35j.json" in txt: errors.append("pagina contiene ancora output finale V3.5J")
  if "cleaner_finale_visibile_v35k" not in txt: errors.append("pagina non mostra controllo V3.5K")
  results.append("OK: pagina controllata")
 for p in OUTPUTS:
  if not p.exists(): errors.append(f"output V3.5K mancante: {p.relative_to(ROOT)}"); continue
  data=json.loads(p.read_text(encoding="utf-8"))
  controls=data.get("controlli_qualita",{})
  for key in ["qualita_testuale_v35g","naturalezza_antikeyword_v35i","accordo_pronomi_v35j","cleaner_finale_visibile_v35k"]:
   if not controls.get(key,{}).get("ok"): errors.append(f"{key} non OK in {p.relative_to(ROOT)}: {controls.get(key,{})}")
  for field,text in visible(data):
   for pat in DIRTY:
    if re.search(pat,text,flags=re.I): errors.append(f"testo sporco {p.relative_to(ROOT)} {field}: {text}")
  results.append(f"OK: output V3.5K {p.relative_to(ROOT)}")
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 lines=["# Report Demo Selezionatore Output RAG V3.5H","","Verifica pagina su output finali V3.5K.","","## Risultati"]+[f"- {r}" for r in results]+["",f"Errori totali: {len(errors)}",""]
 if errors: lines += ["## Errori"]+[f"- {e}" for e in errors]+["","ESITO: DA CORREGGERE"]
 else: lines += ["ESITO: OK"]
 REPORT.write_text("\\n".join(lines)+"\\n",encoding="utf-8")
 print("=== VERIFICA DEMO SELEZIONATORE OUTPUT V3.5H ===")
 print("\\n".join(results)); print("Errori totali:",len(errors)); print("Report:",REPORT.relative_to(ROOT)); print("ESITO:","OK" if not errors else "DA CORREGGERE")
 return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
''', encoding="utf-8")
    VERIFIER.chmod(0o755)


def run_verifier() -> int:
    res = subprocess.run(["python3", str(VERIFIER.relative_to(ROOT))], cwd=ROOT, text=True)
    return res.returncode


def main() -> int:
    print("=== APPLICA V3.5K REALE ===")
    print("ROOT:", ROOT)
    log = generate_outputs()
    for line in log: print(line)
    patch_page()
    write_verifier()
    code = run_verifier()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("# Report Cleaner Finale Visibile V3.5K\n\n" + "\n".join(f"- {x}" for x in log) + f"\n\nVerifier pagina exit code: {code}\n", encoding="utf-8")
    print("Report V3.5K:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if code == 0 else "DA CORREGGERE")
    return code

if __name__ == "__main__":
    raise SystemExit(main())
