from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


CARTELLA_OUTPUT = Path("assets/logica_visiva")
CARTELLA_OUTPUT.mkdir(parents=True, exist_ok=True)


LARGHEZZA_DOMANDA = 900
ALTEZZA_DOMANDA = 420

LARGHEZZA_OPZIONE = 420
ALTEZZA_OPZIONE = 300


def crea_immagine(larghezza, altezza):
    immagine = Image.new("RGB", (larghezza, altezza), "white")
    disegno = ImageDraw.Draw(immagine)
    return immagine, disegno


def font_base(dimensione):
    try:
        return ImageFont.truetype("Arial.ttf", dimensione)
    except:
        return ImageFont.load_default()


def salva(immagine, nome_file):
    percorso = CARTELLA_OUTPUT / nome_file
    immagine.save(percorso)
    print(f"Creata immagine: {percorso}")


def disegna_titolo(disegno, testo):
    font = font_base(24)
    disegno.text((30, 25), testo, fill="black", font=font)


def disegna_cerchio(disegno, x, y, grandezza, pieno=False):
    colore = "black" if pieno else "white"
    disegno.ellipse(
        (x, y, x + grandezza, y + grandezza),
        outline="black",
        fill=colore,
        width=4
    )


def disegna_quadrato(disegno, x, y, grandezza, pieno=False):
    colore = "black" if pieno else "white"
    disegno.rectangle(
        (x, y, x + grandezza, y + grandezza),
        outline="black",
        fill=colore,
        width=4
    )


def disegna_rettangolo(disegno, x, y, larghezza, altezza):
    disegno.rectangle(
        (x, y, x + larghezza, y + altezza),
        outline="black",
        fill="white",
        width=4
    )


def disegna_triangolo(disegno, x, y, grandezza, pieno=False):
    punti = [
        (x + grandezza // 2, y),
        (x, y + grandezza),
        (x + grandezza, y + grandezza)
    ]

    colore = "black" if pieno else "white"

    disegno.polygon(punti, outline="black", fill=colore)
    disegno.line(
        punti + [punti[0]],
        fill="black",
        width=4
    )


def disegna_mezzo_pieno_quadrato(disegno, x, y, grandezza):
    disegno.rectangle(
        (x, y, x + grandezza, y + grandezza),
        outline="black",
        fill="white",
        width=4
    )

    disegno.rectangle(
        (x, y + grandezza // 2, x + grandezza, y + grandezza),
        fill="black"
    )

    disegno.rectangle(
        (x, y, x + grandezza, y + grandezza),
        outline="black",
        width=4
    )


def disegna_mezzo_pieno_cerchio(disegno, x, y, grandezza):
    disegna_cerchio(disegno, x, y, grandezza, pieno=False)

    disegno.pieslice(
        (x, y, x + grandezza, y + grandezza),
        0,
        180,
        fill="black"
    )

    disegno.ellipse(
        (x, y, x + grandezza, y + grandezza),
        outline="black",
        width=4
    )


def disegna_mezzo_pieno_triangolo(disegno, x, y, grandezza):
    disegna_triangolo(disegno, x, y, grandezza, pieno=False)

    punti_neri = [
        (x + grandezza // 4, y + grandezza // 2),
        (x + grandezza * 3 // 4, y + grandezza // 2),
        (x + grandezza, y + grandezza),
        (x, y + grandezza)
    ]

    disegno.polygon(punti_neri, fill="black")

    punti_bordo = [
        (x + grandezza // 2, y),
        (x, y + grandezza),
        (x + grandezza, y + grandezza),
        (x + grandezza // 2, y)
    ]

    disegno.line(punti_bordo, fill="black", width=4)


def disegna_freccia(disegno, x, y, direzione):
    centro_x = x
    centro_y = y
    lunghezza = 90

    if direzione == "su":
        fine = (centro_x, centro_y - lunghezza)
        ali = [(centro_x - 25, centro_y - lunghezza + 30),
               (centro_x + 25, centro_y - lunghezza + 30)]
    elif direzione == "giu":
        fine = (centro_x, centro_y + lunghezza)
        ali = [(centro_x - 25, centro_y + lunghezza - 30),
               (centro_x + 25, centro_y + lunghezza - 30)]
    elif direzione == "destra":
        fine = (centro_x + lunghezza, centro_y)
        ali = [(centro_x + lunghezza - 30, centro_y - 25),
               (centro_x + lunghezza - 30, centro_y + 25)]
    else:
        fine = (centro_x - lunghezza, centro_y)
        ali = [(centro_x - lunghezza + 30, centro_y - 25),
               (centro_x - lunghezza + 30, centro_y + 25)]

    disegno.line((centro_x, centro_y, fine[0], fine[1]), fill="black", width=8)
    disegno.line((fine[0], fine[1], ali[0][0], ali[0][1]), fill="black", width=8)
    disegno.line((fine[0], fine[1], ali[1][0], ali[1][1]), fill="black", width=8)


def crea_log_vis_fac_0001():
    immagine, disegno = crea_immagine(LARGHEZZA_DOMANDA, ALTEZZA_DOMANDA)
    disegna_titolo(disegno, "Completa la sequenza")
    disegna_cerchio(disegno, 90, 160, 90)
    disegna_quadrato(disegno, 250, 160, 90)
    disegna_cerchio(disegno, 410, 160, 90)
    disegna_quadrato(disegno, 570, 160, 90)

    font = font_base(80)
    disegno.text((750, 155), "?", fill="black", font=font)

    salva(immagine, "log_vis_fac_0001_domanda.png")

    opzioni = [
        ("A", "triangolo"),
        ("B", "quadrato"),
        ("C", "cerchio"),
        ("D", "rettangolo"),
    ]

    for lettera, forma in opzioni:
        immagine, disegno = crea_immagine(LARGHEZZA_OPZIONE, ALTEZZA_OPZIONE)
        disegna_titolo(disegno, f"Opzione {lettera}")

        if forma == "triangolo":
            disegna_triangolo(disegno, 150, 110, 100)
        elif forma == "quadrato":
            disegna_quadrato(disegno, 150, 110, 100)
        elif forma == "cerchio":
            disegna_cerchio(disegno, 150, 110, 100)
        else:
            disegna_rettangolo(disegno, 125, 120, 150, 80)

        salva(immagine, f"log_vis_fac_0001_{lettera}.png")


def crea_log_vis_int_0002():
    immagine, disegno = crea_immagine(LARGHEZZA_DOMANDA, ALTEZZA_DOMANDA)
    disegna_titolo(disegno, "Completa la rotazione della freccia")

    disegna_freccia(disegno, 160, 230, "su")
    disegna_freccia(disegno, 350, 230, "destra")
    disegna_freccia(disegno, 540, 230, "giu")

    font = font_base(80)
    disegno.text((740, 170), "?", fill="black", font=font)

    salva(immagine, "log_vis_int_0002_domanda.png")

    opzioni = [
        ("A", "su"),
        ("B", "sinistra"),
        ("C", "destra"),
        ("D", "giu"),
    ]

    for lettera, direzione in opzioni:
        immagine, disegno = crea_immagine(LARGHEZZA_OPZIONE, ALTEZZA_OPZIONE)
        disegna_titolo(disegno, f"Opzione {lettera}")
        disegna_freccia(disegno, 210, 180, direzione)
        salva(immagine, f"log_vis_int_0002_{lettera}.png")


def crea_log_vis_av_0003():
    immagine, disegno = crea_immagine(LARGHEZZA_DOMANDA, ALTEZZA_DOMANDA)
    disegna_titolo(disegno, "Completa la matrice visiva")

    dimensione = 70
    x_inizio = 190
    y_inizio = 90
    spazio_x = 180
    spazio_y = 100

    # Riga 1: cerchi
    disegna_cerchio(disegno, x_inizio, y_inizio, dimensione, pieno=False)
    disegna_mezzo_pieno_cerchio(disegno, x_inizio + spazio_x, y_inizio, dimensione)
    disegna_cerchio(disegno, x_inizio + spazio_x * 2, y_inizio, dimensione, pieno=True)

    # Riga 2: quadrati
    disegna_quadrato(disegno, x_inizio, y_inizio + spazio_y, dimensione, pieno=False)
    disegna_mezzo_pieno_quadrato(disegno, x_inizio + spazio_x, y_inizio + spazio_y, dimensione)
    disegna_quadrato(disegno, x_inizio + spazio_x * 2, y_inizio + spazio_y, dimensione, pieno=True)

    # Riga 3: triangoli
    disegna_triangolo(disegno, x_inizio, y_inizio + spazio_y * 2, dimensione, pieno=False)
    disegna_mezzo_pieno_triangolo(disegno, x_inizio + spazio_x, y_inizio + spazio_y * 2, dimensione)

    font = font_base(60)
    disegno.text(
        (x_inizio + spazio_x * 2 + 20, y_inizio + spazio_y * 2),
        "?",
        fill="black",
        font=font
    )

    salva(immagine, "log_vis_av_0003_domanda.png")

    opzioni = [
        ("A", "triangolo_vuoto"),
        ("B", "quadrato_pieno"),
        ("C", "triangolo_mezzo"),
        ("D", "triangolo_pieno"),
    ]

    for lettera, forma in opzioni:
        immagine, disegno = crea_immagine(LARGHEZZA_OPZIONE, ALTEZZA_OPZIONE)
        disegna_titolo(disegno, f"Opzione {lettera}")

        if forma == "triangolo_vuoto":
            disegna_triangolo(disegno, 150, 105, 110, pieno=False)
        elif forma == "quadrato_pieno":
            disegna_quadrato(disegno, 155, 110, 100, pieno=True)
        elif forma == "triangolo_mezzo":
            disegna_mezzo_pieno_triangolo(disegno, 150, 105, 110)
        else:
            disegna_triangolo(disegno, 150, 105, 110, pieno=True)

        salva(immagine, f"log_vis_av_0003_{lettera}.png")


def main():
    print("----- GENERAZIONE IMMAGINI LOGICA VISIVA -----")

    crea_log_vis_fac_0001()
    crea_log_vis_int_0002()
    crea_log_vis_av_0003()

    print("\nImmagini create correttamente.")


main()