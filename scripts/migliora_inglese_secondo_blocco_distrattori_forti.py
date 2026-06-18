import json
from pathlib import Path

FILE = Path("data/inglese.json")
BACKUP = Path("data/inglese.backup_prima_secondo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_inglese_secondo_blocco_distrattori_forti.md")

PATCH = {
    "ING-FAC-0101": {
        "opzioni": [
            "window",
            "wall",
            "door",
            "floor"
        ],
        "spiegazione": (
            "'Window' significa finestra. "
            "'Wall' significa muro, 'door' significa porta e 'floor' significa pavimento. "
            "Sono parole vicine perché appartengono tutte all'ambiente di una stanza, ma solo 'window' traduce correttamente 'finestra'. "
            "Traduzione domanda: \"Quale parola inglese significa 'finestra'?\" "
            "Traduzione risposta: \"finestra\""
        )
    },

    "ING-INT-0101": {
        "opzioni": [
            "since",
            "for",
            "during",
            "from"
        ],
        "spiegazione": (
            "Con il present perfect si usa 'since' quando si indica il punto di inizio di un'azione, come un anno preciso: 'since 2020'. "
            "'For' si usa con una durata, per esempio 'for three years'. "
            "'During' indica durante un periodo, mentre 'from' da solo non è la forma naturale in questa frase. "
            "Traduzione domanda: \"Completa la frase: Vivo a Roma ___ 2020.\" "
            "Traduzione risposta: \"dal\""
        )
    },

    "ING-AV-0101": {
        "opzioni": [
            "nevertheless",
            "therefore",
            "because",
            "provided that"
        ],
        "spiegazione": (
            "'Nevertheless' introduce un contrasto: il software è affidabile, ciononostante ha bisogno di manutenzione regolare. "
            "'Therefore' indica conseguenza, 'because' indica causa e 'provided that' introduce una condizione. "
            "Traduzione domanda: \"Completa la frase: Il software è affidabile; ___, ha comunque bisogno di manutenzione regolare.\" "
            "Traduzione risposta: \"ciononostante\""
        )
    },

    "ING-FAC-0102": {
        "opzioni": [
            "I",
            "You",
            "He",
            "They"
        ],
        "spiegazione": (
            "Con il verbo 'am' si usa il soggetto 'I'. "
            "La frase corretta è 'I am from Italy'. "
            "'You' richiede 'are', 'he' richiede 'is' e 'they' richiede 'are'. "
            "Traduzione domanda: \"Completa la frase: ___ vengo dall'Italia.\" "
            "Traduzione risposta: \"io\""
        )
    },

    "ING-INT-0102": {
        "opzioni": [
            "much",
            "many",
            "few",
            "several"
        ],
        "spiegazione": (
            "'Information' in inglese è normalmente non numerabile. "
            "Con i nomi non numerabili si usa 'much', quindi la frase corretta è 'There isn't much information on the website'. "
            "'Many', 'few' e 'several' si usano con nomi numerabili plurali. "
            "Traduzione domanda: \"Completa la frase: Non ci sono ___ informazioni sul sito web.\" "
            "Traduzione risposta: \"molte\""
        )
    },

    "ING-AV-0102": {
        "opzioni": [
            "The server that hosts the database is offline.",
            "The server who hosts the database is offline.",
            "The server where hosts the database is offline.",
            "The server whose hosts the database is offline."
        ],
        "spiegazione": (
            "Per riferirsi a una cosa, come 'server', si può usare 'that' o 'which'. "
            "'The server that hosts the database is offline' è corretto. "
            "'Who' si usa per persone, 'where hosts' non costruisce correttamente la relativa e 'whose hosts' usa male il possessivo. "
            "Traduzione domanda: \"Quale frase usa correttamente una proposizione relativa riferita a un server?\" "
            "Traduzione risposta: \"Il server che ospita il database è offline.\""
        )
    },

    "ING-FAC-0103": {
        "opzioni": [
            "His",
            "Her",
            "Their",
            "Our"
        ],
        "spiegazione": (
            "Marco è maschile singolare, quindi il possessivo corretto è 'his'. "
            "'Her' si usa per femminile singolare, 'their' per loro e 'our' per nostro. "
            "La frase corretta è 'This is Marco. His phone is new'. "
            "Traduzione domanda: \"Completa la frase: Questo è Marco. ___ telefono è nuovo.\" "
            "Traduzione risposta: \"il suo\""
        )
    },

    "ING-INT-0103": {
        "opzioni": [
            "learning",
            "to learn",
            "learn",
            "learned"
        ],
        "spiegazione": (
            "Dopo il verbo 'enjoy' si usa normalmente il verbo in -ing. "
            "La frase corretta è 'I enjoy learning new programming languages'. "
            "'To learn', 'learn' e 'learned' sono forme vicine al verbo corretto, ma non rispettano la costruzione richiesta da 'enjoy'. "
            "Traduzione domanda: \"Completa la frase: Mi piace ___ nuovi linguaggi di programmazione.\" "
            "Traduzione risposta: \"imparare\""
        )
    },

    "ING-AV-0103": {
        "opzioni": [
            "The issue has been fixed.",
            "The issue has fixed.",
            "The issue was been fixed.",
            "The issue has been fix."
        ],
        "spiegazione": (
            "La frase corretta usa il passivo al present perfect: 'has been' + participio passato. "
            "'The issue has been fixed' è corretta perché comunica il risultato senza specificare chi ha risolto il problema. "
            "'Has fixed' è attivo e richiederebbe un soggetto agente, 'was been fixed' combina male due forme di 'to be', 'has been fix' usa la forma base invece del participio 'fixed'. "
            "Traduzione domanda: \"In un report tecnico, quale frase indica che il problema è stato risolto senza specificare chi lo ha risolto?\" "
            "Traduzione risposta: \"Il problema è stato risolto.\""
        )
    },

    "ING-FAC-0104": {
        "opzioni": [
            "Do you like coffee?",
            "You like coffee?",
            "Does you like coffee?",
            "Are you like coffee?"
        ],
        "spiegazione": (
            "Nel present simple, con 'you' si usa l'ausiliare 'do' per formare la domanda. "
            "La frase corretta è 'Do you like coffee?'. "
            "'You like coffee?' può essere colloquiale ma non è la forma grammaticale richiesta. "
            "'Does you' sbaglia ausiliare, mentre 'Are you like coffee?' mescola il verbo 'to be' con il verbo principale 'like'. "
            "Traduzione domanda: \"Quale frase è una domanda corretta al presente semplice?\" "
            "Traduzione risposta: \"Ti piace il caffè?\""
        )
    },

    "ING-INT-0104": {
        "opzioni": [
            "to",
            "for",
            "than",
            "that"
        ],
        "spiegazione": (
            "La struttura corretta è 'too + aggettivo + to + verbo'. "
            "Quindi si dice 'The file is too large to upload'. "
            "'For', 'than' e 'that' sono parole grammaticali possibili in altre strutture, ma non completano correttamente questa costruzione. "
            "Traduzione domanda: \"Completa la frase: Il file è troppo grande ___ caricarlo.\" "
            "Traduzione risposta: \"per\""
        )
    },

    "ING-AV-0104": {
        "opzioni": [
            "They said they would release the update the next day.",
            "They said they will release the update tomorrow.",
            "They said they released the update the next day.",
            "They said they had released the update the next day."
        ],
        "spiegazione": (
            "Nel discorso indiretto con backshift, 'will' diventa spesso 'would' e 'tomorrow' diventa 'the next day'. "
            "La trasformazione corretta è 'They said they would release the update the next day'. "
            "'Will' e 'tomorrow' non applicano il backshift standard, 'released' cambia il futuro in passato semplice, 'had released' indica un'azione già completata prima del momento del discorso. "
            "Traduzione domanda: \"Trasforma correttamente in discorso indiretto: 'We will release the update tomorrow.'\" "
            "Traduzione risposta: \"Dissero che avrebbero rilasciato l'aggiornamento il giorno seguente.\""
        )
    },

    "ING-FAC-0105": {
        "opzioni": [
            "by",
            "on",
            "at",
            "with"
        ],
        "spiegazione": (
            "Per indicare il mezzo di trasporto in generale si usa 'by': by bus, by train, by car. "
            "La frase corretta è 'I go to work by bus'. "
            "'On' può comparire in espressioni come 'on the bus', ma non nella struttura generale 'by bus'. "
            "'At' indica luogo o punto, mentre 'with' significa con. "
            "Traduzione domanda: \"Completa la frase: Vado al lavoro ___ autobus.\" "
            "Traduzione risposta: \"in\""
        )
    },

    "ING-INT-0105": {
        "opzioni": [
            "would start",
            "will start",
            "started",
            "start"
        ],
        "spiegazione": (
            "Questa frase usa il second conditional: if + past simple, would + verbo base. "
            "La forma corretta è 'If I had more time, I would start a second project'. "
            "'Will start' appartiene al first conditional, 'started' è solo passato, 'start' manca dell'ausiliare 'would'. "
            "Traduzione domanda: \"Completa la frase: Se avessi più tempo, ___ un secondo progetto.\" "
            "Traduzione risposta: \"inizierei\""
        )
    },

    "ING-AV-0105": {
        "opzioni": [
            "would have fixed",
            "will have fixed",
            "would fix",
            "had fixed"
        ],
        "spiegazione": (
            "Questa frase usa il third conditional: If + past perfect, would have + participio passato. "
            "La forma corretta è 'If I had known about the error, I would have fixed it earlier'. "
            "'Will have fixed' usa il futuro perfetto, 'would fix' appartiene più al second conditional, 'had fixed' non completa correttamente la frase principale. "
            "Traduzione domanda: \"Completa la frase: Se avessi saputo dell'errore, lo ___ prima.\" "
            "Traduzione risposta: \"avrei corretto\""
        )
    },

    "ING-FAC-0106": {
        "opzioni": [
            "can",
            "must",
            "should",
            "will"
        ],
        "spiegazione": (
            "'Can' indica capacità. "
            "'I can swim' significa 'so nuotare'. "
            "'Must' indica obbligo, 'should' consiglio e 'will' futuro. "
            "Traduzione domanda: \"Completa la frase: Io ___ nuotare, ma non so guidare.\" "
            "Traduzione risposta: \"so\""
        )
    },

    "ING-INT-0106": {
        "opzioni": [
            "configurare",
            "spegnere",
            "cercare",
            "rimandare"
        ],
        "spiegazione": (
            "'Set up' significa configurare, preparare o impostare qualcosa. "
            "Nella frase 'I need to set up the app' significa 'devo configurare l'app'. "
            "'Spegnere' corrisponde a 'turn off', 'cercare' a 'look for' o 'search', 'rimandare' a 'postpone' o 'put off'. "
            "Traduzione domanda: \"Nella frase 'I need to set up the app', che cosa significa 'set up'?\" "
            "Traduzione risposta: \"configurare\""
        )
    },

    "ING-AV-0106": {
        "opzioni": [
            "L'app si è bloccata durante l'avvio.",
            "L'app ha migliorato l'avvio.",
            "L'app è stata aggiornata durante l'avvio.",
            "L'app ha ignorato l'avvio."
        ],
        "spiegazione": (
            "Nel contesto software, 'to crash' significa bloccarsi, chiudersi in modo anomalo o andare in errore. "
            "'During startup' significa durante l'avvio. "
            "Quindi 'The app crashed during startup' significa 'L'app si è bloccata durante l'avvio'. "
            "Le altre opzioni cambiano il significato di 'crashed'. "
            "Traduzione domanda: \"Nel contesto software, quale traduzione rende meglio 'The app crashed during startup'?\" "
            "Traduzione risposta: \"L'app si è bloccata durante l'avvio.\""
        )
    },

    "ING-INT-0107": {
        "opzioni": [
            "faster",
            "fastest",
            "more fast",
            "fastly"
        ],
        "spiegazione": (
            "Con un aggettivo breve come 'fast', il comparativo si forma aggiungendo -er: 'faster'. "
            "La frase corretta è 'This laptop is faster than my old one'. "
            "'Fastest' è superlativo, 'more fast' non è la forma standard, 'fastly' non è l'avverbio corretto in inglese comune. "
            "Traduzione domanda: \"Completa la frase: Questo portatile è ___ del mio vecchio.\" "
            "Traduzione risposta: \"più veloce\""
        )
    },

    "ING-AV-0107": {
        "opzioni": [
            "Could you please send me the updated file?",
            "Send me the file now.",
            "Give me that file quickly.",
            "You send the file to me."
        ],
        "spiegazione": (
            "'Could you please send me the updated file?' è una richiesta educata e professionale. "
            "'Send me the file now' e 'Give me that file quickly' sono troppo dirette. "
            "'You send the file to me' è poco naturale come richiesta professionale. "
            "Traduzione domanda: \"Quale frase è più adatta in una comunicazione professionale?\" "
            "Traduzione risposta: \"Potresti per favore inviarmi il file aggiornato?\""
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
        "# Miglioramento Inglese - secondo blocco distrattori forti",
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

    print("===== MIGLIORAMENTO INGLESE - SECONDO BLOCCO =====")
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
    print("OK: secondo blocco Inglese aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
