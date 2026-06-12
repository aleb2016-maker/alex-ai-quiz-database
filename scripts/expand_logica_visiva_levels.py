import json
from pathlib import Path


DATA_FILE = Path("data/logica/logica_visiva.json")
ASSET_DIR = Path("assets/logica_visiva")
BACKUP_FILE = Path("data/logica/logica_visiva.backup.json")


COLORI = {
    "blu": "#1f5fd1",
    "rosso": "#e63935",
    "verde": "#188038",
    "viola": "#6d35d9",
    "oro": "#b8860b",
    "nero": "#111111",
    "grigio": "#777777",
}


NUOVE_DOMANDE = [
    # =========================================================
    # FACILE
    # =========================================================
    {
        "id": "LOG-VIS-FAC-0004",
        "livello": "facile",
        "tipo_visuale": "sequenza_forme",
        "domanda": "Osserva la sequenza visiva. Quale figura completa correttamente il pattern?",
        "risposta_corretta": "A",
        "spiegazione": (
            "La sequenza alterna cerchio e quadrato, mentre il colore alterna blu e rosso. "
            "Dopo il quadrato rosso deve tornare il cerchio blu."
        ),
        "sequenza": [
            {"shape": "circle", "color": "blu", "count": 1},
            {"shape": "square", "color": "rosso", "count": 1},
            {"shape": "circle", "color": "blu", "count": 2},
            {"shape": "square", "color": "rosso", "count": 2},
            None,
        ],
        "opzioni_visuali": {
            "A": {"shape": "circle", "color": "blu", "count": 3},
            "B": {"shape": "square", "color": "blu", "count": 3},
            "C": {"shape": "circle", "color": "rosso", "count": 3},
            "D": {"shape": "square", "color": "rosso", "count": 2},
        },
    },
    {
        "id": "LOG-VIS-FAC-0005",
        "livello": "facile",
        "tipo_visuale": "rotazione_freccia",
        "domanda": "Osserva la rotazione delle frecce. Quale figura viene dopo?",
        "risposta_corretta": "D",
        "spiegazione": (
            "La freccia ruota ogni volta di 90 gradi in senso orario: alto, destra, basso, sinistra."
        ),
        "sequenza": [
            {"shape": "arrow", "color": "verde", "direction": "up", "count": 1},
            {"shape": "arrow", "color": "verde", "direction": "right", "count": 1},
            {"shape": "arrow", "color": "verde", "direction": "down", "count": 1},
            None,
        ],
        "opzioni_visuali": {
            "A": {"shape": "arrow", "color": "verde", "direction": "up", "count": 1},
            "B": {"shape": "arrow", "color": "verde", "direction": "right", "count": 1},
            "C": {"shape": "arrow", "color": "verde", "direction": "down", "count": 1},
            "D": {"shape": "arrow", "color": "verde", "direction": "left", "count": 1},
        },
    },
    {
        "id": "LOG-VIS-FAC-0006",
        "livello": "facile",
        "tipo_visuale": "punti_crescenti",
        "domanda": "Osserva il numero di punti interni. Quale figura completa la sequenza?",
        "risposta_corretta": "C",
        "spiegazione": (
            "Il numero di punti aumenta di uno a ogni passaggio: 1, 2, 3, quindi 4."
        ),
        "sequenza": [
            {"shape": "triangle", "color": "blu", "count": 1},
            {"shape": "triangle", "color": "blu", "count": 2},
            {"shape": "triangle", "color": "blu", "count": 3},
            None,
        ],
        "opzioni_visuali": {
            "A": {"shape": "triangle", "color": "blu", "count": 2},
            "B": {"shape": "triangle", "color": "rosso", "count": 4},
            "C": {"shape": "triangle", "color": "blu", "count": 4},
            "D": {"shape": "square", "color": "blu", "count": 4},
        },
    },
    {
        "id": "LOG-VIS-FAC-0007",
        "livello": "facile",
        "tipo_visuale": "colore_alternato",
        "domanda": "Osserva colore e forma. Quale opzione completa correttamente la sequenza?",
        "risposta_corretta": "B",
        "spiegazione": (
            "La forma resta un esagono, mentre il colore alterna oro e viola. "
            "Dopo oro, viola, oro, deve venire viola."
        ),
        "sequenza": [
            {"shape": "hexagon", "color": "oro", "count": 1},
            {"shape": "hexagon", "color": "viola", "count": 1},
            {"shape": "hexagon", "color": "oro", "count": 1},
            None,
        ],
        "opzioni_visuali": {
            "A": {"shape": "hexagon", "color": "oro", "count": 1},
            "B": {"shape": "hexagon", "color": "viola", "count": 1},
            "C": {"shape": "circle", "color": "viola", "count": 1},
            "D": {"shape": "square", "color": "oro", "count": 1},
        },
    },
    {
        "id": "LOG-VIS-FAC-0008",
        "livello": "facile",
        "tipo_visuale": "matrice_semplice",
        "domanda": "Osserva la matrice. Quale figura completa la casella mancante?",
        "risposta_corretta": "A",
        "spiegazione": (
            "Ogni riga mantiene la stessa forma esterna. Nella terza riga ci sono triangoli. "
            "La terza colonna contiene tre punti, quindi serve un triangolo con tre punti."
        ),
        "matrice": [
            [
                {"shape": "circle", "color": "blu", "count": 1},
                {"shape": "circle", "color": "blu", "count": 2},
                {"shape": "circle", "color": "blu", "count": 3},
            ],
            [
                {"shape": "square", "color": "rosso", "count": 1},
                {"shape": "square", "color": "rosso", "count": 2},
                {"shape": "square", "color": "rosso", "count": 3},
            ],
            [
                {"shape": "triangle", "color": "verde", "count": 1},
                {"shape": "triangle", "color": "verde", "count": 2},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "triangle", "color": "verde", "count": 3},
            "B": {"shape": "triangle", "color": "verde", "count": 2},
            "C": {"shape": "circle", "color": "verde", "count": 3},
            "D": {"shape": "square", "color": "verde", "count": 3},
        },
    },

    # =========================================================
    # INTERMEDIO
    # =========================================================
    {
        "id": "LOG-VIS-INT-0004",
        "livello": "intermedio",
        "tipo_visuale": "sequenza_doppia_regola",
        "domanda": "Osserva la sequenza. Quale figura continua correttamente il pattern?",
        "risposta_corretta": "A",
        "spiegazione": (
            "La figura esterna aumenta i lati: triangolo, quadrato, pentagono, quindi esagono. "
            "Gli elementi interni aumentano di uno: 1, 2, 3, quindi 4."
        ),
        "sequenza": [
            {"shape": "triangle", "color": "blu", "inner": "triangle", "inner_count": 1},
            {"shape": "square", "color": "rosso", "inner": "triangle", "inner_count": 2},
            {"shape": "pentagon", "color": "blu", "inner": "triangle", "inner_count": 3},
            None,
        ],
        "opzioni_visuali": {
            "A": {"shape": "hexagon", "color": "blu", "inner": "triangle", "inner_count": 4},
            "B": {"shape": "hexagon", "color": "rosso", "inner": "triangle", "inner_count": 3},
            "C": {"shape": "pentagon", "color": "blu", "inner": "triangle", "inner_count": 4},
            "D": {"shape": "heptagon", "color": "blu", "inner": "triangle", "inner_count": 4},
        },
    },
    {
        "id": "LOG-VIS-INT-0005",
        "livello": "intermedio",
        "tipo_visuale": "matrice_colore_forma",
        "domanda": "Osserva forma, colore e numero di punti. Quale figura completa la matrice?",
        "risposta_corretta": "B",
        "spiegazione": (
            "La terza riga deve mantenere la forma triangolo. La terza colonna richiede tre punti. "
            "Il colore segue l'alternanza verde, blu, verde."
        ),
        "matrice": [
            [
                {"shape": "circle", "color": "verde", "count": 1},
                {"shape": "circle", "color": "blu", "count": 2},
                {"shape": "circle", "color": "verde", "count": 3},
            ],
            [
                {"shape": "square", "color": "blu", "count": 1},
                {"shape": "square", "color": "verde", "count": 2},
                {"shape": "square", "color": "blu", "count": 3},
            ],
            [
                {"shape": "triangle", "color": "verde", "count": 1},
                {"shape": "triangle", "color": "blu", "count": 2},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "triangle", "color": "blu", "count": 3},
            "B": {"shape": "triangle", "color": "verde", "count": 3},
            "C": {"shape": "square", "color": "verde", "count": 3},
            "D": {"shape": "triangle", "color": "verde", "count": 2},
        },
    },
    {
        "id": "LOG-VIS-INT-0006",
        "livello": "intermedio",
        "tipo_visuale": "trasformazione_2x2",
        "domanda": "Osserva la trasformazione. Quale figura completa correttamente la matrice?",
        "risposta_corretta": "A",
        "spiegazione": (
            "Da sinistra a destra la diagonale cambia verso e i punti aumentano da uno a due. "
            "La stessa trasformazione va applicata anche al cerchio rosso."
        ),
        "matrice": [
            [
                {"shape": "square", "color": "blu", "diagonal": "/", "count": 1},
                {"shape": "square", "color": "blu", "diagonal": "\\", "count": 2},
            ],
            [
                {"shape": "circle", "color": "rosso", "diagonal": "/", "count": 1},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "circle", "color": "rosso", "diagonal": "\\", "count": 2},
            "B": {"shape": "circle", "color": "blu", "diagonal": "\\", "count": 2},
            "C": {"shape": "circle", "color": "rosso", "diagonal": "/", "count": 2},
            "D": {"shape": "circle", "color": "rosso", "diagonal": "\\", "count": 1},
        },
    },
    {
        "id": "LOG-VIS-INT-0007",
        "livello": "intermedio",
        "tipo_visuale": "rotazione_con_punti",
        "domanda": "Osserva direzione, colore e numero di punti. Quale freccia completa la sequenza?",
        "risposta_corretta": "C",
        "spiegazione": (
            "La freccia ruota di 90 gradi in senso orario e il numero di punti aumenta. "
            "Dopo alto, destra, basso, deve venire sinistra con quattro punti."
        ),
        "sequenza": [
            {"shape": "arrow", "color": "blu", "direction": "up", "count": 1},
            {"shape": "arrow", "color": "rosso", "direction": "right", "count": 2},
            {"shape": "arrow", "color": "blu", "direction": "down", "count": 3},
            None,
        ],
        "opzioni_visuali": {
            "A": {"shape": "arrow", "color": "blu", "direction": "left", "count": 4},
            "B": {"shape": "arrow", "color": "rosso", "direction": "down", "count": 4},
            "C": {"shape": "arrow", "color": "rosso", "direction": "left", "count": 4},
            "D": {"shape": "arrow", "color": "rosso", "direction": "left", "count": 3},
        },
    },
    {
        "id": "LOG-VIS-INT-0008",
        "livello": "intermedio",
        "tipo_visuale": "specchio_semplice",
        "domanda": "Quale figura rappresenta l'immagine speculare rispetto alla figura data?",
        "risposta_corretta": "D",
        "spiegazione": (
            "La figura va riflessa rispetto all'asse verticale: gli elementi a sinistra passano a destra "
            "e quelli a destra passano a sinistra."
        ),
        "figura_specchio": {"color": "viola", "variant": "original"},
        "opzioni_visuali": {
            "A": {"shape": "mirror", "color": "viola", "variant": "same"},
            "B": {"shape": "mirror", "color": "viola", "variant": "rotated"},
            "C": {"shape": "mirror", "color": "viola", "variant": "wrong_dot"},
            "D": {"shape": "mirror", "color": "viola", "variant": "correct"},
        },
    },

    # =========================================================
    # AVANZATO
    # =========================================================
    {
        "id": "LOG-VIS-AV-0004",
        "livello": "avanzato",
        "tipo_visuale": "matrice_tre_regole",
        "domanda": "La matrice combina forma, colore e numero di linee. Quale figura manca?",
        "risposta_corretta": "A",
        "spiegazione": (
            "Le righe determinano la forma: cerchio, quadrato, triangolo. "
            "Le colonne determinano il numero di linee: una, due, tre. "
            "Il colore alterna blu, rosso, blu. Serve quindi un triangolo blu con tre linee."
        ),
        "matrice": [
            [
                {"shape": "circle", "color": "blu", "lines": 1},
                {"shape": "circle", "color": "rosso", "lines": 2},
                {"shape": "circle", "color": "blu", "lines": 3},
            ],
            [
                {"shape": "square", "color": "rosso", "lines": 1},
                {"shape": "square", "color": "blu", "lines": 2},
                {"shape": "square", "color": "rosso", "lines": 3},
            ],
            [
                {"shape": "triangle", "color": "blu", "lines": 1},
                {"shape": "triangle", "color": "rosso", "lines": 2},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "triangle", "color": "blu", "lines": 3},
            "B": {"shape": "triangle", "color": "rosso", "lines": 3},
            "C": {"shape": "triangle", "color": "blu", "lines": 2},
            "D": {"shape": "square", "color": "blu", "lines": 3},
        },
    },
    {
        "id": "LOG-VIS-AV-0005",
        "livello": "avanzato",
        "tipo_visuale": "nested_pattern",
        "domanda": "Osserva profondità dei contorni e riempimento interno. Quale figura completa la matrice?",
        "risposta_corretta": "C",
        "spiegazione": (
            "Scendendo nelle righe aumenta il numero di contorni esterni. "
            "Le colonne cambiano il riempimento interno: pieno, righe, puntini. "
            "Serve quindi un esagono con tre contorni e puntini."
        ),
        "matrice": [
            [
                {"shape": "hexagon", "color": "nero", "nested": 1, "pattern": "solid"},
                {"shape": "hexagon", "color": "nero", "nested": 1, "pattern": "stripes"},
                {"shape": "hexagon", "color": "nero", "nested": 1, "pattern": "dots"},
            ],
            [
                {"shape": "hexagon", "color": "nero", "nested": 2, "pattern": "solid"},
                {"shape": "hexagon", "color": "nero", "nested": 2, "pattern": "stripes"},
                {"shape": "hexagon", "color": "nero", "nested": 2, "pattern": "dots"},
            ],
            [
                {"shape": "hexagon", "color": "nero", "nested": 3, "pattern": "solid"},
                {"shape": "hexagon", "color": "nero", "nested": 3, "pattern": "stripes"},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "hexagon", "color": "nero", "nested": 2, "pattern": "dots"},
            "B": {"shape": "hexagon", "color": "nero", "nested": 3, "pattern": "cross"},
            "C": {"shape": "hexagon", "color": "nero", "nested": 3, "pattern": "dots"},
            "D": {"shape": "hexagon", "color": "nero", "nested": 3, "pattern": "solid"},
        },
    },
    {
        "id": "LOG-VIS-AV-0006",
        "livello": "avanzato",
        "tipo_visuale": "analogia_visuale",
        "domanda": "Osserva la trasformazione A→B e applica la stessa regola a C.",
        "risposta_corretta": "B",
        "spiegazione": (
            "La trasformazione aumenta di un lato la figura esterna, elimina il riempimento "
            "e sposta il punto di una posizione in senso orario. Applicando la stessa regola a C "
            "si ottiene un quadrato rosso vuoto con punto in alto."
        ),
        "analogia": {
            "A": {"shape": "pentagon", "color": "blu", "fill": True, "dot_pos": "top"},
            "B": {"shape": "hexagon", "color": "blu", "fill": False, "dot_pos": "right"},
            "C": {"shape": "circle", "color": "rosso", "fill": True, "dot_pos": "left"},
        },
        "opzioni_visuali": {
            "A": {"shape": "square", "color": "rosso", "fill": True, "dot_pos": "top"},
            "B": {"shape": "square", "color": "rosso", "fill": False, "dot_pos": "top"},
            "C": {"shape": "triangle", "color": "rosso", "fill": False, "dot_pos": "top"},
            "D": {"shape": "square", "color": "rosso", "fill": False, "dot_pos": "right"},
        },
    },
    {
        "id": "LOG-VIS-AV-0007",
        "livello": "avanzato",
        "tipo_visuale": "somma_elementi",
        "domanda": "Ogni terza figura riassume gli elementi delle prime due. Quale figura completa l'ultima riga?",
        "risposta_corretta": "A",
        "spiegazione": (
            "Nella terza colonna viene sommato il numero di elementi delle prime due colonne. "
            "Nell'ultima riga: 1 stella + 3 stelle = 4 stelle. La forma resta triangolo verde."
        ),
        "matrice": [
            [
                {"shape": "circle", "color": "blu", "inner": "dot", "inner_count": 1},
                {"shape": "circle", "color": "blu", "inner": "dot", "inner_count": 2},
                {"shape": "circle", "color": "blu", "inner": "dot", "inner_count": 3},
            ],
            [
                {"shape": "square", "color": "rosso", "inner": "line", "inner_count": 2},
                {"shape": "square", "color": "rosso", "inner": "line", "inner_count": 3},
                {"shape": "square", "color": "rosso", "inner": "line", "inner_count": 5},
            ],
            [
                {"shape": "triangle", "color": "verde", "inner": "star", "inner_count": 1},
                {"shape": "triangle", "color": "verde", "inner": "star", "inner_count": 3},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "triangle", "color": "verde", "inner": "star", "inner_count": 4},
            "B": {"shape": "triangle", "color": "verde", "inner": "star", "inner_count": 3},
            "C": {"shape": "triangle", "color": "blu", "inner": "star", "inner_count": 4},
            "D": {"shape": "square", "color": "verde", "inner": "star", "inner_count": 4},
        },
    },
    {
        "id": "LOG-VIS-AV-0008",
        "livello": "avanzato",
        "tipo_visuale": "matrice_ciclica",
        "domanda": "Questa matrice combina forma, colore e numero di segmenti. Quale figura manca?",
        "risposta_corretta": "D",
        "spiegazione": (
            "Le forme ruotano ciclicamente tra cerchio, quadrato e triangolo. "
            "I colori alternano blu e rosso, mentre i segmenti aumentano da sinistra a destra. "
            "La casella mancante è un quadrato blu con tre barre diagonali."
        ),
        "matrice": [
            [
                {"shape": "circle", "color": "blu", "bars": 1},
                {"shape": "square", "color": "rosso", "bars": 2},
                {"shape": "triangle", "color": "blu", "bars": 3},
            ],
            [
                {"shape": "square", "color": "rosso", "bars": 1},
                {"shape": "triangle", "color": "blu", "bars": 2},
                {"shape": "circle", "color": "rosso", "bars": 3},
            ],
            [
                {"shape": "triangle", "color": "blu", "bars": 1},
                {"shape": "circle", "color": "rosso", "bars": 2},
                None,
            ],
        ],
        "opzioni_visuali": {
            "A": {"shape": "circle", "color": "blu", "bars": 3},
            "B": {"shape": "square", "color": "rosso", "bars": 3},
            "C": {"shape": "square", "color": "blu", "bars": 2},
            "D": {"shape": "square", "color": "blu", "bars": 3},
        },
    },
]


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
            valore = dati.get(chiave)

            if isinstance(valore, list):
                return valore

    raise ValueError("Non riesco a trovare la lista delle domande nel JSON.")


def colore(nome):
    return COLORI.get(nome, "#111111")


def polygon_points(cx, cy, radius, sides, rotation=-90):
    import math

    points = []

    for index in range(sides):
        angle = math.radians(rotation + index * 360 / sides)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")

    return " ".join(points)


def shape_svg(item, cx=100, cy=100, size=58):
    if item is None:
        return (
            f'<rect x="{cx - 45}" y="{cy - 45}" width="90" height="90" '
            f'rx="12" fill="none" stroke="#999999" stroke-width="3" '
            f'stroke-dasharray="8 7"/>'
            f'<text x="{cx}" y="{cy + 18}" text-anchor="middle" '
            f'font-size="60" fill="#777777">?</text>'
        )

    shape = item.get("shape", "circle")
    c = colore(item.get("color", "blu"))
    stroke = c
    fill = "none"

    if item.get("fill") is True or item.get("pattern") == "solid":
        fill = c

    elements = []

    if item.get("nested"):
        nested = int(item.get("nested", 1))

        for level in range(nested):
            current_size = size - level * 10
            elements.append(draw_outer_shape(shape, cx, cy, current_size, stroke, "none", 3))

        inner_size = size - nested * 12
        pattern = item.get("pattern", "solid")
        elements.append(draw_pattern(shape, cx, cy, max(inner_size, 18), stroke, pattern))

    else:
        elements.append(draw_outer_shape(shape, cx, cy, size, stroke, fill, 4))

    if "diagonal" in item:
        diag = item.get("diagonal")

        if diag == "/":
            elements.append(
                f'<line x1="{cx - size * 0.55}" y1="{cy + size * 0.55}" '
                f'x2="{cx + size * 0.55}" y2="{cy - size * 0.55}" '
                f'stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            )
        else:
            elements.append(
                f'<line x1="{cx - size * 0.55}" y1="{cy - size * 0.55}" '
                f'x2="{cx + size * 0.55}" y2="{cy + size * 0.55}" '
                f'stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            )

    if "lines" in item:
        total_lines = int(item.get("lines", 1))
        start_y = cy - (total_lines - 1) * 10

        for index in range(total_lines):
            y = start_y + index * 20
            elements.append(
                f'<line x1="{cx - 30}" y1="{y}" x2="{cx + 30}" y2="{y}" '
                f'stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            )

    if "bars" in item:
        total_bars = int(item.get("bars", 1))
        start_x = cx - (total_bars - 1) * 10

        for index in range(total_bars):
            x = start_x + index * 20
            elements.append(
                f'<line x1="{x - 18}" y1="{cy + 22}" x2="{x + 18}" y2="{cy - 22}" '
                f'stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            )

    if "direction" in item:
        elements = [draw_arrow(cx, cy, size, stroke, item.get("direction", "up"))]

    if "count" in item:
        elements.extend(draw_dots(cx, cy, int(item.get("count", 0)), stroke))

    if "inner" in item:
        inner = item.get("inner")
        inner_count = int(item.get("inner_count", 1))
        elements.extend(draw_inner_items(cx, cy, inner, inner_count, stroke))

    if "dot_pos" in item:
        elements.append(draw_position_dot(cx, cy, item["dot_pos"], stroke, item.get("fill", False)))

    if shape == "mirror":
        return draw_mirror_variant(cx, cy, stroke, item.get("variant", "same"))

    return "\n".join(elements)


def draw_outer_shape(shape, cx, cy, size, stroke, fill, stroke_width):
    if shape == "circle":
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{size}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    if shape == "square":
        return (
            f'<rect x="{cx - size}" y="{cy - size}" width="{size * 2}" height="{size * 2}" '
            f'rx="6" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    sides_map = {
        "triangle": 3,
        "pentagon": 5,
        "hexagon": 6,
        "heptagon": 7,
    }

    sides = sides_map.get(shape, 6)
    points = polygon_points(cx, cy, size, sides)

    return (
        f'<polygon points="{points}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="round"/>'
    )


def draw_pattern(shape, cx, cy, size, stroke, pattern):
    elements = []

    if pattern == "solid":
        elements.append(draw_outer_shape(shape, cx, cy, size, stroke, stroke, 2))

    elif pattern == "stripes":
        elements.append(draw_outer_shape(shape, cx, cy, size, stroke, "none", 2))

        for offset in [-18, -9, 0, 9, 18]:
            elements.append(
                f'<line x1="{cx - size * 0.55}" y1="{cy + offset}" '
                f'x2="{cx + size * 0.55}" y2="{cy + offset}" '
                f'stroke="{stroke}" stroke-width="2"/>'
            )

    elif pattern == "dots":
        elements.append(draw_outer_shape(shape, cx, cy, size, stroke, "none", 2))

        positions = [
            (-18, -18), (0, -18), (18, -18),
            (-18, 0), (0, 0), (18, 0),
            (-18, 18), (0, 18), (18, 18),
        ]

        for dx, dy in positions:
            elements.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="4" fill="{stroke}"/>')

    elif pattern == "cross":
        elements.append(draw_outer_shape(shape, cx, cy, size, stroke, "none", 2))

        for offset in [-18, 0, 18]:
            elements.append(
                f'<line x1="{cx - size * 0.55}" y1="{cy + offset}" '
                f'x2="{cx + size * 0.55}" y2="{cy + offset}" '
                f'stroke="{stroke}" stroke-width="2"/>'
            )
            elements.append(
                f'<line x1="{cx + offset}" y1="{cy - size * 0.55}" '
                f'x2="{cx + offset}" y2="{cy + size * 0.55}" '
                f'stroke="{stroke}" stroke-width="2"/>'
            )

    return "\n".join(elements)


def draw_dots(cx, cy, count, stroke):
    positions_by_count = {
        1: [(0, 0)],
        2: [(-14, 0), (14, 0)],
        3: [(-20, 0), (0, 0), (20, 0)],
        4: [(-16, -14), (16, -14), (-16, 14), (16, 14)],
        5: [(-20, -16), (20, -16), (0, 0), (-20, 16), (20, 16)],
    }

    positions = positions_by_count.get(count, positions_by_count[1])
    elements = []

    for dx, dy in positions:
        elements.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="7" fill="{stroke}"/>')

    return elements


def draw_inner_items(cx, cy, inner, count, stroke):
    positions_by_count = {
        1: [(0, 0)],
        2: [(-18, 0), (18, 0)],
        3: [(0, -18), (-20, 18), (20, 18)],
        4: [(-20, -18), (20, -18), (-20, 18), (20, 18)],
        5: [(0, -24), (-22, 0), (22, 0), (-14, 24), (14, 24)],
    }

    positions = positions_by_count.get(count, positions_by_count[1])
    elements = []

    for dx, dy in positions:
        x = cx + dx
        y = cy + dy

        if inner == "triangle":
            points = polygon_points(x, y, 11, 3)
            elements.append(f'<polygon points="{points}" fill="{stroke}"/>')

        elif inner == "star":
            elements.append(draw_star(x, y, 12, stroke))

        elif inner == "line":
            elements.append(
                f'<line x1="{x - 10}" y1="{y}" x2="{x + 10}" y2="{y}" '
                f'stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            )

        else:
            elements.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{stroke}"/>')

    return elements


def draw_star(cx, cy, size, fill):
    import math

    points = []

    for index in range(10):
        radius = size if index % 2 == 0 else size * 0.45
        angle = math.radians(-90 + index * 36)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")

    return f'<polygon points="{" ".join(points)}" fill="{fill}"/>'


def draw_arrow(cx, cy, size, stroke, direction):
    base = [
        (-42, -18), (0, -18), (0, -38),
        (48, 0),
        (0, 38), (0, 18), (-42, 18),
    ]

    rotations = {
        "right": 0,
        "down": 90,
        "left": 180,
        "up": 270,
    }

    import math

    angle = math.radians(rotations.get(direction, 0))
    points = []

    for x, y in base:
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        points.append(f"{cx + rx:.1f},{cy + ry:.1f}")

    return (
        f'<polygon points="{" ".join(points)}" fill="none" '
        f'stroke="{stroke}" stroke-width="5" stroke-linejoin="round"/>'
    )


def draw_position_dot(cx, cy, dot_pos, stroke, filled):
    offsets = {
        "top": (0, -35),
        "right": (35, 0),
        "bottom": (0, 35),
        "left": (-35, 0),
    }

    dx, dy = offsets.get(dot_pos, (0, -35))
    fill = "white" if filled else stroke

    return f'<circle cx="{cx + dx}" cy="{cy + dy}" r="8" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'


def draw_mirror_variant(cx, cy, stroke, variant):
    if variant == "correct":
        top_x = cx + 35
        bottom_x = cx - 35
    elif variant == "wrong_dot":
        top_x = cx - 35
        bottom_x = cx - 35
    elif variant == "rotated":
        top_x = cx
        bottom_x = cx
    else:
        top_x = cx - 35
        bottom_x = cx + 35

    return f"""
    <circle cx="{top_x}" cy="{cy - 45}" r="26" fill="none" stroke="{stroke}" stroke-width="4"/>
    <polygon points="{top_x},{cy - 60} {top_x - 12},{cy - 35} {top_x + 12},{cy - 35}" fill="{stroke}"/>
    <path d="M {cx - 45} {cy} A 45 35 0 0 0 {cx + 45} {cy}" fill="none" stroke="{stroke}" stroke-width="4"/>
    <line x1="{cx - 35}" y1="{cy - 5}" x2="{cx + 35}" y2="{cy - 5}" stroke="{stroke}" stroke-width="3"/>
    <line x1="{cx - 28}" y1="{cy + 5}" x2="{cx + 28}" y2="{cy + 5}" stroke="{stroke}" stroke-width="3"/>
    <polygon points="{bottom_x},{cy + 45} {bottom_x + 28},{cy + 73} {bottom_x},{cy + 101} {bottom_x - 28},{cy + 73}" fill="none" stroke="{stroke}" stroke-width="4"/>
    <circle cx="{bottom_x}" cy="{cy + 73}" r="8" fill="{stroke}"/>
    """


def svg_wrapper(width, height, content):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
{content}
</svg>
"""


def salva_svg(path, width, height, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_wrapper(width, height, content), encoding="utf-8")


def render_sequence(question_id, items):
    width = 780
    height = 180
    cell_w = 135
    start_x = 80
    cy = 88

    elements = []

    for index, item in enumerate(items):
        cx = start_x + index * cell_w
        elements.append(
            f'<rect x="{cx - 58}" y="24" width="116" height="130" rx="14" '
            f'fill="#ffffff" stroke="#dddddd" stroke-width="2"/>'
        )
        elements.append(shape_svg(item, cx, cy, 42))

        if index < len(items) - 1:
            arrow_x = cx + 70
            elements.append(
                f'<text x="{arrow_x}" y="{cy + 10}" text-anchor="middle" '
                f'font-size="34" fill="#555555">→</text>'
            )

    path = ASSET_DIR / f"{question_id}_domanda.svg"
    salva_svg(path, width, height, "\n".join(elements))

    return str(path)


def render_matrix(question_id, matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    cell = 145
    width = cols * cell
    height = rows * cell

    elements = []

    for row_index, row in enumerate(matrix):
        for col_index, item in enumerate(row):
            x = col_index * cell
            y = row_index * cell

            elements.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'fill="#ffffff" stroke="#d8d8d8" stroke-width="2"/>'
            )
            elements.append(shape_svg(item, x + cell / 2, y + cell / 2, 42))

    path = ASSET_DIR / f"{question_id}_domanda.svg"
    salva_svg(path, width, height, "\n".join(elements))

    return str(path)


def render_analogy(question_id, analogy):
    width = 820
    height = 190
    elements = []

    labels = [
        ("A", analogy["A"]),
        ("B", analogy["B"]),
        ("C", analogy["C"]),
        ("?", None),
    ]

    positions = [100, 290, 500, 700]

    for index, (label, item) in enumerate(labels):
        cx = positions[index]
        elements.append(
            f'<text x="{cx}" y="34" text-anchor="middle" font-size="28" '
            f'font-weight="bold" fill="#111111">{label}</text>'
        )

        elements.append(shape_svg(item, cx, 105, 42))

        if index == 0:
            elements.append('<text x="195" y="112" text-anchor="middle" font-size="34" fill="#555555">:</text>')
        elif index == 1:
            elements.append('<text x="395" y="112" text-anchor="middle" font-size="34" fill="#555555">::</text>')

    path = ASSET_DIR / f"{question_id}_domanda.svg"
    salva_svg(path, width, height, "\n".join(elements))

    return str(path)


def render_mirror(question_id, item):
    width = 560
    height = 250
    stroke = colore(item.get("color", "viola"))

    elements = [
        draw_mirror_variant(180, 90, stroke, "same"),
        f'<line x1="330" y1="25" x2="330" y2="220" stroke="{stroke}" '
        f'stroke-width="3" stroke-dasharray="8 8"/>',
    ]

    path = ASSET_DIR / f"{question_id}_domanda.svg"
    salva_svg(path, width, height, "\n".join(elements))

    return str(path)


def render_option(question_id, letter, item):
    width = 170
    height = 170

    elements = [
        f'<rect x="8" y="8" width="154" height="154" rx="18" '
        f'fill="#ffffff" stroke="#dddddd" stroke-width="2"/>',
        shape_svg(item, 85, 85, 42),
    ]

    path = ASSET_DIR / f"{question_id}_opzione_{letter}.svg"
    salva_svg(path, width, height, "\n".join(elements))

    return str(path)


def crea_immagini(domanda):
    question_id = domanda["id"]

    if "matrice" in domanda:
        domanda_path = render_matrix(question_id, domanda["matrice"])

    elif "sequenza" in domanda:
        domanda_path = render_sequence(question_id, domanda["sequenza"])

    elif "analogia" in domanda:
        domanda_path = render_analogy(question_id, domanda["analogia"])

    elif "figura_specchio" in domanda:
        domanda_path = render_mirror(question_id, domanda["figura_specchio"])

    else:
        raise ValueError(f"Nessun tipo visuale riconosciuto per {question_id}")

    opzioni_path = {}

    for lettera, item in domanda["opzioni_visuali"].items():
        opzioni_path[lettera] = render_option(question_id, lettera, item)

    return domanda_path, opzioni_path


def prepara_domanda_per_json(domanda):
    domanda_path, opzioni_path = crea_immagini(domanda)

    return {
        "id": domanda["id"],
        "categoria": "logica",
        "sottocategoria": "logica_visiva",
        "livello": domanda["livello"],
        "tipo": "visiva",
        "domanda": domanda["domanda"],
        "opzioni": ["A", "B", "C", "D"],
        "risposta_corretta": domanda["risposta_corretta"],
        "spiegazione": domanda["spiegazione"],
        "immagine": domanda_path,
        "immagine_domanda": domanda_path,
        "immagini_opzioni": opzioni_path,
    }


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"File non trovato: {DATA_FILE}")

    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    dati = carica_json(DATA_FILE)
    lista_domande = trova_lista_domande(dati)

    if not BACKUP_FILE.exists():
        salva_json(BACKUP_FILE, dati)
        print("Backup creato:", BACKUP_FILE)

    id_esistenti = {domanda.get("id") for domanda in lista_domande if isinstance(domanda, dict)}
    domande_aggiunte = 0
    domande_saltate = 0

    for domanda in NUOVE_DOMANDE:
        if domanda["id"] in id_esistenti:
            print("Già presente, salto:", domanda["id"])
            domande_saltate += 1
            continue

        domanda_json = prepara_domanda_per_json(domanda)
        lista_domande.append(domanda_json)

        print("Aggiunta:", domanda["id"], "-", domanda["livello"])
        domande_aggiunte += 1

    salva_json(DATA_FILE, dati)

    print("")
    print("----- ESPANSIONE LOGICA VISIVA COMPLETATA -----")
    print("Domande aggiunte:", domande_aggiunte)
    print("Domande saltate perché già presenti:", domande_saltate)
    print("File aggiornato:", DATA_FILE)
    print("Immagini create in:", ASSET_DIR)


main()