import json
from pathlib import Path

FILE = Path("data/inglese.json")
BACKUP = Path("data/inglese.backup_prima_quarto_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_inglese_quarto_blocco_distrattori_forti.md")

PATCH = {
    "ING-INT-0209": {
        "opzioni": [
            "turn off",
            "turn on",
            "turn down",
            "turn up"
        ],
        "spiegazione": (
            "'Turn off' significa spegnere. "
            "La frase corretta è 'Please turn off your phone before the meeting'. "
            "'Turn on' significa accendere, 'turn down' significa abbassare, 'turn up' significa alzare o presentarsi. "
            "Traduzione domanda: \"Scegli il phrasal verb corretto: per favore spegni il telefono prima della riunione.\" "
            "Traduzione risposta: \"spegni\""
        )
    },

    "ING-INT-0210": {
        "opzioni": [
            "Could you tell me where the station is?",
            "Could you tell me where is the station?",
            "Could you tell me where the station?",
            "Could you tell me where does the station is?"
        ],
        "spiegazione": (
            "Nelle domande indirette l'ordine delle parole diventa simile a una frase affermativa. "
            "La forma corretta è 'Could you tell me where the station is?'. "
            "'Where is the station' è ordine da domanda diretta, 'where the station' manca del verbo, 'where does the station is' mescola ausiliari in modo errato. "
            "Traduzione domanda: \"Scegli la domanda indiretta corretta.\" "
            "Traduzione risposta: \"Potrebbe dirmi dov'è la stazione?\""
        )
    },

    "ING-INT-0211": {
        "opzioni": [
            "some",
            "many",
            "few",
            "several"
        ],
        "spiegazione": (
            "'Milk' è un nome non numerabile. "
            "In una frase affermativa si può usare 'some': 'There is some milk in the fridge'. "
            "'Many', 'few' e 'several' si usano con nomi numerabili plurali, non con 'milk'. "
            "Traduzione domanda: \"Scegli il quantificatore corretto: c'è del latte in frigorifero.\" "
            "Traduzione risposta: \"del\""
        )
    },

    "ING-INT-0212": {
        "opzioni": [
            "too heavy to",
            "heavy enough to",
            "too heavy for",
            "heavy too to"
        ],
        "spiegazione": (
            "La struttura corretta è 'too + aggettivo + to + verbo'. "
            "Quindi si dice 'The bag is too heavy to carry'. "
            "'Heavy enough to' avrebbe un significato diverso, 'too heavy for' richiederebbe un nome o pronome dopo 'for', 'heavy too to' ha ordine scorretto. "
            "Traduzione domanda: \"Completa la struttura con too: la borsa è troppo pesante da portare.\" "
            "Traduzione risposta: \"troppo pesante da\""
        )
    },

    "ING-INT-0213": {
        "opzioni": [
            "I used to play football when I was a child.",
            "I use to played football when I was a child.",
            "I used play football when I was a child.",
            "I was used to play football when I was a child."
        ],
        "spiegazione": (
            "'Used to' indica un'abitudine del passato che non è più attuale. "
            "La frase corretta è 'I used to play football when I was a child'. "
            "'Use to played' combina forma base e passato in modo errato, 'used play' manca di 'to', 'was used to play' cambia struttura e significato. "
            "Traduzione domanda: \"Quale frase descrive un'abitudine passata che ora non è più attuale?\" "
            "Traduzione risposta: \"Giocavo a calcio quando ero bambino.\""
        )
    },

    "ING-INT-0214": {
        "opzioni": [
            "who",
            "which",
            "where",
            "when"
        ],
        "spiegazione": (
            "Per riferirsi a una persona in una frase relativa si usa 'who'. "
            "La frase corretta è 'The woman who lives next door is a doctor'. "
            "'Which' si usa più spesso per cose o animali, 'where' per luoghi, 'when' per tempi o momenti. "
            "Traduzione domanda: \"Scegli il pronome relativo corretto: la donna che vive accanto è una dottoressa.\" "
            "Traduzione risposta: \"che\""
        )
    },

    "ING-AV-0201": {
        "opzioni": [
            "If I had known, I would have called you.",
            "If I knew, I would have called you.",
            "If I have known, I would call you.",
            "If I had knew, I would have called you."
        ],
        "spiegazione": (
            "Il third conditional usa 'if' + past perfect e 'would have' + participio passato. "
            "La frase corretta è 'If I had known, I would have called you'. "
            "'If I knew' appartiene più al second conditional, 'If I have known' usa un tempo sbagliato, 'had knew' usa la forma errata invece di 'had known'. "
            "Traduzione domanda: \"Seleziona la struttura irreale del passato per questa idea: se lo avessi saputo, ti avrei chiamato.\" "
            "Traduzione risposta: \"Se lo avessi saputo, ti avrei chiamato.\""
        )
    },

    "ING-AV-0202": {
        "opzioni": [
            "She said that she was tired.",
            "She said that she is tired yesterday.",
            "She said me that she was tired.",
            "She told that she was tired."
        ],
        "spiegazione": (
            "Nel reported speech con backshift, 'am' diventa spesso 'was'. "
            "La frase corretta è 'She said that she was tired'. "
            "'Is tired yesterday' mescola presente e tempo passato preciso, 'said me' non è la costruzione corretta, 'told that' richiede normalmente un oggetto come 'me' o 'him'. "
            "Traduzione domanda: \"Scegli la frase corretta nel discorso indiretto.\" "
            "Traduzione risposta: \"Ha detto che era stanca.\""
        )
    },

    "ING-AV-0203": {
        "opzioni": [
            "Rarely have I seen such a clear explanation.",
            "Rarely I have seen such a clear explanation.",
            "Rarely have seen I such a clear explanation.",
            "Rarely I seen have such a clear explanation."
        ],
        "spiegazione": (
            "Dopo un avverbio negativo o limitativo all'inizio della frase, come 'rarely', si usa l'inversione tra ausiliare e soggetto. "
            "La forma corretta è 'Rarely have I seen such a clear explanation'. "
            "Le altre opzioni mantengono l'ordine normale o spostano male ausiliare, soggetto e verbo. "
            "Traduzione domanda: \"Scegli l'inversione corretta dopo un avverbio negativo.\" "
            "Traduzione risposta: \"Raramente ho visto una spiegazione così chiara.\""
        )
    },

    "ING-AV-0204": {
        "opzioni": [
            "Despite the rain, we went out.",
            "Despite it was raining, we went out.",
            "Despite of the rain, we went out.",
            "Despite raining was, we went out."
        ],
        "spiegazione": (
            "'Despite' è seguito da un nome, un pronome o una forma in -ing, non da una frase completa con soggetto e verbo finito. "
            "La frase corretta è 'Despite the rain, we went out'. "
            "'Despite it was raining' richiederebbe 'although', 'despite of' non è la forma standard, 'despite raining was' ha ordine scorretto. "
            "Traduzione domanda: \"Scegli la frase con l'uso corretto di despite.\" "
            "Traduzione risposta: \"Nonostante la pioggia, siamo usciti.\""
        )
    },

    "ING-AV-0205": {
        "opzioni": [
            "The man standing by the door is my uncle.",
            "The man who is standing by the door is my uncle.",
            "The man who standing by the door is my uncle.",
            "The man stood by the door is my uncle."
        ],
        "spiegazione": (
            "Una reduced relative clause può eliminare 'who is' e mantenere il participio presente. "
            "Da 'The man who is standing by the door' si ottiene 'The man standing by the door'. "
            "'Who is standing' è grammaticalmente corretto ma non è la relativa ridotta richiesta. "
            "'Who standing' manca di 'is', mentre 'stood' non costruisce correttamente questa riduzione. "
            "Traduzione domanda: \"Scegli la frase corretta con una relativa ridotta.\" "
            "Traduzione risposta: \"L'uomo in piedi vicino alla porta è mio zio.\""
        )
    },

    "ING-AV-0206": {
        "opzioni": [
            "Hardly had we arrived when it started to rain.",
            "Hardly we had arrived when it started to rain.",
            "Hardly had arrived we when it started to rain.",
            "Hardly we arrived had when it started to rain."
        ],
        "spiegazione": (
            "Quando 'hardly' è all'inizio della frase, si usa l'inversione con l'ausiliare. "
            "La forma corretta è 'Hardly had we arrived when it started to rain'. "
            "Le altre opzioni mantengono l'ordine normale o spostano male ausiliare e soggetto. "
            "Traduzione domanda: \"Dopo hardly all'inizio della frase, qual è l'ordine corretto delle parole?\" "
            "Traduzione risposta: \"Eravamo appena arrivati quando ha iniziato a piovere.\""
        )
    },

    "ING-AV-0207": {
        "opzioni": [
            "If I had studied medicine, I would be a doctor now.",
            "If I studied medicine, I would have been a doctor now.",
            "If I had study medicine, I would be a doctor now.",
            "If I have studied medicine, I would be a doctor now."
        ],
        "spiegazione": (
            "Il mixed conditional può collegare una condizione passata irreale a un risultato presente. "
            "La frase corretta è 'If I had studied medicine, I would be a doctor now'. "
            "'If I studied' non esprime chiaramente la condizione passata irreale, 'had study' usa la forma sbagliata, 'have studied' non è la struttura richiesta. "
            "Traduzione domanda: \"Quale frase collega una condizione irreale passata a un risultato presente?\" "
            "Traduzione risposta: \"Se avessi studiato medicina, ora sarei medico.\""
        )
    },

    "ING-AV-0208": {
        "opzioni": [
            "It was John who solved the problem.",
            "It was John which solved the problem.",
            "It John was who solved the problem.",
            "It was John solved who the problem."
        ],
        "spiegazione": (
            "La cleft sentence 'It was John who...' mette enfasi sulla persona che ha compiuto l'azione. "
            "La frase corretta è 'It was John who solved the problem'. "
            "'Which' non è adatto per una persona in questa struttura, mentre le altre opzioni hanno ordine delle parole scorretto. "
            "Traduzione domanda: \"Quale frase scissa mette in evidenza John come persona che ha risolto il problema?\" "
            "Traduzione risposta: \"È stato John a risolvere il problema.\""
        )
    },

    "ING-AV-0209": {
        "opzioni": [
            "I would appreciate it if you could send me the document.",
            "I would appreciate if you could send me the document.",
            "I want you to send me the document now.",
            "Send me the document because I need it."
        ],
        "spiegazione": (
            "'I would appreciate it if you could send me the document' è una richiesta formale, cortese e grammaticalmente corretta. "
            "La versione senza 'it' è meno completa nella struttura standard. "
            "'I want you to send me the document now' è troppo diretta, mentre 'Send me the document because I need it' non è adatta a una richiesta professionale cortese. "
            "Traduzione domanda: \"Quale opzione è il modo più cortese per chiedere a qualcuno di inviare un documento?\" "
            "Traduzione risposta: \"Le sarei grato se potesse inviarmi il documento.\""
        )
    },

    "ING-AV-0210": {
        "opzioni": [
            "No sooner had I left than the phone rang.",
            "No sooner I had left than the phone rang.",
            "No sooner had left I than the phone rang.",
            "No sooner I left had than the phone rang."
        ],
        "spiegazione": (
            "Quando 'no sooner' è all'inizio della frase, si usa l'inversione con l'ausiliare e poi si collega la seconda azione con 'than'. "
            "La frase corretta è 'No sooner had I left than the phone rang'. "
            "Le altre opzioni non applicano correttamente l'inversione o spostano male soggetto e ausiliare. "
            "Traduzione domanda: \"Seleziona l'opzione che usa correttamente no sooner con than.\" "
            "Traduzione risposta: \"Non appena ero uscito, il telefono ha squillato.\""
        )
    },

    "ING-AV-0211": {
        "opzioni": [
            "What I need is a clear plan.",
            "What I need it is a clear plan.",
            "What need I is a clear plan.",
            "What I need are a clear plan."
        ],
        "spiegazione": (
            "'What I need is...' è una struttura enfatica corretta per mettere in evidenza ciò che serve. "
            "La frase corretta è 'What I need is a clear plan'. "
            "'What I need it is' aggiunge un pronome inutile, 'What need I' inverte male le parole, 'are' non concorda con 'a clear plan'. "
            "Traduzione domanda: \"Scegli la struttura enfatica corretta.\" "
            "Traduzione risposta: \"Quello di cui ho bisogno è un piano chiaro.\""
        )
    },

    "ING-AV-0212": {
        "opzioni": [
            "unless you leave now",
            "unless you will leave now",
            "unless you left now",
            "unless you leaving now"
        ],
        "spiegazione": (
            "'Unless' significa 'a meno che non' e, per un risultato futuro, introduce di solito una condizione al present simple. "
            "La forma corretta è 'You will miss the train unless you leave now'. "
            "'Unless you will leave' usa il futuro nella subordinata, 'left' usa il passato, 'leaving' manca del verbo finito. "
            "Traduzione domanda: \"Completa la condizione con unless: perderai il treno a meno che tu non parta ora.\" "
            "Traduzione risposta: \"a meno che tu non parta ora\""
        )
    },

    "ING-AV-0213": {
        "opzioni": [
            "Having finished the report, she sent it to her manager.",
            "Having finish the report, she sent it to her manager.",
            "Finished having the report, she sent it to her manager.",
            "Having finished the report, she sends it yesterday."
        ],
        "spiegazione": (
            "'Having finished' indica un'azione completata prima dell'azione principale. "
            "La frase corretta è 'Having finished the report, she sent it to her manager'. "
            "'Having finish' usa la forma base invece del participio, 'Finished having' cambia struttura, 'she sends it yesterday' mescola presente e tempo passato preciso. "
            "Traduzione domanda: \"Scegli la frase corretta con una participle clause.\" "
            "Traduzione risposta: \"Dopo aver finito il rapporto, lo ha inviato al suo responsabile.\""
        )
    },

    "ING-AV-0214": {
        "opzioni": [
            "I would rather stay at home tonight.",
            "I would rather to stay at home tonight.",
            "I rather would staying at home tonight.",
            "I would rather stayed at home tonight."
        ],
        "spiegazione": (
            "'Would rather' è seguito dal verbo base senza 'to'. "
            "La frase corretta è 'I would rather stay at home tonight'. "
            "'Would rather to stay' aggiunge 'to' in modo errato, 'rather would staying' ha ordine e forma sbagliati, 'would rather stayed' usa il passato invece della forma base. "
            "Traduzione domanda: \"Scegli la frase corretta con would rather.\" "
            "Traduzione risposta: \"Preferirei restare a casa stasera.\""
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
        "# Miglioramento Inglese - quarto blocco distrattori forti",
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

    print("===== MIGLIORAMENTO INGLESE - QUARTO BLOCCO =====")
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
    print("OK: quarto blocco Inglese aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
