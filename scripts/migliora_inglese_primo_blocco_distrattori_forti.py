import json
from pathlib import Path

FILE = Path("data/inglese.json")
BACKUP = Path("data/inglese.backup_prima_primo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_inglese_primo_blocco_distrattori_forti.md")

PATCH = {
    "ING-FAC-0001": {
        "opzioni": [
            "She has a blue backpack.",
            "She have a blue backpack.",
            "She has blue backpack.",
            "She is has a blue backpack."
        ],
        "spiegazione": (
            "Con 'she' al presente semplice si usa 'has'. "
            "'She have a blue backpack' sbaglia la concordanza del verbo. "
            "'She has blue backpack' manca dell'articolo 'a'. "
            "'She is has a blue backpack' mescola due verbi ausiliari in modo errato. "
            "Traduzione domanda: \"Quale frase usa correttamente il presente semplice con il soggetto 'lei'?\" "
            "Traduzione risposta: \"Lei ha uno zaino blu.\""
        )
    },

    "ING-INT-0002": {
        "opzioni": [
            "I have just finished my homework.",
            "I have just finish my homework.",
            "I just finished my homework.",
            "I have finished my homework yesterday."
        ],
        "spiegazione": (
            "Il present perfect si forma con 'have/has' + participio passato. "
            "'I have just finished my homework' è corretto perché usa 'have' + 'finished'. "
            "'I have just finish' usa la forma base invece del participio passato. "
            "'I just finished' è past simple, mentre con 'yesterday' di solito si usa il past simple e non il present perfect. "
            "Traduzione domanda: \"Quale frase usa correttamente il present perfect?\" "
            "Traduzione risposta: \"Ho appena finito i miei compiti.\""
        )
    },

    "ING-AV-0003": {
        "opzioni": [
            "yet",
            "because",
            "therefore",
            "although"
        ],
        "spiegazione": (
            "'Yet' è corretto perché introduce un contrasto tra due idee: l'app è semplice da usare, ma offre anche funzioni avanzate. "
            "'Because' introduce una causa, 'therefore' una conseguenza. "
            "'Although' esprime contrasto, ma in questa posizione dopo la virgola non completa la frase in modo naturale come 'yet'. "
            "Traduzione domanda: \"Completa la frase scegliendo il connettivo più adatto: L'app è semplice da usare, ___ offre funzionalità avanzate per utenti esperti.\" "
            "Traduzione risposta: \"eppure\""
        )
    },

    "ING-FAC-0004": {
        "opzioni": [
            "They are students.",
            "They is students.",
            "They are student.",
            "They am students."
        ],
        "spiegazione": (
            "'They are students' è corretto perché 'they' richiede 'are' e il nome deve essere al plurale: 'students'. "
            "'They is students' usa il verbo sbagliato. "
            "'They are student' sbaglia il plurale del nome. "
            "'They am students' usa una forma verbale che si usa con 'I', non con 'they'. "
            "Traduzione domanda: \"Quale frase usa correttamente il presente con il soggetto 'they'?\" "
            "Traduzione risposta: \"Loro sono studenti.\""
        )
    },

    "ING-INT-0004": {
        "opzioni": [
            "She visited London last year.",
            "She has visited London last year.",
            "She visit London last year.",
            "She was visited London last year."
        ],
        "spiegazione": (
            "Con un tempo passato preciso come 'last year' si usa il past simple. "
            "'She visited London last year' è corretto. "
            "'She has visited London last year' mescola present perfect e tempo passato preciso. "
            "'She visit London last year' non usa il passato. "
            "'She was visited London last year' crea una struttura passiva non adatta al significato della frase. "
            "Traduzione domanda: \"Quale frase usa correttamente il past simple?\" "
            "Traduzione risposta: \"Lei ha visitato Londra l'anno scorso.\""
        )
    },

    "ING-AV-0004": {
        "opzioni": [
            "however",
            "therefore",
            "moreover",
            "otherwise"
        ],
        "spiegazione": (
            "'However' introduce un contrasto: il sistema è potente, ma richiede comunque test accurati prima della distribuzione. "
            "'Therefore' indica conseguenza, 'moreover' aggiunge un'informazione nella stessa direzione, mentre 'otherwise' indica un'alternativa o conseguenza se non si fa qualcosa. "
            "Traduzione domanda: \"Completa la frase: Il sistema è potente; ___, richiede test accurati prima della distribuzione.\" "
            "Traduzione risposta: \"tuttavia\""
        )
    },

    "ING-FAC-0005": {
        "opzioni": [
            "an",
            "a",
            "the",
            "some"
        ],
        "spiegazione": (
            "Si usa 'an' davanti a parole che iniziano con suono vocalico, come 'apple'. "
            "'A' si usa davanti a suono consonantico. "
            "'The' indica qualcosa di specifico, mentre 'some' non si usa normalmente con il singolare 'apple' in questa struttura. "
            "Traduzione domanda: \"Completa la frase: Ho ___ mela nella borsa.\" "
            "Traduzione risposta: \"una\""
        )
    },

    "ING-INT-0005": {
        "opzioni": [
            "more difficult",
            "most difficult",
            "more difficulty",
            "difficulter"
        ],
        "spiegazione": (
            "Dopo 'than' serve il comparativo. "
            "Con un aggettivo lungo come 'difficult' si usa 'more difficult'. "
            "'Most difficult' è superlativo, 'more difficulty' usa un nome invece dell'aggettivo, mentre 'difficulter' non è una forma corretta. "
            "Traduzione domanda: \"Completa la frase: Questo esercizio è ___ del precedente.\" "
            "Traduzione risposta: \"più difficile\""
        )
    },

    "ING-AV-0005": {
        "opzioni": [
            "The developer who fixed the bug updated the repository.",
            "The developer which fixed the bug updated the repository.",
            "The developer who fixing the bug updated the repository.",
            "The developer whose fixed the bug updated the repository."
        ],
        "spiegazione": (
            "Per riferirsi a una persona in una frase relativa si usa normalmente 'who'. "
            "'The developer who fixed the bug updated the repository' è corretto. "
            "'Which' si usa più spesso per cose o animali. "
            "'Who fixing' manca del verbo corretto nella relativa. "
            "'Whose' indica possesso e non può sostituire 'who' in questa frase. "
            "Traduzione domanda: \"Scegli la frase corretta:\" "
            "Traduzione risposta: \"Lo sviluppatore che ha corretto il bug ha aggiornato il repository.\""
        )
    },

    "ING-FAC-0006": {
        "opzioni": [
            "cold",
            "warm",
            "cool",
            "dry"
        ],
        "spiegazione": (
            "'Hot' significa caldo. "
            "Il contrario più diretto è 'cold', cioè freddo. "
            "'Warm' significa caldo/tiepido, quindi è vicino ma non contrario. "
            "'Cool' può significare fresco, ma non è il contrario più diretto in questa domanda base. "
            "'Dry' significa asciutto. "
            "Traduzione domanda: \"Quale parola inglese indica il contrario di 'hot'?\" "
            "Traduzione risposta: \"freddo\""
        )
    },

    "ING-INT-0006": {
        "opzioni": [
            "You must wear a helmet.",
            "You should wear a helmet.",
            "You might wear a helmet.",
            "You could wear a helmet."
        ],
        "spiegazione": (
            "'Must' esprime obbligo o necessità forte. "
            "'You should wear a helmet' è un consiglio forte, ma non obbligo pieno. "
            "'Might' e 'could' indicano possibilità, non obbligo. "
            "Traduzione domanda: \"Quale frase esprime meglio un obbligo?\" "
            "Traduzione risposta: \"Devi indossare il casco.\""
        )
    },

    "ING-AV-0006": {
        "opzioni": [
            "The report was reviewed by the team.",
            "The report has been review by the team.",
            "The report is reviewed by the team yesterday.",
            "The report was reviewing by the team."
        ],
        "spiegazione": (
            "La forma passiva corretta usa il verbo 'to be' più il participio passato. "
            "'The report was reviewed by the team' è corretto perché usa 'was reviewed'. "
            "'Has been review' manca del participio passato 'reviewed'. "
            "'Is reviewed yesterday' mescola presente e tempo passato preciso. "
            "'Was reviewing' è progressivo, non passivo corretto in questa frase. "
            "Traduzione domanda: \"Quale frase usa correttamente la forma passiva?\" "
            "Traduzione risposta: \"Il report è stato revisionato dal team.\""
        )
    },

    "ING-FAC-0007": {
        "opzioni": [
            "on",
            "in",
            "at",
            "to"
        ],
        "spiegazione": (
            "Si usa 'on' quando qualcosa si trova sopra una superficie. "
            "'The book is on the table' significa che il libro è sul tavolo. "
            "'In' indica dentro, 'at' indica posizione generica o punto, 'to' indica movimento verso qualcosa. "
            "Traduzione domanda: \"Completa la frase: Il libro è ___ tavolo.\" "
            "Traduzione risposta: \"sul\""
        )
    },

    "ING-INT-0007": {
        "opzioni": [
            "will stay",
            "would stay",
            "stay",
            "stayed"
        ],
        "spiegazione": (
            "Nel first conditional si usa 'if' + present simple e poi 'will' + verbo base. "
            "La frase corretta è: 'If it rains tomorrow, we will stay at home.' "
            "'Would stay' appartiene più al second conditional, 'stay' manca di 'will' nella frase principale, mentre 'stayed' è passato. "
            "Traduzione domanda: \"Completa la frase: Se domani piove, noi ___ a casa.\" "
            "Traduzione risposta: \"resteremo\""
        )
    },

    "ING-AV-0007": {
        "opzioni": [
            "You should consider updating the documentation.",
            "You should update the documentation immediately.",
            "You could update the documentation if necessary.",
            "You must update the documentation now."
        ],
        "spiegazione": (
            "'You should consider updating the documentation' esprime un consiglio formale e prudente. "
            "'You should update the documentation immediately' è più diretto e urgente. "
            "'You could update the documentation if necessary' indica possibilità, non consiglio formale chiaro. "
            "'You must update the documentation now' esprime obbligo immediato. "
            "Traduzione domanda: \"Quale frase esprime meglio un consiglio formale?\" "
            "Traduzione risposta: \"Dovresti valutare di aggiornare la documentazione.\""
        )
    },

    "ING-FAC-0008": {
        "opzioni": [
            "children",
            "childs",
            "childes",
            "childrens"
        ],
        "spiegazione": (
            "'Child' ha un plurale irregolare: 'children'. "
            "'Childs', 'childes' e 'childrens' sembrano forme plurali possibili, ma non sono corrette in inglese standard. "
            "Traduzione domanda: \"Qual è il plurale corretto di 'child'?\" "
            "Traduzione risposta: \"bambini\""
        )
    },

    "ING-INT-0008": {
        "opzioni": [
            "spegnere",
            "accendere",
            "abbassare",
            "staccare"
        ],
        "spiegazione": (
            "'Turn off' significa spegnere. "
            "'Turn on' significa accendere, 'turn down' può significare abbassare, mentre 'unplug' significa staccare o scollegare. "
            "Traduzione domanda: \"Nella frase 'Please turn off the light', che cosa significa 'turn off'?\" "
            "Traduzione risposta: \"spegnere\""
        )
    },

    "ING-AV-0008": {
        "opzioni": [
            "He said that he was working on the project.",
            "He said that he is working on the project.",
            "He said that he had been working on the project.",
            "He said that he worked on the project."
        ],
        "spiegazione": (
            "Con il backshift standard del discorso indiretto, 'I am working' diventa 'he was working'. "
            "'He said that he was working on the project' mantiene l'idea dell'azione in corso. "
            "'Is working' non applica il backshift. "
            "'Had been working' sposta il tempo ancora più indietro. "
            "'Worked' perde l'idea dell'azione in corso. "
            "Traduzione domanda: \"Quale frase trasforma correttamente 'I am working on the project' nel discorso indiretto con backshift standard?\" "
            "Traduzione risposta: \"Lui disse che stava lavorando al progetto.\""
        )
    },

    "ING-INT-0009": {
        "opzioni": [
            "I am looking forward to starting the course.",
            "I am looking forward to start the course.",
            "I am looking for starting the course.",
            "I am looking after starting the course."
        ],
        "spiegazione": (
            "'Look forward to' significa non vedere l'ora di fare qualcosa. "
            "Dopo 'to' in questa espressione si usa il verbo in -ing: 'starting'. "
            "'Looking forward to start' usa la forma verbale sbagliata. "
            "'Looking for' significa cercare, mentre 'looking after' significa prendersi cura di. "
            "Traduzione domanda: \"Quale frase corrisponde meglio a: 'Non vedo l'ora di iniziare il corso'?\" "
            "Traduzione risposta: \"Non vedo l'ora di iniziare il corso.\""
        )
    },

    "ING-AV-0009": {
        "opzioni": [
            "La funzionalità è compatibile con versioni precedenti.",
            "La funzionalità richiede solo versioni successive.",
            "La funzionalità funziona solo se tutte le versioni vecchie vengono rimosse.",
            "La funzionalità è stata riscritta senza garantire compatibilità."
        ],
        "spiegazione": (
            "'Backward compatible' significa che una funzionalità rimane compatibile con versioni precedenti del sistema o del software. "
            "Le altre opzioni sono plausibili nel contesto software, ma indicano compatibilità solo futura, rimozione del supporto alle versioni vecchie o assenza di garanzie. "
            "Traduzione domanda: \"Nel contesto software, quale frase rende meglio 'The feature is backward compatible'?\" "
            "Traduzione risposta: \"La funzionalità è compatibile con versioni precedenti.\""
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
        "# Miglioramento Inglese - primo blocco distrattori forti",
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

    print("===== MIGLIORAMENTO INGLESE - PRIMO BLOCCO =====")
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
    print("OK: primo blocco Inglese aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
