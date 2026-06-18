import json
from pathlib import Path

FILE = Path("data/logica/logica_verbale.json")
BACKUP = Path("backups/logica_verbale.backup_prima_secondo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_logica_secondo_blocco_distrattori_forti.md")

PATCH = {
    "LOG-VER-FAC-0001": {
        "opzioni": [
            "FE",
            "EF",
            "FG",
            "GF"
        ],
        "spiegazione": (
            "La regola inverte l'ordine delle due lettere. "
            "AB diventa BA e CD diventa DC. "
            "Seguendo la stessa logica, EF diventa FE. "
            "EF non applica l'inversione, FG cambia una lettera, GF inverte una coppia diversa."
        )
    },

    "LOG-VER-INT-0002": {
        "opzioni": [
            "tagliare",
            "incollare",
            "misurare",
            "disegnare"
        ],
        "spiegazione": (
            "La relazione è tra uno strumento e la sua funzione principale. "
            "La penna serve principalmente per scrivere; le forbici servono principalmente per tagliare. "
            "Incollare, misurare e disegnare sono azioni possibili con altri strumenti, ma non sono la funzione principale delle forbici."
        )
    },

    "LOG-VER-AV-0003": {
        "opzioni": [
            "indizio → ipotesi",
            "prova → verdetto",
            "errore → correzione",
            "causa → conseguenza"
        ],
        "spiegazione": (
            "Un sintomo è un segnale che aiuta a formulare una diagnosi, senza coincidere con una certezza finale. "
            "Allo stesso modo, un indizio aiuta a formulare un'ipotesi. "
            "Prova → verdetto è più vicino a decisione conclusiva, errore → correzione indica soluzione di un problema, causa → conseguenza indica rapporto diretto di produzione."
        )
    },

    "LOG-VER-INT-0004": {
        "opzioni": [
            "prototipo → prodotto definitivo",
            "bozza → revisione",
            "idea → progetto iniziale",
            "indice → documento finale"
        ],
        "spiegazione": (
            "Una bozza è una versione iniziale che può evolvere in un documento finale. "
            "Allo stesso modo, un prototipo è una versione iniziale che può evolvere in un prodotto definitivo. "
            "Bozza → revisione indica solo una fase intermedia. "
            "Idea → progetto iniziale resta ancora nella fase iniziale. "
            "Indice → documento finale collega una parte al documento, non una versione iniziale alla versione conclusiva."
        )
    },

    "LOG-VER-FAC-0101": {
        "opzioni": [
            "basso",
            "piccolo",
            "lungo",
            "vicino"
        ],
        "spiegazione": (
            "La relazione è di opposizione diretta. "
            "Caldo e freddo sono contrari; allo stesso modo, alto e basso sono contrari. "
            "Piccolo riguarda la dimensione, lungo riguarda la lunghezza, vicino riguarda la distanza: sono concetti collegati allo spazio, ma non sono il contrario diretto di alto."
        )
    },

    "LOG-VER-INT-0101": {
        "opzioni": [
            "scuola",
            "classe",
            "lezione",
            "libro"
        ],
        "spiegazione": (
            "La relazione è tra una professione e il luogo generale in cui viene svolta. "
            "Il medico lavora tipicamente in ospedale; l'insegnante lavora tipicamente in una scuola. "
            "Classe e lezione sono collegate all'insegnamento, ma sono più specifiche. "
            "Libro è uno strumento o materiale, non il luogo equivalente."
        )
    },

    "LOG-VER-AV-0101": {
        "opzioni": [
            "apprendimento",
            "interrogazione",
            "lezione",
            "materia"
        ],
        "spiegazione": (
            "La relazione è tra un'attività e il risultato che può produrre. "
            "L'allenamento può portare a un miglioramento; lo studio può portare ad apprendimento. "
            "Interrogazione, lezione e materia appartengono al contesto scolastico, ma non sono il risultato diretto dello studio."
        )
    },

    "LOG-VER-FAC-0102": {
        "opzioni": [
            "martello",
            "armadio",
            "tavolo",
            "sedia"
        ],
        "spiegazione": (
            "Tavolo, sedia e armadio sono mobili. "
            "Martello è un attrezzo, quindi non appartiene allo stesso gruppo. "
            "Le altre opzioni sono plausibili perché sono oggetti domestici, ma condividono la categoria dei mobili."
        )
    },

    "LOG-VER-INT-0102": {
        "opzioni": [
            "uovo: uccello",
            "germoglio: pianta",
            "foglia: ramo",
            "frutto: albero"
        ],
        "spiegazione": (
            "La relazione è tra un punto di origine e ciò che può svilupparsi da esso. "
            "Dal seme può svilupparsi una pianta; dall'uovo può svilupparsi un uccello. "
            "Germoglio: pianta è vicino, ma il germoglio è già una fase successiva. "
            "Foglia: ramo e frutto: albero indicano parti o prodotti collegati, non l'origine dello sviluppo."
        )
    },

    "LOG-VER-AV-0103": {
        "opzioni": [
            "quadri",
            "cataloghi",
            "sculture",
            "cornici"
        ],
        "spiegazione": (
            "La relazione è tra un luogo di raccolta e il tipo principale di opere o oggetti che contiene. "
            "Una biblioteca raccoglie libri; una pinacoteca raccoglie ed espone quadri. "
            "Cataloghi e cornici sono oggetti collegati, ma non sono il contenuto principale. "
            "Sculture appartengono più a un museo o a una galleria d'arte in senso diverso."
        )
    },

    "LOG-VER-0201": {
        "opzioni": [
            "Scuola",
            "Classe",
            "Aula",
            "Biblioteca"
        ],
        "spiegazione": (
            "La relazione è tra una professione e il luogo tipico di lavoro. "
            "Il medico lavora tipicamente in ospedale; l'insegnante lavora tipicamente a scuola. "
            "Classe e aula sono luoghi più specifici dentro la scuola. "
            "Biblioteca è un luogo di studio, ma non è il luogo generale equivalente dell'insegnante."
        )
    },

    "LOG-VER-0202": {
        "opzioni": [
            "Robusto",
            "Delicato",
            "Leggero",
            "Sottile"
        ],
        "spiegazione": (
            "Fragile indica qualcosa che si rompe facilmente. "
            "Il contrario più adatto è robusto, cioè resistente. "
            "Delicato è vicino a fragile, leggero riguarda il peso, sottile riguarda lo spessore."
        )
    },

    "LOG-VER-0203": {
        "opzioni": [
            "Rosa",
            "Cane",
            "Gatto",
            "Leone"
        ],
        "spiegazione": (
            "Cane, gatto e leone sono animali. "
            "Rosa è un fiore, quindi non appartiene allo stesso gruppo. "
            "Le altre tre parole appartengono alla stessa categoria generale degli animali."
        )
    },

    "LOG-VER-0204": {
        "opzioni": [
            "Prodotti",
            "Scaffali",
            "Carrelli",
            "Corsie"
        ],
        "spiegazione": (
            "La relazione è tra un luogo e ciò che vi si trova principalmente. "
            "In biblioteca si trovano libri; in supermercato si trovano prodotti da acquistare. "
            "Scaffali, carrelli e corsie sono elementi presenti in un supermercato, ma non rappresentano il contenuto principale equivalente ai libri."
        )
    },

    "LOG-VER-0205": {
        "opzioni": [
            "Penna",
            "Tastiera",
            "Libro",
            "Carta"
        ],
        "spiegazione": (
            "La relazione è tra una persona e lo strumento principale usato nella sua attività. "
            "Il pittore usa il pennello; lo scrittore usa la penna come strumento di scrittura. "
            "Tastiera è plausibile in contesto moderno, ma cambia lo strumento classico dell'analogia. "
            "Libro e carta sono collegati alla scrittura, ma non sono lo strumento equivalente al pennello."
        )
    },

    "LOG-VER-0206": {
        "opzioni": [
            "Tutti i poeti sono scrittori",
            "Alcuni scrittori sono insegnanti",
            "Tutti gli scrittori sono poeti",
            "Tutti gli insegnanti sono poeti"
        ],
        "spiegazione": (
            "La conclusione sicuramente vera è quella già garantita dalla premessa: tutti i poeti sono scrittori. "
            "Anche 'alcuni scrittori sono insegnanti' è una premessa, ma non risponde alla relazione sui poeti. "
            "Non si può dedurre che tutti gli scrittori siano poeti, né che tutti gli insegnanti siano poeti."
        )
    },

    "LOG-VER-0207": {
        "opzioni": [
            "Preciso",
            "Attento",
            "Veloce",
            "Imprevisto"
        ],
        "spiegazione": (
            "Accurato significa fatto con cura, attenzione e precisione. "
            "La parola più vicina è preciso. "
            "Attento è collegato, ma indica più l'atteggiamento che il risultato. "
            "Veloce e imprevisto cambiano completamente il significato."
        )
    },

    "LOG-VER-0208": {
        "opzioni": [
            "Tutte le serre sono strutture chiuse",
            "Alcune strutture chiuse sono riscaldate",
            "Tutte le serre sono riscaldate",
            "Alcune serre non sono strutture chiuse"
        ],
        "spiegazione": (
            "La conclusione certa è che tutte le serre sono strutture chiuse, perché è indicato direttamente dalla prima premessa. "
            "La frase 'alcune strutture chiuse sono riscaldate' è una premessa, ma non permette di stabilire quali strutture siano serre. "
            "Non si può dedurre che tutte le serre siano riscaldate. "
            "Dire che alcune serre non sono strutture chiuse contraddice la prima premessa."
        )
    },

    "LOG-VER-0209": {
        "opzioni": [
            "Allenamento e miglioramento",
            "Pioggia e ombrello",
            "Libro e scaffale",
            "Finestra e stanza"
        ],
        "spiegazione": (
            "La relazione richiesta è di causa o attività che produce un risultato. "
            "Lo studio può produrre preparazione; allo stesso modo, l'allenamento può produrre miglioramento. "
            "Pioggia e ombrello sono collegati da bisogno o protezione, non da miglioramento prodotto. "
            "Libro e scaffale indicano oggetto e supporto. "
            "Finestra e stanza indicano parte e luogo."
        )
    },

    "LOG-VER-0210": {
        "opzioni": [
            "Per guidare serve la patente",
            "Per guidare può servire una strada libera",
            "Studio anche se sono stanco",
            "Parto oppure resto"
        ],
        "spiegazione": (
            "Una condizione necessaria indica qualcosa che deve esserci perché una certa azione sia possibile o valida. "
            "La frase 'Per guidare serve la patente' indica che la patente è necessaria per guidare legalmente. "
            "Una strada libera può aiutare ma non è la condizione logica richiesta. "
            "Anche se indica contrasto, mentre oppure indica alternativa."
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
        raise SystemExit("ERRORE: data/logica/logica_verbale.json non trovato.")

    BACKUP.parent.mkdir(parents=True, exist_ok=True)

    if not BACKUP.exists():
        BACKUP.write_text(FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato fuori dai dati ufficiali: {BACKUP}")
    else:
        print(f"Backup già presente fuori dai dati ufficiali: {BACKUP}")

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
            "Ogni risposta errata deve essere semanticamente vicina alla corretta, "
            "ma sbagliata per una relazione logica precisa: categoria diversa, funzione non principale, "
            "luogo troppo specifico, causa confusa, opposizione non diretta o deduzione non garantita."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Logica - secondo blocco distrattori forti",
        "",
        "File aggiornato: `data/logica/logica_verbale.json`",
        "",
        "Backup salvato fuori dai dati ufficiali: `backups/logica_verbale.backup_prima_secondo_blocco_distrattori_forti.json`",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: distrattori semanticamente vicini e sbagliati per una relazione logica precisa.",
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

    print("===== MIGLIORAMENTO LOGICA - SECONDO BLOCCO =====")
    print("File: data/logica/logica_verbale.json")
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
    print("OK: secondo blocco Logica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
