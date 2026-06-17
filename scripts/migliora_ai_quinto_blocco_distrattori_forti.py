import json
from pathlib import Path

FILE_AI = Path("data/ai.json")
BACKUP = Path("data/ai.backup_prima_quinto_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_ai_quinto_blocco_distrattori_forti.md")

PATCH = {
    "AI-FAC-0004": {
        "opzioni": [
            "Esempi usati dal modello per imparare schemi e relazioni",
            "Esempi usati dal modello, ma solo per controllare il risultato dopo l'addestramento",
            "Esempi da cui il modello apprende, ma già trasformati nei parametri finali del modello",
            "Esempi usati nel training, ma scritti come regole manuali per ogni risposta possibile"
        ],
        "spiegazione": (
            "I dati di addestramento sono esempi usati dal modello per imparare schemi e relazioni. "
            "Non sono soltanto dati di controllo dopo il training, non coincidono con i parametri finali e non sono regole manuali scritte risposta per risposta."
        )
    },

    "AI-FAC-0005": {
        "opzioni": [
            "Riassumi questo testo in 5 righe usando un linguaggio semplice",
            "Riassumi questo testo usando un linguaggio semplice, ma senza indicare quanto deve essere breve",
            "Riscrivi questo testo in modo semplice, mantenendo però quasi tutti i dettagli originali",
            "Riformula questo testo con parole più chiare, ma senza chiedere una vera riduzione"
        ],
        "spiegazione": (
            "Il prompt più chiaro specifica compito, lunghezza e stile: riassumere il testo in 5 righe usando un linguaggio semplice. "
            "Gli altri prompt sono vicini, ma mancano il vincolo di lunghezza oppure chiedono una riscrittura invece di un riassunto breve."
        )
    },

    "AI-AV-0009": {
        "opzioni": [
            "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
            "Perché i dati possono introdurre distorsioni, ma obiettivi e metriche restano neutrali",
            "Perché le metriche possono orientare il risultato, ma i dati iniziali hanno un ruolo marginale",
            "Perché gli obiettivi di addestramento possono incidere, ma dati e metriche non modificano il comportamento"
        ],
        "spiegazione": (
            "Un modello può produrre risultati distorti anche con algoritmo implementato correttamente perché dati, obiettivi di addestramento e metriche possono introdurre distorsioni. "
            "Limitare il problema a una sola causa rende la spiegazione incompleta."
        )
    },

    "AI-FAC-0101": {
        "opzioni": [
            "Riconoscere schemi nei dati e usare questi schemi per produrre risposte o previsioni",
            "Riconoscere schemi nei dati, ma usarli principalmente per copiare esempi già presenti",
            "Memorizzare dati ricevuti, ma senza trasformarli in schemi utili per nuove previsioni",
            "Organizzare informazioni digitali, ma senza usarle per rispondere o prevedere casi nuovi"
        ],
        "spiegazione": (
            "Un modello di intelligenza artificiale riconosce schemi nei dati e li usa per produrre risposte o previsioni. "
            "Non si limita a copiare esempi, non è solo memoria grezza e non è un semplice archivio di informazioni."
        )
    },

    "AI-INT-0101": {
        "opzioni": [
            "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
            "Perché chunk molto grandi conservano contesto, ma possono mescolare informazioni non pertinenti",
            "Perché chunk molto piccoli possono essere precisi, ma rischiano di perdere contesto utile",
            "Perché la scelta dei chunk migliora il recupero, ma modifica anche i pesi del modello durante la risposta"
        ],
        "spiegazione": (
            "In un sistema RAG la scelta dei chunk è importante perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso. "
            "I chunk grandi possono mescolare contenuti non pertinenti, quelli piccoli possono perdere contesto, ma la loro scelta non modifica i pesi del modello."
        )
    },

    "AI-FAC-0102": {
        "opzioni": [
            "Riassumi questo testo in 5 righe indicando le idee principali",
            "Riassumi questo testo indicando le idee principali, ma senza fissare una lunghezza precisa",
            "Spiega questo testo indicando i punti importanti, ma mantenendo una forma più estesa",
            "Riscrivi questo testo in modo ordinato, ma senza chiedere di selezionare solo le idee principali"
        ],
        "spiegazione": (
            "Il prompt più chiaro chiede di riassumere il testo in 5 righe indicando le idee principali. "
            "Le altre opzioni sono vicine al lavoro sul testo, ma non uniscono in modo preciso compito, lunghezza e selezione delle idee essenziali."
        )
    },

    "AI-INT-0102": {
        "opzioni": [
            "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
            "La ricerca semantica può usare parole diverse, ma richiede comunque gli stessi termini principali",
            "La ricerca per parole esatte può trovare sinonimi, ma solo quando il testo ha la stessa intenzione",
            "La ricerca per parole esatte confronta il significato, ma funziona meglio se le parole non coincidono"
        ],
        "spiegazione": (
            "La ricerca semantica può trovare contenuti simili nel significato anche quando le parole sono diverse. "
            "La ricerca per parole esatte dipende di più dalle corrispondenze letterali e non riconosce automaticamente sinonimi o intenzioni come fa una ricerca basata sul significato."
        )
    },

    "AI-FAC-0103": {
        "opzioni": [
            "Perché influenzano ciò che il modello impara e come risponde",
            "Perché influenzano ciò che il modello impara, ma rendono superfluo controllare le risposte",
            "Perché servono a verificare il modello dopo l'addestramento, più che a farlo imparare",
            "Perché definiscono esempi utili, ma obbligano il modello a ricopiare risposte predefinite"
        ],
        "spiegazione": (
            "I dati di addestramento sono importanti perché influenzano ciò che il modello impara e come risponde. "
            "Questo non rende inutili i controlli, non li trasforma in dati di semplice verifica e non significa che il modello debba ricopiare risposte predefinite."
        )
    },

    "AI-AV-0104": {
        "opzioni": [
            "Un documento contiene istruzioni nascoste che provano a far ignorare le regole del sistema",
            "Un documento contiene testo che sembra informativo, ma prova a essere trattato come istruzione operativa",
            "Un documento contiene una richiesta esterna, ma viene letto solo come contenuto senza rischi per il comportamento",
            "Un documento contiene testo ambiguo, ma il rischio riguarda soltanto la qualità linguistica della risposta"
        ],
        "spiegazione": (
            "Un esempio realistico di prompt injection è un documento esterno che contiene istruzioni nascoste per far ignorare le regole del sistema. "
            "Il rischio nasce quando contenuto apparentemente informativo prova a influenzare il comportamento del modello o degli strumenti collegati."
        )
    },

    "AI-FAC-0104": {
        "opzioni": [
            "Stabilire se un messaggio è spam o non spam",
            "Stabilire una categoria per un messaggio, ma senza usare etichette definite in partenza",
            "Analizzare messaggi simili, ma raggruppandoli senza scegliere una classe finale",
            "Produrre una risposta a un messaggio, ma usando il testo come se fosse una categoria"
        ],
        "spiegazione": (
            "Un compito di classificazione assegna un input a una categoria tra quelle previste, come spam o non spam. "
            "Raggruppare senza etichette è clustering, mentre generare una risposta appartiene alla generazione di contenuti."
        )
    },

    "AI-AV-0105": {
        "opzioni": [
            "Per rendere più chiaro dove nasce un errore e migliorare ogni fase separatamente",
            "Per analizzare recupero, generazione e controllo, ma senza collegare gli errori al risultato finale",
            "Per separare le fasi dell'app, ma impedendo al modello di usare fonti esterne quando servono",
            "Per rendere il sistema più ordinato, ma evitando controlli dopo la generazione della risposta"
        ],
        "spiegazione": (
            "Separare recupero dei dati, generazione e controllo finale aiuta a capire dove nasce un errore e a migliorare ogni fase separatamente. "
            "La separazione non deve scollegare gli errori dal risultato finale, non impedisce l'uso di fonti esterne e non elimina il controllo conclusivo."
        )
    },

    "AI-FAC-0106": {
        "opzioni": [
            "A una risposta plausibile ma falsa o non verificata",
            "A una risposta plausibile e incompleta, ma senza informazioni false o inventate",
            "A una risposta corretta ma troppo breve, quindi poco utile per l'utente",
            "A una risposta prudente che segnala incertezza invece di inventare informazioni"
        ],
        "spiegazione": (
            "Un'allucinazione in AI è una risposta plausibile ma falsa, inventata o non verificata. "
            "Una risposta incompleta, breve o prudente può essere migliorabile, ma non è necessariamente un'allucinazione."
        )
    },

    "AI-FAC-0203": {
        "opzioni": [
            "Perché fornisce esempi da cui il modello può imparare relazioni e schemi",
            "Perché fornisce esempi di apprendimento, ma sostituisce la valutazione del modello",
            "Perché contiene dati utili, ma rende meno importante scegliere un algoritmo adatto",
            "Perché offre esempi al modello, ma serve soprattutto a fargli ricopiare risposte finali"
        ],
        "spiegazione": (
            "Un dataset di addestramento è importante perché fornisce esempi da cui il modello può imparare relazioni e schemi. "
            "Non sostituisce la valutazione, non rende irrilevante l'algoritmo e non serve a far copiare meccanicamente risposte finali."
        )
    },

    "AI-FAC-0205": {
        "opzioni": [
            "Una situazione in cui il modello impara troppo bene gli esempi di addestramento e generalizza male su dati nuovi",
            "Una situazione in cui il modello si adatta molto ai dati di training, ma migliora anche sui casi nuovi",
            "Una situazione in cui il modello impara esempi specifici, ma senza perdere capacità di generalizzare",
            "Una situazione in cui il modello memorizza dettagli del training, ma diventa più affidabile fuori dal training"
        ],
        "spiegazione": (
            "L'overfitting avviene quando il modello impara troppo bene gli esempi di addestramento e generalizza male su dati nuovi. "
            "Il punto critico non è solo adattarsi al training, ma perdere affidabilità quando arrivano casi diversi da quelli visti."
        )
    },

    "AI-INT-0203": {
        "opzioni": [
            "Rende le risposte più variabili e meno deterministiche",
            "Rende le risposte più varie, ma riduce direttamente il numero di parametri del modello",
            "Aumenta la variabilità della generazione, ma amplia anche la finestra di contesto disponibile",
            "Rende la generazione meno prevedibile, ma impedisce al modello di produrre testo creativo"
        ],
        "spiegazione": (
            "Aumentare la temperatura rende in genere le risposte più variabili e meno deterministiche. "
            "Non cambia direttamente il numero di parametri, non amplia la finestra di contesto e non impedisce la creatività: semmai tende ad aumentare la varietà."
        )
    },

    "AI-AV-0212": {
        "opzioni": [
            "Perché serve confrontare la risposta con fonti, contesto e correttezza fattuale, non solo con la forma del testo",
            "Perché una risposta può sembrare ben scritta, ma richiedere verifica su fonti e contesto",
            "Perché una metrica può premiare fluidità e somiglianza, ma non garantire correttezza fattuale",
            "Perché valutare le allucinazioni richiede controllo del contenuto, ma può ignorare il supporto delle fonti"
        ],
        "spiegazione": (
            "Valutare le allucinazioni richiede spesso più di una metrica automatica semplice perché bisogna confrontare risposta, fonti, contesto e correttezza fattuale. "
            "Fluidità, somiglianza o buona forma del testo non bastano a dimostrare che una risposta sia realmente corretta e supportata."
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
    if not FILE_AI.exists():
        raise SystemExit("ERRORE: data/ai.json non trovato.")

    if not BACKUP.exists():
        BACKUP.write_text(FILE_AI.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato: {BACKUP}")
    else:
        print(f"Backup già presente: {BACKUP}")

    contenuto = carica_json(FILE_AI)
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
            "Ogni risposta errata deve condividere il concetto centrale della corretta "
            "e diventare sbagliata per un dettaglio tecnico, logico o pratico."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE_AI, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento AI - quinto blocco distrattori forti",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: stesso concetto centrale, stesso contesto, piccolo dettaglio sbagliato.",
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

    print("===== MIGLIORAMENTO AI - QUINTO BLOCCO =====")
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
    print("OK: quinto blocco AI aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
