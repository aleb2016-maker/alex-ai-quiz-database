import json
from pathlib import Path

FILE = Path("data/inglese.json")
BACKUP = Path("data/inglese.backup_prima_terzo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_inglese_terzo_blocco_distrattori_forti.md")

PATCH = {
    "ING-FAC-0201": {
        "opzioni": [
            "am",
            "is",
            "are",
            "be"
        ],
        "spiegazione": (
            "Con il soggetto 'I' si usa il verbo 'am'. "
            "La frase corretta è 'I am from Rome'. "
            "'Is' si usa con he, she e it; 'are' si usa con you, we e they; 'be' è la forma base e non completa correttamente questa frase. "
            "Traduzione domanda: \"Scegli la frase corretta: io ___ di Roma.\" "
            "Traduzione risposta: \"sono\""
        )
    },

    "ING-FAC-0202": {
        "opzioni": [
            "drinks",
            "drink",
            "is drink",
            "drinking"
        ],
        "spiegazione": (
            "Alla terza persona singolare del present simple si aggiunge spesso la s finale. "
            "Con 'she' la forma corretta è 'drinks', quindi la frase diventa 'She drinks coffee every morning'. "
            "'Drink' manca della s, 'is drink' mescola due strutture, 'drinking' da solo non completa il present simple. "
            "Traduzione domanda: \"Scegli la frase corretta: lei beve caffè ogni mattina.\" "
            "Traduzione risposta: \"beve\""
        )
    },

    "ING-FAC-0203": {
        "opzioni": [
            "an",
            "a",
            "the",
            "some"
        ],
        "spiegazione": (
            "Si usa 'an' davanti a parole che iniziano con suono vocalico, come 'umbrella'. "
            "La frase corretta è 'I need an umbrella'. "
            "'A' si usa davanti a suono consonantico, 'the' indica qualcosa di specifico, 'some' non è adatto con questo singolare nella frase. "
            "Traduzione domanda: \"Scegli l'articolo corretto: ho bisogno di un ombrello.\" "
            "Traduzione risposta: \"un\""
        )
    },

    "ING-FAC-0204": {
        "opzioni": [
            "children",
            "childs",
            "childes",
            "childrens"
        ],
        "spiegazione": (
            "'Child' ha un plurale irregolare: 'children'. "
            "Quindi si dice 'one child, two children'. "
            "'Childs', 'childes' e 'childrens' sembrano plurali possibili, ma non sono corretti in inglese standard. "
            "Traduzione domanda: \"Scegli il plurale corretto: un bambino, due ___.\" "
            "Traduzione risposta: \"bambini\""
        )
    },

    "ING-FAC-0205": {
        "opzioni": [
            "on",
            "in",
            "at",
            "over"
        ],
        "spiegazione": (
            "Si usa 'on' quando qualcosa si trova sopra una superficie. "
            "La frase corretta è 'The keys are on the table'. "
            "'In' indica dentro, 'at' indica un punto o luogo generico, 'over' indica sopra ma non necessariamente appoggiato sulla superficie. "
            "Traduzione domanda: \"Scegli la preposizione corretta: le chiavi sono sul tavolo.\" "
            "Traduzione risposta: \"su\""
        )
    },

    "ING-FAC-0206": {
        "opzioni": [
            "Do",
            "Does",
            "Are",
            "Is"
        ],
        "spiegazione": (
            "Nel present simple interrogativo, con 'you' si usa l'ausiliare 'do'. "
            "La domanda corretta è 'Do you speak English?'. "
            "'Does' si usa con he, she e it; 'are' e 'is' appartengono al verbo to be e non costruiscono questa domanda con 'speak'. "
            "Traduzione domanda: \"Scegli la domanda corretta: parli inglese?\" "
            "Traduzione risposta: \"do\""
        )
    },

    "ING-FAC-0207": {
        "opzioni": [
            "do not like",
            "does not like",
            "not like",
            "am not like"
        ],
        "spiegazione": (
            "Con 'I', nella forma negativa del present simple, si usa 'do not' più verbo base. "
            "La frase corretta è 'I do not like onions'. "
            "'Does not like' si usa con he, she e it; 'not like' manca dell'ausiliare; 'am not like' confonde il verbo to be con il verbo 'like'. "
            "Traduzione domanda: \"Completa la frase negativa al present simple: non mi piacciono le cipolle.\" "
            "Traduzione risposta: \"non mi piacciono\""
        )
    },

    "ING-FAC-0208": {
        "opzioni": [
            "Good night",
            "Good evening",
            "Good afternoon",
            "Good luck"
        ],
        "spiegazione": (
            "'Good night' significa buonanotte e si usa prima di dormire o quando ci si congeda la sera tardi. "
            "'Good evening' significa buonasera, 'Good afternoon' significa buon pomeriggio, 'Good luck' significa buona fortuna. "
            "Traduzione domanda: \"Scegli la traduzione corretta di buonanotte.\" "
            "Traduzione risposta: \"Buonanotte\""
        )
    },

    "ING-FAC-0209": {
        "opzioni": [
            "are",
            "is",
            "am",
            "be"
        ],
        "spiegazione": (
            "Con 'there' e un nome plurale si usa 'there are'. "
            "Poiché 'two chairs' è plurale, la frase corretta è 'There are two chairs in the room'. "
            "'Is' si usa con il singolare, 'am' con I, 'be' è la forma base. "
            "Traduzione domanda: \"Scegli la frase corretta: ci sono due sedie nella stanza.\" "
            "Traduzione risposta: \"ci sono\""
        )
    },

    "ING-FAC-0210": {
        "opzioni": [
            "food",
            "water",
            "sleep",
            "weather"
        ],
        "spiegazione": (
            "'Hungry' significa affamato, quindi la parola più adatta è 'food'. "
            "La frase corretta è 'I am hungry. I want some food'. "
            "'Water' si collega alla sete, 'sleep' alla stanchezza, 'weather' significa tempo atmosferico. "
            "Traduzione domanda: \"Scegli la parola corretta: ho fame. Voglio del cibo.\" "
            "Traduzione risposta: \"cibo\""
        )
    },

    "ING-FAC-0211": {
        "opzioni": [
            "watched",
            "watch",
            "watches",
            "watching"
        ],
        "spiegazione": (
            "'Yesterday' indica un tempo passato, quindi serve il past simple. "
            "Il verbo regolare 'watch' al passato diventa 'watched'. "
            "'Watch' è forma base, 'watches' è present simple con terza persona singolare, 'watching' è forma in -ing. "
            "Traduzione domanda: \"Scegli la forma al passato corretta: ieri ho guardato un film.\" "
            "Traduzione risposta: \"ho guardato\""
        )
    },

    "ING-FAC-0212": {
        "opzioni": [
            "my",
            "me",
            "I",
            "mine"
        ],
        "spiegazione": (
            "'My' è un aggettivo possessivo e si usa prima di un nome, come in 'my book'. "
            "La frase corretta è 'This is my book'. "
            "'Me' è pronome oggetto, 'I' è pronome soggetto, 'mine' è pronome possessivo e non si mette prima di 'book'. "
            "Traduzione domanda: \"Scegli l'aggettivo possessivo corretto: questo è il mio libro.\" "
            "Traduzione risposta: \"mio\""
        )
    },

    "ING-INT-0201": {
        "opzioni": [
            "I have lived here for five years.",
            "I live here since five years.",
            "I have lived here since five years.",
            "I am living here from five years."
        ],
        "spiegazione": (
            "Per una durata iniziata nel passato e ancora valida nel presente si usa spesso il present perfect con 'for'. "
            "La frase corretta è 'I have lived here for five years'. "
            "'Since' si usa con un punto di inizio, non con una durata come 'five years'. "
            "'I live here since five years' e 'I am living here from five years' non sono costruzioni corrette in inglese standard. "
            "Traduzione domanda: \"Come si dice in inglese: vivo qui da cinque anni?\" "
            "Traduzione risposta: \"Vivo qui da cinque anni.\""
        )
    },

    "ING-INT-0202": {
        "opzioni": [
            "so",
            "because",
            "although",
            "while"
        ],
        "spiegazione": (
            "'So' introduce una conseguenza. "
            "La frase significa: ero stanco, quindi sono andato a letto presto. "
            "'Because' introduce una causa, 'although' introduce contrasto, 'while' indica contemporaneità o contrasto. "
            "Traduzione domanda: \"Scegli l'opzione corretta: ero stanco, quindi sono andato a letto presto.\" "
            "Traduzione risposta: \"quindi\""
        )
    },

    "ING-INT-0203": {
        "opzioni": [
            "will stay",
            "stay",
            "would stay",
            "stayed"
        ],
        "spiegazione": (
            "Nel first conditional si usa 'if' + present simple e poi 'will' + verbo base. "
            "La forma corretta è 'If it rains tomorrow, we will stay at home'. "
            "'Stay' manca di 'will', 'would stay' appartiene più al second conditional, 'stayed' è passato. "
            "Traduzione domanda: \"Scegli il condizionale corretto: se domani piove, resteremo a casa.\" "
            "Traduzione risposta: \"resteremo\""
        )
    },

    "ING-INT-0204": {
        "opzioni": [
            "I was studying when you called.",
            "I studied when you were called.",
            "I am studying when you called.",
            "I was study when you called."
        ],
        "spiegazione": (
            "Il past continuous si forma con 'was' o 'were' più verbo in -ing. "
            "La frase corretta è 'I was studying when you called'. "
            "'I studied when you were called' cambia struttura e significato, 'I am studying' usa il presente, 'I was study' manca della forma in -ing. "
            "Traduzione domanda: \"Scegli la frase corretta al past continuous.\" "
            "Traduzione risposta: \"Stavo studiando quando hai chiamato.\""
        )
    },

    "ING-INT-0205": {
        "opzioni": [
            "must",
            "should",
            "might",
            "could"
        ],
        "spiegazione": (
            "'Must' indica obbligo forte. "
            "La frase 'You must wear a helmet on a motorbike' significa che devi indossare il casco in moto. "
            "'Should' indica consiglio, mentre 'might' e 'could' indicano possibilità. "
            "Traduzione domanda: \"Scegli il verbo modale corretto: devi indossare il casco in moto.\" "
            "Traduzione risposta: \"devi\""
        )
    },

    "ING-INT-0206": {
        "opzioni": [
            "The letter was sent yesterday.",
            "The letter sent yesterday.",
            "The letter was send yesterday.",
            "The letter is sent yesterday."
        ],
        "spiegazione": (
            "Il passivo al passato usa 'was' o 'were' più participio passato. "
            "La frase corretta è 'The letter was sent yesterday'. "
            "'The letter sent yesterday' manca dell'ausiliare passivo, 'was send' usa la forma base invece del participio, 'is sent yesterday' mescola presente e tempo passato preciso. "
            "Traduzione domanda: \"Scegli la forma passiva corretta.\" "
            "Traduzione risposta: \"La lettera è stata inviata ieri.\""
        )
    },

    "ING-INT-0207": {
        "opzioni": [
            "easier",
            "more easy",
            "easiest",
            "easy"
        ],
        "spiegazione": (
            "Il comparativo corretto di 'easy' è 'easier'. "
            "La frase corretta è 'This exercise is easier than the last one'. "
            "'More easy' non è la forma standard, 'easiest' è superlativo, 'easy' è la forma base. "
            "Traduzione domanda: \"Completa il confronto: questo esercizio è più facile del precedente.\" "
            "Traduzione risposta: \"più facile\""
        )
    },

    "ING-INT-0208": {
        "opzioni": [
            "the most interesting",
            "the more interesting",
            "the interestinger",
            "most interesting than"
        ],
        "spiegazione": (
            "Con aggettivi lunghi come 'interesting' si usa il superlativo con 'the most'. "
            "La forma corretta è 'the most interesting'. "
            "'The more interesting' è comparativo, 'the interestinger' non è una forma corretta, 'most interesting than' mescola superlativo e comparativo. "
            "Traduzione domanda: \"Completa il superlativo: è il libro più interessante del negozio.\" "
            "Traduzione risposta: \"il più interessante\""
        )
    }
}


def carica_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path, contenuto):
    path.write_text(json.dumps(contenuto, ensure_ascii=False, indent=2), encoding="utf-8")


def estrai_domande(contenuto):
    if isinstance(contenuto, list):
        return contenuto

    for chiave in ["domande", "questions", "quiz", "items"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave]

    raise ValueError("Formato JSON non riconosciuto: non trovo la lista delle domande.")


def aggiorna_opzioni(domanda, nuove_opzioni):
    for chiave in ["opzioni", "options", "risposte", "answers"]:
        if chiave in domanda:
            domanda[chiave] = nuove_opzioni
            return

    domanda["opzioni"] = nuove_opzioni


def aggiorna_risposta_corretta(domanda, testo_corretta):
    for chiave in ["risposta_corretta", "correct_answer", "correct", "answer", "soluzione"]:
        if chiave in domanda:
            valore = str(domanda.get(chiave, "")).strip().upper()

            if valore in ["A", "B", "C", "D"]:
                domanda[chiave] = "A"
            else:
                domanda[chiave] = testo_corretta

            return

    domanda["risposta_corretta"] = testo_corretta


def main():
    if not FILE.exists():
        raise SystemExit("ERRORE: data/inglese.json non trovato.")

    if not BACKUP.exists():
        BACKUP.write_text(FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato: {BACKUP}")
    else:
        print(f"Backup già presente: {BACKUP}")

    contenuto = carica_json(FILE)
    domande = estrai_domande(contenuto)

    indice_per_id = {
        str(domanda.get("id", "")).strip(): domanda
        for domanda in domande
    }

    aggiornate = []
    non_trovate = []

    for id_domanda, dati in PATCH.items():
        domanda = indice_per_id.get(id_domanda)

        if domanda is None:
            non_trovate.append(id_domanda)
            continue

        nuove_opzioni = dati["opzioni"]

        aggiorna_opzioni(domanda, nuove_opzioni)
        aggiorna_risposta_corretta(domanda, nuove_opzioni[0])
        domanda["spiegazione"] = dati["spiegazione"]
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve essere vicina alla corretta per struttura, significato o contesto, "
            "ma sbagliata per un dettaglio preciso: verbo, tempo, articolo, preposizione, connettivo, registro o traduzione."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Inglese - terzo blocco distrattori forti",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: errori inglesi plausibili, strutture vicine, stesso contesto, differenza precisa.",
        "",
        "Controllo speciale: spiegazioni con etichette `Traduzione domanda:` e `Traduzione risposta:`.",
        "",
        f"Domande aggiornate: {len(aggiornate)}",
        "",
    ]

    for id_domanda in aggiornate:
        righe.append(f"- {id_domanda}")

    if non_trovate:
        righe.append("")
        righe.append("## ID non trovati")
        righe.append("")

        for id_domanda in non_trovate:
            righe.append(f"- {id_domanda}")

    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print("===== MIGLIORAMENTO INGLESE - TERZO BLOCCO =====")
    print(f"Domande aggiornate: {len(aggiornate)}")

    for id_domanda in aggiornate:
        print(f"- {id_domanda}")

    if non_trovate:
        print()
        print("ID non trovati:")

        for id_domanda in non_trovate:
            print(f"- {id_domanda}")

    print()
    print(f"Report creato: {REPORT}")
    print("OK: terzo blocco Inglese aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
