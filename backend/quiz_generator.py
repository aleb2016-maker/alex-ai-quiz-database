# Questa funzione genera una lista di domande quiz in formato JSON.
def genera_quiz_json(categoria, difficolta, numero_domande):
    domande_generate = []

    for numero_domanda in range(1, numero_domande + 1):
        domanda = {
            "categoria": categoria,
            "difficolta": difficolta,
            "domanda": (
                f"Domanda {numero_domanda} di {categoria} "
                f"livello {difficolta}"
            ),
            "risposte": [
                "Risposta A",
                "Risposta B",
                "Risposta C",
                "Risposta D"
            ],
            "risposta_corretta": 0,
            "spiegazione": (
                "Questa è una spiegazione dimostrativa. "
                "Più avanti verrà generata da una vera AI."
            )
        }

        domande_generate.append(domanda)

    return domande_generate