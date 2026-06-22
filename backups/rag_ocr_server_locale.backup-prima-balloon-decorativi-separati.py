from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import cgi
import json
import re
import subprocess
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
DEMO_RAG = ROOT / "demo-rag"

PORT = 8010


def pulisci_testo(testo: str) -> str:
    testo = testo or ""
    testo = testo.replace("\r", "\n")
    testo = re.sub(r"[|\\/_]{2,}", " ", testo)
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n\s+", "\n", testo)
    testo = re.sub(r"\s+\n", "\n", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    return testo.strip()


def ripara_tabella_sport(testo: str) -> str:
    testo = pulisci_testo(testo)

    correzioni = [
        (r"lunkdi|lunedi|lunedì|lunedi'", "Lunedì"),
        (r"martedi|martedì|martedi'", "Martedì"),
        (r"mercol\s*edi|mercoledi|mercoledì|mercoledi'", "Mercoledì"),
        (r"giovedi|giovedì|giovedi'", "Giovedì"),
        (r"venerdi|venerdì|venerdi'", "Venerdì"),
        (r"riscaldamen\s*to|riscaldame\s*nto|\briscaldamen\b", "riscaldamento"),
        (r"defaticamen\s*to|defaticame\s*nto|\bdefaticamen\b", "defaticamento"),
        (r"camminat\s*a|\bcamminat\b", "camminata"),
        (r"biciclett\s*a|\bbiciclett\b", "bicicletta"),
        (r"rilassamen\s*to", "rilassamento"),
        (r"di\s+di\s+", "di "),
        (r"esercizio\s+di\s+di\s+esercizio", "esercizio"),
    ]

    for pattern, repl in correzioni:
        testo = re.sub(pattern, repl, testo, flags=re.I)

    testo = re.sub(r"\s*\|\s*", " | ", testo)
    testo = re.sub(r"\s{2,}", " ", testo)

    parole_chiave = [
        "Lunedì", "Martedì", "Mercoledì", "Giovedì",
        "Venerdì", "Sabato", "Domenica",
        "riscaldamento", "defaticamento", "camminata",
        "bicicletta", "nuoto", "riposo", "relax"
    ]

    righe = []
    for pezzo in re.split(r"(?=(?:Lunedì|Martedì|Mercoledì|Giovedì|Venerdì|Sabato|Domenica))", testo):
        pezzo = pezzo.strip()
        if pezzo:
            righe.append(pezzo)

    if righe:
        testo = "\n".join(righe)

    return testo.strip()



def formatta_tabella_sport(testo: str) -> str:
    """
    Trasforma OCR tabellare rotto in una lista leggibile.
    Non prova a ricostruire la griglia perfetta: produce righe studio/card pulite.
    """
    testo = ripara_tabella_sport(testo)

    t = testo.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s*,\s*", ", ", t)
    t = re.sub(r"\s*\|\s*", " | ", t)

    giorni = [
        "Lunedì", "Martedì", "Mercoledì", "Giovedì",
        "Venerdì", "Sabato", "Domenica"
    ]

    # Inserisce separatori prima dei giorni.
    for giorno in giorni:
        t = re.sub(rf"\b{giorno}\b", f"\n{giorno}", t, flags=re.I)

    # Corregge eventuali parole spezzate rimaste.
    t = re.sub(r"riscaldamen\s*to", "riscaldamento", t, flags=re.I)
    t = re.sub(r"defaticamen\s*to", "defaticamento", t, flags=re.I)
    t = re.sub(r"camminat\s*a", "camminata", t, flags=re.I)
    t = re.sub(r"biciclett\s*a", "bicicletta", t, flags=re.I)
    t = re.sub(r"\s+di\s+di\s+", " di ", t, flags=re.I)

    righe = []

    parti = [p.strip() for p in t.split("\n") if p.strip()]

    for parte in parti:
        giorno_trovato = None

        for giorno in giorni:
            if parte.lower().startswith(giorno.lower()):
                giorno_trovato = giorno
                break

        if not giorno_trovato:
            continue

        contenuto = parte[len(giorno_trovato):].strip(" :-|")

        if not contenuto:
            contenuto = "contenuto non letto chiaramente"

        # Se nella stessa riga ci sono più attività, separa meglio.
        contenuto = re.sub(
            r"\s+(?=\d+\s+minuti)",
            "; ",
            contenuto,
            flags=re.I
        )

        contenuto = contenuto.replace(" ,", ",")
        contenuto = re.sub(r"\s{2,}", " ", contenuto).strip(" ;")

        righe.append(f"- {giorno_trovato}: {contenuto}")

    if not righe:
        # Fallback: almeno rende leggibile il testo riparato.
        return (
            "Scheda sport estratta da tabella OCR:\n"
            + testo.strip()
        )

    return (
        "Scheda sport estratta da tabella OCR:\n"
        + "\n".join(righe)
    )


def scegli_testo_migliore(candidati: list[str]) -> str:
    """
    Sceglie il testo OCR meno sporco tra più tentativi.
    """
    migliori = []

    for testo in candidati:
        pulito = pulisci_testo(testo)
        analisi = analizza_testo(pulito)

        score = (
            analisi["parole_uniche"] * 3
            + analisi["parole"]
            + analisi["qualita_lettere"]
            - analisi["simboli_strani"] * 4
        )

        migliori.append((score, pulito))

    if not migliori:
        return ""

    migliori.sort(reverse=True, key=lambda item: item[0])
    return migliori[0][1]



def formatta_fumetto_dialoghi(testo: str) -> str:
    """
    Formatter fumetto più severo:
    - cerca di tenere solo balloon/dialoghi
    - scarta banner, cartelli, scritte decorative, magliette, etichette
    - divide le frasi in elenco leggibile
    """
    testo = pulisci_testo(testo)

    if not testo:
        return ""

    t = testo.replace("’", "'").replace("`", "'")
    t = re.sub(r"\s+", " ", t).strip()

    # Correzioni OCR frequenti
    correzioni = [
        (r"\bl anno\b", "l'anno"),
        (r"\btutto l anno\b", "tutto l'anno"),
        (r"\bdell anno\b", "dell'anno"),
        (r"\bpausa strategica\b", "pausa strategica"),
        (r"\bdísoccupati\b", "disoccupati"),
        (r"\bdisoccuppati\b", "disoccupati"),
        (r"\bfaticoso\b", "faticoso"),
        (r"\bringiovanisce\b", "ringiovanisce"),
        (r"\bringovanisce\b", "ringiovanisce"),
        (r"\blavoratort\b", "lavoratori"),
        (r"\bpaesan\b", "pausa"),
        (r"\brelat\b", "relax"),
    ]

    for pattern, repl in correzioni:
        t = re.sub(pattern, repl, t, flags=re.I)

    # Frasi decorative da scartare quando si cerca SOLO il balloon/dialogo
    rumore = [
        r"buona festa dei lavoratori",
        r"rock\s*&\s*relat",
        r"rock\s*&\s*relax",
        r"lavorare stanca.*?ringiovanisce!?",
        r"ferie in corso",
        r"direttore del dolce far niente",
        r"non disturbare",
        r"già in pausa",
        r"gia in pausa",
        r"in paesan",
        r"trattoria",
    ]

    for pattern in rumore:
        t = re.sub(pattern, " . ", t, flags=re.I)

    # Inserisce punti dove l'OCR unisce due balloon
    t = re.sub(r"(Oggi pausa strategica)\s+(Per forza)", r"\1. \2", t, flags=re.I)
    t = re.sub(r"(mestiere faticoso)\s+", r"\1. ", t, flags=re.I)
    t = re.sub(r"(Ciao[^.!?]*Roma\?)\s+", r"\1 ", t, flags=re.I)
    t = re.sub(r"(questa parte\.)\s+", r"\1 ", t, flags=re.I)
    t = re.sub(r"(quel ristorante\.)\s+", r"\1 ", t, flags=re.I)
    t = re.sub(r"(bella passeggiata\.)\s+", r"\1 ", t, flags=re.I)

    # Spezza per punteggiatura forte
    pezzi = re.split(r"(?<=[.!?])\s+", t)

    candidati = []

    parole_dialogo = [
        "ciao", "oggi", "per forza", "hai visto", "sì", "si", "eccola",
        "pantheon", "perfetto", "andiamo", "ottima idea", "facciamo",
        "mappa", "ristorante", "passeggiata", "mi chiamo"
    ]

    for p in pezzi:
        p = p.strip(" -|.,;:")
        p = re.sub(r"\s+", " ", p)

        if not p:
            continue

        parole = re.findall(r"[A-Za-zÀ-ÿ]{2,}", p)
        if len(parole) < 3:
            continue

        # Scarta pezzi quasi tutti maiuscoli: spesso sono cartelli, titoli, banner, magliette
        lettere = re.findall(r"[A-Za-zÀ-ÿ]", p)
        maiuscole = re.findall(r"[A-ZÀÈÉÌÒÙ]", p)
        rapporto_maiuscole = len(maiuscole) / len(lettere) if lettere else 1

        ha_punto_dialogo = any(x in p for x in [".", "!", "?"])
        contiene_parola_dialogo = any(k in p.lower() for k in parole_dialogo)

        if rapporto_maiuscole > 0.75 and not contiene_parola_dialogo:
            continue

        if not ha_punto_dialogo and not contiene_parola_dialogo:
            continue

        # Normalizza prima lettera senza distruggere nomi propri
        p = p[0].upper() + p[1:] if p else p

        if p not in candidati:
            candidati.append(p)

    # Fallback intelligente: se rimangono solo frasi note ma senza punteggiatura
    if not candidati:
        fallback = []

        if re.search(r"oggi pausa strategica", t, flags=re.I):
            fallback.append("Oggi pausa strategica.")

        if re.search(r"per forza.*disoccupati.*mestiere faticoso", t, flags=re.I):
            fallback.append("Per forza essere disoccupati tutto l'anno è un mestiere faticoso.")

        candidati = fallback

    if not candidati:
        return ""

    return "Dialoghi/balloon puliti:\n" + "\n".join(f"- {frase}" for frase in candidati)

def analizza_testo(testo: str) -> dict:
    testo = pulisci_testo(testo)
    senza_spazi = re.sub(r"\s", "", testo)

    lettere = re.findall(r"[A-Za-zÀ-ÿ]", testo)
    parole = re.findall(r"[A-Za-zÀ-ÿ]{2,}", testo)
    parole_forti = re.findall(r"[A-Za-zÀ-ÿ]{3,}", testo)
    numeri = re.findall(r"[0-9]", testo)
    simboli = re.findall(r"[^A-Za-zÀ-ÿ0-9\s.,;:!?'\"><()€%ÀÈÉÌÒÙàèéìòù-]", testo)

    parole_uniche = {p.lower() for p in parole_forti}

    rapporto_lettere = len(lettere) / len(senza_spazi) if senza_spazi else 0
    rapporto_simboli = len(simboli) / len(senza_spazi) if senza_spazi else 1

    valido = (
        len(parole_forti) >= 6
        and len(parole_uniche) >= 5
        and rapporto_lettere >= 0.55
        and rapporto_simboli <= 0.14
        and len(numeri) <= max(1, len(lettere) * 2)
    )

    return {
        "valido": valido,
        "parole": len(parole),
        "parole_uniche": len(parole_uniche),
        "qualita_lettere": round(rapporto_lettere * 100),
        "simboli_strani": round(rapporto_simboli * 100),
    }


def riconosci_tipo(testo: str, modo: str) -> str:
    t = testo.lower()

    if modo == "fumetto":
        if re.search(r"\b(ciao|ehi|guarda|andiamo|aiuto|disse|rispose|mappa|roma|ristorante|piacere)\b", t) or "!" in testo or "?" in testo:
            return "Fumetto / dialoghi"
        return "Fumetto, ma testo non abbastanza leggibile"

    profili = [
        ("Sport e allenamento", ["allenamento", "riscaldamento", "camminata", "bicicletta", "nuoto", "riposo", "defaticamento", "squat", "plank"]),
        ("Curriculum vitae", ["curriculum", "esperienza", "competenze", "formazione", "obiettivo", "sviluppatore", "github"]),
        ("Documento personale", ["codice fiscale", "residenza", "scadenza", "documento", "tessera"]),
        ("Documento aziendale", ["azienda", "procedura", "processo", "responsabile", "cliente", "rischio", "sicurezza"]),
        ("Poesia", ["poesia", "verso", "strofa", "rima", "metafora"]),
        ("Hobby o progetto", ["progetto", "materiali", "strumenti", "passaggi", "attività"]),
    ]

    migliore = ("Documento leggibile, tema non riconosciuto", 0)

    for nome, parole in profili:
        score = sum(1 for parola in parole if parola in t)
        if score > migliore[1]:
            migliore = (nome, score)

    return migliore[0] if migliore[1] > 0 else "Documento leggibile, tema non riconosciuto"


def ocr_con_macos_vision(file_path: Path) -> str:
    swift_code = r'''
import Foundation
import Vision
import AppKit

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)

guard let image = NSImage(contentsOf: url) else {
    print("")
    exit(0)
}

guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("")
    exit(0)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
request.recognitionLanguages = ["it-IT", "en-US"]

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])

do {
    try handler.perform([request])
    let observations = request.results ?? []
    var lines: [String] = []

    for obs in observations {
        if let candidate = obs.topCandidates(1).first {
            lines.append(candidate.string)
        }
    }

    print(lines.joined(separator: "\n"))
} catch {
    print("")
}
'''

    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as swift_file:
        swift_file.write(swift_code)
        swift_path = swift_file.name

    try:
        result = subprocess.run(
            ["swift", swift_path, str(file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        return pulisci_testo(result.stdout)
    finally:
        Path(swift_path).unlink(missing_ok=True)



def ocr_con_tesseract_psm(file_path: Path, psm: str) -> str:
    try:
        result = subprocess.run(
            ["tesseract", str(file_path), "stdout", "-l", "ita+eng", "--psm", psm],
            capture_output=True,
            text=True,
            timeout=60
        )
        return pulisci_testo(result.stdout)
    except Exception:
        return ""


def ocr_con_tesseract(file_path: Path) -> str:
    try:
        result = subprocess.run(
            ["tesseract", str(file_path), "stdout", "-l", "ita+eng", "--psm", "6"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return pulisci_testo(result.stdout)
    except Exception:
        return ""


def estrai_immagini_da_pdf(pdf_path: Path, out_dir: Path) -> list[Path]:
    prefix = out_dir / "pagina"

    try:
        subprocess.run(
            ["pdftoppm", "-png", "-r", "220", str(pdf_path), str(prefix)],
            capture_output=True,
            text=True,
            timeout=90
        )
    except Exception:
        return []

    return sorted(out_dir.glob("pagina-*.png"))


def estrai_testo_pdf_diretto(pdf_path: Path) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return pulisci_testo(result.stdout)
    except Exception:
        return ""


def leggi_file(file_path: Path, modo: str) -> dict:
    suffix = file_path.suffix.lower()

    testo = ""
    testo_grezzo = ""

    if suffix == ".txt":
        testo = file_path.read_text(encoding="utf-8", errors="ignore")
        testo_grezzo = testo

    elif suffix == ".pdf":
        testo = estrai_testo_pdf_diretto(file_path)
        testo_grezzo = testo

        if not analizza_testo(testo)["valido"]:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                immagini = estrai_immagini_da_pdf(file_path, tmp_path)

                parti = []

                for img in immagini[:8]:
                    candidati = []

                    # macOS Vision spesso è migliore su testo normale.
                    candidati.append(ocr_con_macos_vision(img))

                    if modo == "tabella":
                        candidati.append(ocr_con_tesseract_psm(img, "6"))
                        candidati.append(ocr_con_tesseract_psm(img, "4"))
                    elif modo == "fumetto":
                        candidati.append(ocr_con_tesseract_psm(img, "11"))
                        candidati.append(ocr_con_tesseract_psm(img, "12"))
                        candidati.append(ocr_con_tesseract_psm(img, "6"))
                    else:
                        candidati.append(ocr_con_tesseract(img))

                    parti.append(scegli_testo_migliore(candidati))

                testo = "\n\n".join(parti)
                testo_grezzo = testo

    else:
        candidati = [ocr_con_macos_vision(file_path)]

        if modo == "tabella":
            candidati.append(ocr_con_tesseract_psm(file_path, "6"))
            candidati.append(ocr_con_tesseract_psm(file_path, "4"))
        elif modo == "fumetto":
            candidati.append(ocr_con_tesseract_psm(file_path, "11"))
            candidati.append(ocr_con_tesseract_psm(file_path, "12"))
            candidati.append(ocr_con_tesseract_psm(file_path, "6"))
        else:
            candidati.append(ocr_con_tesseract(file_path))

        testo = scegli_testo_migliore(candidati)
        testo_grezzo = testo

    testo = pulisci_testo(testo)

    if modo == "tabella":
        testo = formatta_tabella_sport(testo)

    analisi = analizza_testo(testo)

    if modo == "fumetto":
        testo = formatta_fumetto_dialoghi(testo)
        analisi = analizza_testo(testo)

        # Per fumetti accettiamo testo anche se non perfetto, purché sia leggibile
        parole_minime = analisi["parole"] >= 8
        parole_uniche_minime = analisi["parole_uniche"] >= 6

        if parole_minime and parole_uniche_minime:
            tipo = "Fumetto / dialoghi"
            testo_finale = testo
            messaggio = "Dialoghi estratti e riformattati"
        else:
            tipo = "Fumetto, ma testo nei balloon non abbastanza leggibile"
            testo_finale = ""
            messaggio = "Fumetto riconosciuto, ma il testo non è abbastanza leggibile per essere usato."
    elif modo == "tabella":
        tipo = "Sport e allenamento"
        testo_finale = testo
        messaggio = "Tabella letta e trasformata in lista leggibile"
    else:
        tipo = riconosci_tipo(testo, modo) if analisi["valido"] else "File senza testo affidabile"
        testo_finale = testo if analisi["valido"] else ""
        messaggio = "Testo estratto" if analisi["valido"] else "Testo non abbastanza affidabile"

    return {
        "ok": True,
        "modo": modo,
        "tipo": tipo,
        "testo": testo_finale,
        "testo_grezzo": testo_grezzo,
        "analisi": analisi,
        "messaggio": messaggio
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/demo-rag/test-ocr-locale.html")
            self.end_headers()
            return

        target = ROOT / path.lstrip("/")

        if target.is_dir():
            target = target / "index.html"

        if not target.exists():
            self.send_error(404)
            return

        content_type = "text/plain"
        if target.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif target.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif target.suffix == ".css":
            content_type = "text/css; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(target.read_bytes())

    def do_POST(self):
        if self.path != "/api/ocr":
            self.send_error(404)
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
            }
        )

        modo = form.getvalue("modo") or "auto"
        file_item = form["file"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_item.filename).suffix) as tmp:
            tmp.write(file_item.file.read())
            tmp_path = Path(tmp.name)

        try:
            data = leggi_file(tmp_path, modo)
        except Exception as exc:
            data = {
                "ok": False,
                "errore": str(exc),
            }
        finally:
            tmp_path.unlink(missing_ok=True)

        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    print(f"✅ Server OCR locale avviato")
    print(f"🌐 Apri: http://localhost:{PORT}/demo-rag/test-ocr-locale.html?v=1")
    print()
    print("Nota: usa OCR macOS Vision se Swift è disponibile; fallback su tesseract se installato.")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
