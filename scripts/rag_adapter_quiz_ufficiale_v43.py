#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "generated" / "rag_quiz_bridge_v43.json"
DEFAULT_CONTAINER = ROOT / "dist" / "generated" / "rag_quiz_bridge_v43_container.json"
REPORT_PATH = ROOT / "reports" / "rag_adapter_quiz_ufficiale_v43.md"

STOP_CONCETTI = {
    "deve", "devono", "usare", "usa", "fare", "avere", "essere", "può", "possono",
    "questo", "questa", "quello", "quella", "parte", "documento", "testo", "utente",
    "sistema", "cosa", "quali", "perché", "quando", "come", "molto"
}

VALIDATORI_ESISTENTI = [
    "scripts/rag_valida_quiz_json.py",
    "scripts/rag_valida_distrattori_forti.py",
    "scripts/validatore_rag_distrattori_forti_v2.py",
    "scripts/qualita_linguistica.py",
    "scripts/motore_qualita_generale.py",
]


@dataclass
class Candidate:
    concetto: str
    domanda: str
    corretta: str
    distrattori: list[str]
    spiegazione: str
    tags: list[str]
    fonte: str


def normalizza_spazi(testo: str) -> str:
    return re.sub(r"\s+", " ", str(testo or "")).strip()


def pulisci_testo(testo: str) -> str:
    testo = testo.replace("\ufeff", " ")
    testo = testo.replace("þÿ", " ")
    testo = testo.replace("\\n", "\n")
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    return testo.strip()


def frasi_da_testo(testo: str) -> list[str]:
    testo = pulisci_testo(testo)
    parti = re.split(r"(?<=[.!?])\s+|\n+", testo)
    frasi = []
    for parte in parti:
        frase = normalizza_spazi(parte)
        if 45 <= len(frase) <= 280:
            frasi.append(frase)
    return frasi


def parole_chiave(testo: str) -> list[str]:
    parole = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{4,}", testo.lower())
    parole = [p for p in parole if p not in STOP_CONCETTI]
    frequenze: dict[str, int] = {}
    for parola in parole:
        if parola.isdigit():
            continue
        frequenze[parola] = frequenze.get(parola, 0) + 1
    ordinate = sorted(frequenze.items(), key=lambda item: (-item[1], item[0]))
    return [p for p, _ in ordinate[:30]]


def contiene(testo: str, *parole: str) -> bool:
    basso = testo.lower()
    return any(parola.lower() in basso for parola in parole)


def scegli_frase(frasi: list[str], *parole: str) -> str:
    for frase in frasi:
        if contiene(frase, *parole):
            return frase
    return frasi[0] if frasi else ""


def crea_candidate_sicurezza(testo: str) -> list[Candidate]:
    frasi = frasi_da_testo(testo)
    candidates: list[Candidate] = []

    def add(concetto: str, domanda: str, corretta: str, distrattori: list[str], spiegazione: str, tags: list[str], fonte: str) -> None:
        candidates.append(Candidate(
            concetto=concetto,
            domanda=normalizza_spazi(domanda),
            corretta=normalizza_spazi(corretta),
            distrattori=[normalizza_spazi(d) for d in distrattori],
            spiegazione=normalizza_spazi(spiegazione),
            tags=tags,
            fonte=normalizza_spazi(fonte),
        ))

    if contiene(testo, "password"):
        fonte = scegli_frase(frasi, "password")
        add(
            "password sicure",
            "Secondo il documento, quale caratteristica deve avere una password sicura?",
            "Deve essere lunga, difficile da indovinare e diversa per ogni servizio.",
            [
                "Deve essere lunga, ma può essere riutilizzata su tutti i servizi se è facile da ricordare.",
                "Deve essere breve e semplice, purché venga cambiata molto spesso.",
                "Deve essere salvata nel browser come unica protezione dell'account."
            ],
            "Una password sicura riduce il rischio di accesso non autorizzato perché è difficile da indovinare e non viene riutilizzata su più servizi.",
            ["password", "sicurezza", "account"],
            fonte,
        )
        add(
            "riuso password",
            "Perché usare la stessa password su più siti è rischioso?",
            "Se un servizio viene violato, la stessa password può essere provata anche su altri account.",
            [
                "Perché la password diventa automaticamente pubblica su tutti i dispositivi collegati.",
                "Perché i siti bloccano sempre gli utenti che usano password simili.",
                "Perché il browser cancella tutte le password uguali senza avvisare l'utente."
            ],
            "Il riuso della password crea un effetto domino: una sola violazione può mettere a rischio più account.",
            ["password", "account", "riuso"],
            fonte,
        )

    if contiene(testo, "2fa", "due fattori", "autenticazione a due fattori"):
        fonte = scegli_frase(frasi, "2fa", "due fattori", "autenticazione")
        add(
            "autenticazione a due fattori",
            "Quale vantaggio offre l'autenticazione a due fattori secondo il documento?",
            "Aggiunge un secondo controllo oltre alla password, riducendo il rischio se la password viene rubata.",
            [
                "Sostituisce completamente la password, quindi l'utente non deve più ricordarla.",
                "Rende inutile aggiornare software e sistemi operativi.",
                "Protegge solo la rete Wi-Fi, ma non gli account online."
            ],
            "La 2FA non elimina la password, ma aggiunge un secondo livello di verifica che rende più difficile l'accesso abusivo.",
            ["2fa", "autenticazione", "account"],
            fonte,
        )

    if contiene(testo, "phishing", "mittente", "link"):
        fonte = scegli_frase(frasi, "phishing", "mittente", "link")
        add(
            "phishing",
            "Quale comportamento aiuta a riconoscere un possibile tentativo di phishing?",
            "Controllare mittente, link sospetti, tono urgente e richieste insolite di password o dati bancari.",
            [
                "Aprire subito il link se il messaggio sembra urgente, così si evita il blocco dell'account.",
                "Fidarsi del messaggio quando contiene il logo di un'azienda conosciuta.",
                "Rispondere al messaggio chiedendo conferma della password prima di accedere."
            ],
            "Il phishing sfrutta urgenza, link ingannevoli e richieste anomale: controllare questi segnali riduce il rischio.",
            ["phishing", "email", "link"],
            fonte,
        )

    if contiene(testo, "malware", "allegati", "antivirus", "endpoint"):
        fonte = scegli_frase(frasi, "malware", "allegati", "antivirus", "endpoint")
        add(
            "malware",
            "Quale combinazione di azioni riduce meglio il rischio malware?",
            "Evitare software non autorizzato, non aprire allegati inattesi, aggiornare i sistemi e usare strumenti di protezione.",
            [
                "Installare molti programmi sconosciuti, purché l'antivirus venga avviato una volta al mese.",
                "Aprire gli allegati solo dopo averli rinominati con un nome più chiaro.",
                "Disattivare gli aggiornamenti per evitare cambiamenti improvvisi nel computer."
            ],
            "La prevenzione del malware richiede più comportamenti insieme: prudenza sugli allegati, aggiornamenti e strumenti di protezione.",
            ["malware", "allegati", "protezione"],
            fonte,
        )

    if contiene(testo, "backup"):
        fonte = scegli_frase(frasi, "backup")
        add(
            "backup",
            "Perché i backup regolari sono importanti in un documento sulla sicurezza informatica?",
            "Permettono di recuperare dati e lavoro se un guasto, un attacco o un ransomware causa perdita o blocco dei file.",
            [
                "Servono solo a velocizzare la connessione Internet durante il lavoro quotidiano.",
                "Eliminano la necessità di usare password sicure e autenticazione a due fattori.",
                "Impediscono sempre l'arrivo di email di phishing nella casella di posta."
            ],
            "Il backup non impedisce ogni attacco, ma riduce il danno perché consente il recupero dei dati.",
            ["backup", "ransomware", "dati"],
            fonte,
        )

    if contiene(testo, "wi-fi", "wifi", "rete"):
        fonte = scegli_frase(frasi, "wi-fi", "wifi", "rete")
        add(
            "rete Wi-Fi",
            "Quale indicazione rende più sicura una rete Wi-Fi aziendale o domestica?",
            "Usare una password forte e una crittografia adeguata.",
            [
                "Lasciare la rete aperta per evitare problemi di accesso agli utenti autorizzati.",
                "Usare una password corta uguale al nome della rete per ricordarla meglio.",
                "Proteggere solo i computer, perché la rete Wi-Fi non può essere attaccata."
            ],
            "Una rete Wi-Fi protetta riduce gli accessi non autorizzati e rende più sicura la comunicazione dei dispositivi.",
            ["wifi", "rete", "crittografia"],
            fonte,
        )

    return candidates


def crea_candidate_generiche(testo: str, numero: int) -> list[Candidate]:
    frasi = frasi_da_testo(testo)
    keywords = parole_chiave(testo)
    candidates: list[Candidate] = []
    usate: set[str] = set()

    for keyword in keywords:
        if len(candidates) >= numero:
            break
        if keyword in STOP_CONCETTI or keyword in usate:
            continue
        fonte = scegli_frase(frasi, keyword)
        if not fonte:
            continue
        concetto = keyword
        corretta = fonte.rstrip(".") + "."
        domanda = f"Quale affermazione descrive meglio il concetto di {concetto} nel documento?"
        distrattori = [
            f"Il concetto di {concetto} viene citato solo come dettaglio estetico, senza effetto pratico sul tema.",
            f"Il concetto di {concetto} indica sempre una procedura automatica che non richiede scelte dell'utente.",
            f"Il concetto di {concetto} serve principalmente a sostituire tutti gli altri punti del documento."
        ]
        spiegazione = f"Nel documento, {concetto} è collegato al contenuto analizzato e va interpretato nel contesto della frase: {fonte}"
        candidates.append(Candidate(concetto, domanda, corretta, distrattori, spiegazione, [concetto], fonte))
        usate.add(keyword)

    return candidates


def candidate_da_documento(testo: str, numero: int) -> list[Candidate]:
    testo_basso = testo.lower()
    if any(p in testo_basso for p in ["password", "phishing", "malware", "backup", "2fa", "ransomware", "wi-fi", "wifi"]):
        candidates = crea_candidate_sicurezza(testo)
    else:
        candidates = []
    if len(candidates) < numero:
        candidates.extend(crea_candidate_generiche(testo, numero - len(candidates)))
    return candidates[:numero]


def normalizza_domanda_ufficiale(candidate: Candidate, indice: int, categoria: str, sottocategoria: str) -> dict[str, Any]:
    opzioni = [candidate.corretta] + candidate.distrattori[:3]
    opzioni = [normalizza_spazi(o) for o in opzioni if normalizza_spazi(o)]

    # Mantiene 4 opzioni, senza duplicati esatti.
    pulite = []
    viste = set()
    for opzione in opzioni:
        chiave = opzione.lower()
        if chiave not in viste:
            pulite.append(opzione)
            viste.add(chiave)

    while len(pulite) < 4:
        pulite.append(f"Opzione vicina al tema {candidate.concetto}, ma sbagliata per un dettaglio pratico.")

    return {
        "id": f"RAG-V43-{indice:04d}",
        "categoria": categoria,
        "sottocategoria": sottocategoria,
        "livello": "medio",
        "domanda": candidate.domanda,
        "opzioni": pulite[:4],
        "risposta_corretta": candidate.corretta,
        "spiegazione": candidate.spiegazione,
        "tags": candidate.tags[:5],
        "difficolta": 2,
        "distrattore_forte": pulite[1],
        "motivo_distrattore_forte": "È vicino al tema della risposta corretta, ma cambia un dettaglio tecnico, logico o pratico che lo rende sbagliato.",
        "regola_distrattori": "tre_distrattori_forti",
        "criterio_distrattori": "Ogni risposta errata deve condividere il concetto centrale della corretta e diventare sbagliata per un dettaglio tecnico, logico o pratico.",
        "fonte_rag": candidate.fonte,
        "stato": "bozza_validata_da_adapter"
    }


def carica_domande_da_json(percorso: Path) -> list[dict[str, Any]]:
    data = json.loads(percorso.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    if isinstance(data, dict):
        for key in ("domande", "questions", "quiz"):
            value = data.get(key)
            if isinstance(value, list):
                return [d for d in value if isinstance(d, dict)]
    raise ValueError(f"Formato JSON non riconosciuto: {percorso}")


def adatta_domande_esistenti(domande: list[dict[str, Any]], categoria: str, sottocategoria: str) -> list[dict[str, Any]]:
    adattate = []
    for i, domanda in enumerate(domande, 1):
        opzioni = domanda.get("opzioni") or domanda.get("options") or []
        risposta = domanda.get("risposta_corretta") or domanda.get("correct_answer") or domanda.get("risposta") or ""
        testo_domanda = domanda.get("domanda") or domanda.get("question") or ""
        spiegazione = domanda.get("spiegazione") or domanda.get("explanation") or ""
        tags = domanda.get("tags") or [categoria, sottocategoria]

        if risposta and isinstance(opzioni, list) and risposta not in opzioni:
            opzioni = [risposta] + [o for o in opzioni if o != risposta]

        while len(opzioni) < 4:
            opzioni.append("Distrattore vicino al tema, ma sbagliato per un dettaglio specifico da revisionare.")

        adattate.append({
            "id": domanda.get("id") or f"RAG-V43-{i:04d}",
            "categoria": domanda.get("categoria") or categoria,
            "sottocategoria": domanda.get("sottocategoria") or sottocategoria,
            "livello": domanda.get("livello") or "medio",
            "domanda": normalizza_spazi(testo_domanda),
            "opzioni": [normalizza_spazi(str(o)) for o in opzioni[:4]],
            "risposta_corretta": normalizza_spazi(str(risposta)),
            "spiegazione": normalizza_spazi(spiegazione),
            "tags": tags if isinstance(tags, list) else [str(tags)],
            "difficolta": domanda.get("difficolta") or 2,
            "distrattore_forte": domanda.get("distrattore_forte") or (opzioni[1] if len(opzioni) > 1 else ""),
            "motivo_distrattore_forte": domanda.get("motivo_distrattore_forte") or "Da verificare con il validatore distrattori forti.",
            "regola_distrattori": domanda.get("regola_distrattori") or "tre_distrattori_forti",
            "criterio_distrattori": domanda.get("criterio_distrattori") or "Ogni risposta errata deve condividere il concetto centrale della corretta e diventare sbagliata per un dettaglio tecnico, logico o pratico.",
            "fonte_rag": domanda.get("fonte_rag") or domanda.get("fonte") or "",
            "stato": "bozza_adattata_da_json_rag"
        })
    return adattate


def valida_struttura_ufficiale(domande: list[dict[str, Any]]) -> list[str]:
    problemi: list[str] = []
    richieste = ["id", "categoria", "sottocategoria", "livello", "domanda", "opzioni", "risposta_corretta", "spiegazione", "tags", "difficolta"]
    for i, domanda in enumerate(domande, 1):
        for chiave in richieste:
            if chiave not in domanda or domanda[chiave] in ("", None, []):
                problemi.append(f"Domanda {i}: manca campo obbligatorio {chiave}.")
        opzioni = domanda.get("opzioni", [])
        if not isinstance(opzioni, list) or len(opzioni) != 4:
            problemi.append(f"Domanda {i}: deve avere esattamente 4 opzioni.")
        if domanda.get("risposta_corretta") not in opzioni:
            problemi.append(f"Domanda {i}: risposta_corretta non presente nelle opzioni.")
        testo = " ".join([str(domanda.get("domanda", "")), str(domanda.get("spiegazione", ""))] + [str(o) for o in opzioni])
        if "þÿ" in testo or "\\n" in testo:
            problemi.append(f"Domanda {i}: contiene simboli corrotti o newline visibili.")
        domanda_bassa = str(domanda.get("domanda", "")).lower()
        if "quale concetto è più collegato" in domanda_bassa:
            problemi.append(f"Domanda {i}: domanda troppo generica.")
        tags = [str(t).lower() for t in domanda.get("tags", [])]
        if any(tag in STOP_CONCETTI for tag in tags):
            problemi.append(f"Domanda {i}: tag/concetto spazzatura: {tags}.")
    return problemi


def valida_linguistica_importata(domande: list[dict[str, Any]]) -> list[str]:
    problemi: list[str] = []
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from qualita_linguistica import controlla_lingua_domanda  # type: ignore
    except Exception as exc:
        return [f"Qualità linguistica non importabile: {exc}"]

    for i, domanda in enumerate(domande, 1):
        esiti = controlla_lingua_domanda(
            domanda.get("domanda", ""),
            domanda.get("opzioni", []),
            domanda.get("spiegazione", "")
        )
        if esiti:
            for esito in esiti:
                problemi.append(f"Domanda {i}: {esito}")
    return problemi


def scrivi_output(domande: list[dict[str, Any]], output: Path, container: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    container.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(domande, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    container.write_text(json.dumps({
        "titolo": "RAG bridge V4.3 - quiz ufficiale",
        "formato": "quiz_ufficiale",
        "domande": domande
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_subprocess(command: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        return result.returncode, (result.stdout + result.stderr).strip()
    except Exception as exc:
        return 999, str(exc)


def esegui_validatori_esterni(output: Path, container: Path) -> list[str]:
    risultati = []
    controlli = [
        ["python3", "scripts/rag_valida_quiz_json.py", str(container)],
        ["python3", "scripts/rag_valida_distrattori_forti.py", str(container)],
        ["python3", "scripts/rag_valida_distrattori_forti.py", str(output)],
    ]
    for command in controlli:
        script = ROOT / command[1]
        if not script.exists():
            risultati.append(f"SKIP: {command[1]} non trovato.")
            continue
        code, text = run_subprocess(command)
        stato = "OK" if code == 0 else "DA RIVEDERE"
        risultati.append(f"{stato}: {' '.join(command)}\n{text[:2500]}")
    return risultati


def scrivi_report(domande: list[dict[str, Any]], problemi: list[str], problemi_lingua: list[str], risultati_esterni: list[str], output: Path) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    righe = [
        "# RAG Adapter Quiz Ufficiale V4.3",
        "",
        f"Output: `{output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}`",
        f"Domande generate/adattate: {len(domande)}",
        "",
        "## Controllo struttura ufficiale",
    ]
    if problemi:
        righe.extend([f"- ERRORE: {p}" for p in problemi])
    else:
        righe.append("- OK: struttura ufficiale valida.")

    righe.extend(["", "## Controllo qualità linguistica"])
    if problemi_lingua:
        righe.extend([f"- AVVISO: {p}" for p in problemi_lingua])
    else:
        righe.append("- OK: nessun problema linguistico rilevato dall'import locale.")

    righe.extend(["", "## Validatori esterni già presenti"])
    for risultato in risultati_esterni:
        righe.append("```text")
        righe.append(risultato)
        righe.append("```")

    righe.extend(["", "## Prossimo passo"])
    righe.append("Collegare questo JSON ufficiale alla UI solo dopo verifica del report.")
    REPORT_PATH.write_text("\n".join(righe) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Adatta output RAG al formato ufficiale dei quiz del progetto.")
    parser.add_argument("--documento", help="Documento TXT/MD da trasformare in quiz ufficiale controllabile.")
    parser.add_argument("--input-json", help="JSON RAG già generato da adattare al formato ufficiale.")
    parser.add_argument("--categoria", default="informatica")
    parser.add_argument("--sottocategoria", default="rag_documenti")
    parser.add_argument("--numero-domande", type=int, default=6)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--container", default=str(DEFAULT_CONTAINER))
    parser.add_argument("--no-validatori-esterni", action="store_true")
    args = parser.parse_args()

    if not args.documento and not args.input_json:
        parser.error("Serve --documento oppure --input-json.")

    if args.input_json:
        input_json = Path(args.input_json)
        if not input_json.is_absolute():
            input_json = ROOT / input_json
        domande_grezze = carica_domande_da_json(input_json)
        domande = adatta_domande_esistenti(domande_grezze, args.categoria, args.sottocategoria)
    else:
        documento = Path(args.documento)
        if not documento.is_absolute():
            documento = ROOT / documento
        testo = documento.read_text(encoding="utf-8")
        candidates = candidate_da_documento(testo, args.numero_domande)
        domande = [
            normalizza_domanda_ufficiale(c, i, args.categoria, args.sottocategoria)
            for i, c in enumerate(candidates, 1)
        ]

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    container = Path(args.container)
    if not container.is_absolute():
        container = ROOT / container

    scrivi_output(domande, output, container)

    problemi = valida_struttura_ufficiale(domande)
    problemi_lingua = valida_linguistica_importata(domande)
    risultati_esterni = [] if args.no_validatori_esterni else esegui_validatori_esterni(output, container)
    scrivi_report(domande, problemi, problemi_lingua, risultati_esterni, output)

    print("=== RAG Adapter Quiz Ufficiale V4.3 ===")
    print(f"Domande: {len(domande)}")
    print(f"Output ufficiale: {output}")
    print(f"Output container: {container}")
    print(f"Report: {REPORT_PATH}")
    if problemi:
        print("ERRORE: struttura non valida")
        for p in problemi:
            print("-", p)
        raise SystemExit(1)
    print("OK: struttura ufficiale valida")
    if problemi_lingua:
        print("AVVISI qualità linguistica:")
        for p in problemi_lingua[:12]:
            print("-", p)
    print("Fine adapter. Controlla il report prima di collegare UI/PDF.")


if __name__ == "__main__":
    main()
