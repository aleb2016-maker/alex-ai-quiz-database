import json
from pathlib import Path


JSON_FILE = Path("data/logica/logica_visiva.json")
ASSET_DIR = Path("assets/logica_visiva")
ID_DOMANDA = "LOG-VIS-AV-0004"


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(dati, file, ensure_ascii=False, indent=2)


def trova_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "items", "data"]:
            if isinstance(dati.get(chiave), list):
                return dati[chiave]

    raise ValueError("Lista domande non trovata.")


def colore_svg(nome_colore):
    if nome_colore == "blu":
        return "#2563eb"

    if nome_colore == "rosso":
        return "#ef4444"

    return "#111827"


def linee_interne_triangolo(numero_linee):
    if numero_linee == 1:
        ys = [150]
    elif numero_linee == 2:
        ys = [135, 175]
    else:
        ys = [120, 155, 190]

    linee = []

    for y in ys:
        t = (y - 65) / (220 - 65)
        sinistra = 150 + (80 - 150) * t + 14
        destra = 150 + (220 - 150) * t - 14

        linee.append(
            f'<line x1="{sinistra:.1f}" y1="{y}" '
            f'x2="{destra:.1f}" y2="{y}" '
            f'stroke="CURRENT_COLOR" stroke-width="8" '
            f'stroke-linecap="round"/>'
        )

    return "\n".join(linee)


def linee_interne_quadrato(numero_linee):
    if numero_linee == 1:
        ys = [150]
    elif numero_linee == 2:
        ys = [135, 165]
    else:
        ys = [120, 150, 180]

    return "\n".join(
        f'<line x1="105" y1="{y}" x2="195" y2="{y}" '
        f'stroke="CURRENT_COLOR" stroke-width="8" '
        f'stroke-linecap="round"/>'
        for y in ys
    )


def disegna_figura(tipo_figura, colore, numero_linee):
    colore_esatto = colore_svg(colore)

    if tipo_figura == "triangolo":
        corpo = f'''
<polygon points="150,65 80,220 220,220"
         fill="none"
         stroke="CURRENT_COLOR"
         stroke-width="8"
         stroke-linejoin="round"/>
{linee_interne_triangolo(numero_linee)}
'''

    elif tipo_figura == "quadrato":
        corpo = f'''
<rect x="85" y="85" width="130" height="130" rx="14"
      fill="none"
      stroke="CURRENT_COLOR"
      stroke-width="8"/>
{linee_interne_quadrato(numero_linee)}
'''

    elif tipo_figura == "cerchio":
        ys = [150] if numero_linee == 1 else [135, 165] if numero_linee == 2 else [120, 150, 180]

        linee = "\n".join(
            f'<line x1="105" y1="{y}" x2="195" y2="{y}" '
            f'stroke="CURRENT_COLOR" stroke-width="8" stroke-linecap="round"/>'
            for y in ys
        )

        corpo = f'''
<circle cx="150" cy="150" r="70"
        fill="none"
        stroke="CURRENT_COLOR"
        stroke-width="8"/>
{linee}
'''

    else:
        raise ValueError(f"Figura non gestita: {tipo_figura}")

    return corpo.replace("CURRENT_COLOR", colore_esatto)


def crea_svg_opzione(tipo_figura, colore, numero_linee):
    corpo = disegna_figura(tipo_figura, colore, numero_linee)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300">
  <rect x="22" y="22" width="256" height="256" rx="34" fill="#ffffff" stroke="#d1d5db" stroke-width="4"/>
  <rect x="38" y="38" width="224" height="224" rx="26" fill="#ffffff" stroke="#e5e7eb" stroke-width="3"/>
  {corpo}
</svg>
'''


def crea_svg_domanda():
    celle = [
        ("cerchio", "blu", 1),
        ("cerchio", "rosso", 2),
        ("cerchio", "blu", 3),
        ("quadrato", "rosso", 1),
        ("quadrato", "blu", 2),
        ("quadrato", "rosso", 3),
        ("triangolo", "blu", 1),
        ("triangolo", "rosso", 2),
        ("mancante", "grigio", 0),
    ]

    blocchi = []

    for indice, (figura, colore, linee) in enumerate(celle):
        colonna = indice % 3
        riga = indice // 3

        x = 90 + colonna * 150
        y = 70 + riga * 150

        if figura == "mancante":
            contenuto = '''
<rect x="35" y="35" width="80" height="80" rx="12"
      fill="#ffffff"
      stroke="#8b8b8b"
      stroke-width="4"
      stroke-dasharray="10 8"/>
<text x="75" y="91"
      font-size="58"
      text-anchor="middle"
      fill="#666666"
      font-family="Arial, sans-serif">?</text>
'''
        else:
            contenuto = disegna_figura(figura, colore, linee)
            contenuto = contenuto.replace("150", "75")
            contenuto = contenuto.replace("220", "110")
            contenuto = contenuto.replace("80", "40")
            contenuto = contenuto.replace("65", "32")
            contenuto = contenuto.replace("85", "38")
            contenuto = contenuto.replace("130", "74")
            contenuto = contenuto.replace("105", "48")
            contenuto = contenuto.replace("195", "102")
            contenuto = contenuto.replace("120", "58")
            contenuto = contenuto.replace("135", "66")
            contenuto = contenuto.replace("165", "84")
            contenuto = contenuto.replace("175", "91")
            contenuto = contenuto.replace("190", "98")
            contenuto = contenuto.replace("70", "38")

        blocchi.append(
            f'''
<g transform="translate({x},{y})">
  <rect x="0" y="0" width="150" height="150" fill="#ffffff" stroke="#d8d8d8" stroke-width="2"/>
  {contenuto}
</g>
'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="520" viewBox="0 0 760 520">
  <rect x="0" y="0" width="760" height="520" rx="34" fill="#ffffff"/>
  <rect x="90" y="70" width="450" height="450" fill="#ffffff" stroke="#d8d8d8" stroke-width="2"/>
  {''.join(blocchi)}
</svg>
'''


def aggiorna_json():
    dati = carica_json(JSON_FILE)
    domande = trova_lista_domande(dati)

    domanda_trovata = None

    for domanda in domande:
        if domanda.get("id") == ID_DOMANDA:
            domanda_trovata = domanda
            break

    if domanda_trovata is None:
        raise ValueError(f"Domanda non trovata: {ID_DOMANDA}")

    domanda_trovata["domanda"] = (
        "Osserva la matrice visiva. Quale casella completa correttamente lo schema?"
    )

    domanda_trovata["opzioni"] = ["A", "B", "C", "D"]
    domanda_trovata["risposta_corretta"] = "A"

    domanda_trovata["immagine_domanda"] = (
        "assets/logica_visiva/LOG-VIS-AV-0004_domanda.svg"
    )

    domanda_trovata["immagini_opzioni"] = {
        "A": "assets/logica_visiva/LOG-VIS-AV-0004_opzione_A.svg",
        "B": "assets/logica_visiva/LOG-VIS-AV-0004_opzione_B.svg",
        "C": "assets/logica_visiva/LOG-VIS-AV-0004_opzione_C.svg",
        "D": "assets/logica_visiva/LOG-VIS-AV-0004_opzione_D.svg",
    }

    domanda_trovata["spiegazione"] = (
        "Le righe determinano la forma: cerchio, quadrato, triangolo. "
        "Le colonne determinano il numero di linee interne: una, due, tre. "
        "Il colore alterna blu, rosso, blu. "
        "Serve quindi un triangolo blu con tre linee interne."
    )

    domanda_trovata["distrattore_forte"] = "B"
    domanda_trovata["motivo_distrattore_forte"] = (
        "B mantiene forma e numero di linee interne corretti, ma sbaglia il colore."
    )

    salva_json(JSON_FILE, dati)


def aggiorna_svg():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    (ASSET_DIR / "LOG-VIS-AV-0004_domanda.svg").write_text(
        crea_svg_domanda(),
        encoding="utf-8",
    )

    (ASSET_DIR / "LOG-VIS-AV-0004_opzione_A.svg").write_text(
        crea_svg_opzione("triangolo", "blu", 3),
        encoding="utf-8",
    )

    (ASSET_DIR / "LOG-VIS-AV-0004_opzione_B.svg").write_text(
        crea_svg_opzione("triangolo", "rosso", 3),
        encoding="utf-8",
    )

    (ASSET_DIR / "LOG-VIS-AV-0004_opzione_C.svg").write_text(
        crea_svg_opzione("triangolo", "blu", 2),
        encoding="utf-8",
    )

    (ASSET_DIR / "LOG-VIS-AV-0004_opzione_D.svg").write_text(
        crea_svg_opzione("quadrato", "blu", 3),
        encoding="utf-8",
    )


def main():
    aggiorna_json()
    aggiorna_svg()

    print("----- CORREZIONE LOG-VIS-AV-0004 COMPLETATA -----")
    print("Domanda resa neutra: non anticipa più la regola.")
    print("Risposta A corretta: triangolo blu con 3 linee interne.")
    print("Spiegazione aggiornata con forma, linee e alternanza colore.")


main()
