import re


SHAPE_SIDES = {
    "cerchio": 0,
    "triangolo": 3,
    "quadrato": 4,
    "pentagono": 5,
    "esagono": 6,
}


REQUIRED_EXPLANATION_WORDS = [
    "forma",
    "colore",
    "lati",
    "intern",
    "regola",
]


def is_visual_logic_question(question):
    return (
        question.get("sottocategoria") == "logica_visiva"
        or str(question.get("id", "")).startswith("LOG-VIS")
    )


def normalize_text(value):
    return str(value or "").lower().strip()


def explanation_contains_term(text, term):
    normalized_term = normalize_text(term)

    if not normalized_term:
        return True

    if normalized_term in text:
        return True

    if len(normalized_term) > 4 and normalized_term[:-1] in text:
        return True

    return False


def canonical_figure(figure):
    if not isinstance(figure, dict):
        return None

    inner_objects = figure.get("inner_objects", [])

    if not isinstance(inner_objects, list):
        inner_objects = []

    return {
        "outer_shape": normalize_text(figure.get("outer_shape")),
        "outer_color": normalize_text(figure.get("outer_color")),
        "sides": figure.get("sides"),
        "inner_objects": sorted(
            [
                {
                    "type": normalize_text(item.get("type")),
                    "color": normalize_text(item.get("color")),
                    "quantity": item.get("quantity"),
                    "position": normalize_text(item.get("position")),
                }
                for item in inner_objects
                if isinstance(item, dict)
            ],
            key=lambda item: (
                item["type"],
                item["color"],
                str(item["quantity"]),
                item["position"],
            ),
        ),
    }


def figures_match(left, right):
    return canonical_figure(left) == canonical_figure(right)


def validate_figure(figure, label, uses_position=False):
    errors = []

    if not isinstance(figure, dict):
        return [f"{label}: la figura deve essere un oggetto strutturato."]

    outer_shape = normalize_text(figure.get("outer_shape"))
    outer_color = normalize_text(figure.get("outer_color"))
    sides = figure.get("sides")

    if not outer_shape:
        errors.append(f"{label}: manca la forma esterna.")

    if not outer_color:
        errors.append(f"{label}: manca il colore esterno.")

    expected_sides = SHAPE_SIDES.get(outer_shape)

    if expected_sides is None:
        errors.append(f"{label}: forma esterna non riconosciuta: {outer_shape}.")
    elif not isinstance(sides, int):
        errors.append(f"{label}: manca il numero di lati.")
    elif sides != expected_sides:
        errors.append(
            f"{label}: numero di lati incoerente, {outer_shape} richiede {expected_sides}."
        )

    inner_objects = figure.get("inner_objects")

    if not isinstance(inner_objects, list):
        errors.append(f"{label}: manca l'elenco completo degli oggetti interni.")
        return errors

    for index, item in enumerate(inner_objects, start=1):
        item_label = f"{label}, oggetto interno {index}"

        if not isinstance(item, dict):
            errors.append(f"{item_label}: deve essere un oggetto strutturato.")
            continue

        if not normalize_text(item.get("type")):
            errors.append(f"{item_label}: manca il tipo.")

        if not normalize_text(item.get("color")):
            errors.append(f"{item_label}: manca il colore.")

        quantity = item.get("quantity")

        if not isinstance(quantity, int) or quantity < 1:
            errors.append(f"{item_label}: manca una quantità valida.")

        if uses_position and not normalize_text(item.get("position")):
            errors.append(f"{item_label}: manca la posizione.")

    return errors


def get_option_map(question):
    options = question.get("opzioni", [])
    visual_logic = question.get("visual_logic", {})
    visual_options = visual_logic.get("options", {})

    if not isinstance(options, list):
        return {}

    return {
        option: visual_options.get(option)
        for option in options
    }


def validate_color_alternation(sequence, expected_answer, colors):
    errors = []

    if not isinstance(colors, list) or len(colors) < 2:
        return ["La regola di alternanza colori deve dichiarare almeno due colori."]

    observed_colors = [
        normalize_text(figure.get("outer_color"))
        for figure in sequence + [expected_answer]
    ]

    for index, color in enumerate(observed_colors):
        expected_color = normalize_text(colors[index % len(colors)])

        if color != expected_color:
            errors.append(
                "Alternanza colori non rispettata: "
                f"posizione {index + 1} ha '{color}', atteso '{expected_color}'."
            )

    return errors


def explanation_mentions_required_parts(explanation, expected_answer, rule_text):
    text = normalize_text(explanation)
    errors = []

    if len(text) < 120:
        errors.append("La spiegazione è troppo breve per una domanda visiva.")

    for word in REQUIRED_EXPLANATION_WORDS:
        if word not in text:
            errors.append(f"La spiegazione non cita '{word}'.")

    outer_shape = normalize_text(expected_answer.get("outer_shape"))
    outer_color = normalize_text(expected_answer.get("outer_color"))
    sides = expected_answer.get("sides")

    if outer_shape and outer_shape not in text:
        errors.append("La spiegazione non cita la forma esterna corretta.")

    if outer_color and outer_color not in text:
        errors.append("La spiegazione non cita il colore esterno corretto.")

    if isinstance(sides, int) and str(sides) not in text:
        errors.append("La spiegazione non cita il numero di lati corretto.")

    for item in expected_answer.get("inner_objects", []):
        item_type = normalize_text(item.get("type"))
        item_color = normalize_text(item.get("color"))
        quantity = item.get("quantity")

        if isinstance(quantity, int) and str(quantity) not in text:
            errors.append("La spiegazione non cita la quantità degli oggetti interni.")

        if item_type and not explanation_contains_term(text, item_type):
            errors.append("La spiegazione non cita il tipo degli oggetti interni.")

        if item_color and item_color not in text:
            errors.append("La spiegazione non cita il colore degli oggetti interni.")

    if rule_text and not any(
        word in text
        for word in ["alterna", "alternanza", "aumenta", "mantiene", "speculare", "matrice", "sequenza"]
    ):
        errors.append("La spiegazione non cita chiaramente la regola logica usata.")

    return errors


def validate_wrong_option_explanations(question):
    errors = []
    correct = question.get("risposta_corretta")
    option_explanations = question.get("spiegazioni_opzioni", {})

    if not isinstance(option_explanations, dict):
        return ["Manca il dizionario spiegazioni_opzioni per le risposte."]

    for option in question.get("opzioni", []):
        explanation = normalize_text(option_explanations.get(option))

        if option == correct:
            continue

        if len(explanation) < 50:
            errors.append(f"L'opzione {option} non spiega chiaramente cosa non torna.")
            continue

        if not any(word in explanation for word in ["sbaglia", "non", "manca", "incoerente"]):
            errors.append(f"L'opzione {option} non dice chiaramente cosa non torna.")

    return errors


def validate_mirror_instruction(question, visual_logic):
    errors = []
    sequence = visual_logic.get("sequence", [])
    rule = visual_logic.get("rule", {})
    mirror_axis = normalize_text(rule.get("mirror_axis"))

    is_mirror = (
        normalize_text(visual_logic.get("type")) == "mirror"
        or bool(mirror_axis)
    )

    if not is_mirror or len(sequence) != 1:
        return errors

    text = normalize_text(question.get("domanda"))
    axis_pattern = r"figura speculare rispetto all'asse (verticale|orizzontale)"

    if not re.search(axis_pattern, text):
        errors.append(
            "Domanda speculare ambigua: manca la frase "
            "'Scegli la figura speculare rispetto all'asse verticale/orizzontale'."
        )

    if mirror_axis not in ["verticale", "orizzontale"]:
        errors.append("La regola speculare deve dichiarare asse verticale o orizzontale.")

    return errors


def validate_visual_logic_question(question):
    errors = []

    if not is_visual_logic_question(question):
        return {
            "valid": True,
            "errors": [],
        }

    visual_logic = question.get("visual_logic")

    if not isinstance(visual_logic, dict):
        return {
            "valid": False,
            "errors": ["Manca il contratto visual_logic della domanda visiva."],
        }

    sequence = visual_logic.get("sequence")
    expected_answer = visual_logic.get("expected_answer")
    rule = visual_logic.get("rule", {})
    uses_position = bool(visual_logic.get("uses_position"))

    if not isinstance(sequence, list) or not sequence:
        errors.append("visual_logic.sequence deve contenere almeno una figura.")
        sequence = []

    if not isinstance(expected_answer, dict):
        errors.append("Manca visual_logic.expected_answer.")
        expected_answer = {}

    for index, figure in enumerate(sequence, start=1):
        errors.extend(validate_figure(figure, f"sequenza figura {index}", uses_position))

    errors.extend(validate_figure(expected_answer, "risposta corretta attesa", uses_position))

    option_map = get_option_map(question)
    correct = question.get("risposta_corretta")

    if correct not in option_map:
        errors.append("La risposta corretta non è presente nelle opzioni visuali.")
    elif not figures_match(option_map.get(correct), expected_answer):
        errors.append("La risposta corretta non rispetta la regola dichiarata.")

    correct_figure = option_map.get(correct)

    for option, figure in option_map.items():
        errors.extend(validate_figure(figure, f"opzione {option}", uses_position))

        if option != correct and figures_match(figure, correct_figure):
            errors.append(f"L'opzione {option} è uguale alla risposta corretta.")

    color_rule = rule.get("color_alternation", {})

    if isinstance(color_rule, dict) and color_rule.get("enabled"):
        errors.extend(
            validate_color_alternation(
                sequence,
                expected_answer,
                color_rule.get("colors", []),
            )
        )

    errors.extend(validate_mirror_instruction(question, visual_logic))

    errors.extend(
        explanation_mentions_required_parts(
            question.get("spiegazione", ""),
            expected_answer,
            rule.get("description", ""),
        )
    )

    errors.extend(validate_wrong_option_explanations(question))

    return {
        "valid": not errors,
        "errors": errors,
    }
