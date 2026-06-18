import json
from pathlib import Path

FILE = Path("data/logica/ragionamento_critico.json")
BACKUP = Path("backups/ragionamento_critico.backup_prima_quarto_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_logica_quarto_blocco_distrattori_forti.md")

PATCH = {
    "LOG-CRI-FAC-0001": {
        "opzioni": [
            "Il treno 25 arriva in stazione",
            "Il treno 25 arriva in stazione solo se è in orario",
            "Ogni treno che arriva in stazione appartiene alla linea A",
            "Il treno 25 è l'unico treno della linea A che arriva in stazione"
        ],
        "spiegazione": (
            "La premessa dice che tutti i treni della linea A arrivano in stazione. "
            "Dato che il treno 25 è della linea A, si può concludere che il treno 25 arriva in stazione. "
            "L'orario non è una condizione presente nella premessa. "
            "Non si può invertire la regola dicendo che ogni treno arrivato sia della linea A. "
            "Non si può nemmeno dedurre che il treno 25 sia l'unico treno della linea A ad arrivare."
        )
    },

    "LOG-CRI-INT-0002": {
        "opzioni": [
            "Oggi non piove",
            "Marco ha dimenticato l'ombrello anche se piove",
            "Oggi piove, ma Marco ha cambiato comportamento",
            "Non si può collegare l'ombrello alla pioggia"
        ],
        "spiegazione": (
            "La regola è: se piove, Marco prende l'ombrello. "
            "Se oggi Marco non prende l'ombrello, allora la condizione 'piove' non si è verificata. "
            "È una deduzione per contrapposizione: se P implica Q, allora non Q implica non P. "
            "Dire che Marco abbia dimenticato l'ombrello o cambiato comportamento aggiunge informazioni non date. "
            "Dire che non si possa collegare ombrello e pioggia ignora la regola iniziale."
        )
    },

    "LOG-CRI-AV-0003": {
        "opzioni": [
            "Non è certo che il prodotto sia scontato",
            "Il prodotto è scontato perché si trova nello scaffale rosso",
            "Lo scaffale rosso contiene solo prodotti scontati",
            "I prodotti non scontati sono esclusi dallo scaffale rosso"
        ],
        "spiegazione": (
            "La premessa dice che tutti i prodotti scontati sono nello scaffale rosso. "
            "Questo non significa che tutti i prodotti nello scaffale rosso siano scontati. "
            "Trovare un prodotto nello scaffale rosso non basta quindi per concludere che sia scontato. "
            "Le altre risposte confondono la direzione della regola: da 'scontato implica scaffale rosso' non segue 'scaffale rosso implica scontato'."
        )
    },

    "LOG-CRI-INT-0004": {
        "opzioni": [
            "Alcune persone che documentano gli errori controllano i log",
            "Tutte le persone che documentano gli errori controllano i log",
            "Alcune persone che controllano i log documentano gli errori",
            "Chi controlla i log documenta anche gli errori"
        ],
        "spiegazione": (
            "Sappiamo che alcuni tecnici documentano gli errori e che tutti i tecnici controllano i log. "
            "Quindi almeno alcune persone che documentano gli errori controllano anche i log. "
            "Non si può estendere la conclusione a tutte le persone che documentano errori, perché la premessa parla solo di alcuni tecnici. "
            "La frase sulle persone che controllano i log può sembrare vicina, ma cambia il punto di partenza della deduzione. "
            "Non è dimostrato che chi controlla i log documenti anche errori."
        )
    },

    "LOG-CRI-AV-0005": {
        "opzioni": [
            "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
            "L'aggiornamento è la causa perché è avvenuto prima degli errori",
            "Gli errori sono indipendenti dall'aggiornamento perché li hanno segnalati solo alcuni utenti",
            "Le segnalazioni bastano da sole per identificare la causa tecnica"
        ],
        "spiegazione": (
            "La vicinanza temporale tra aggiornamento ed errori suggerisce una possibile relazione, ma non dimostra una causa. "
            "La conclusione più prudente è che l'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche. "
            "Dire che l'aggiornamento sia la causa solo perché è avvenuto prima confonde successione temporale e causalità. "
            "Dire che gli errori siano indipendenti perché riguardano solo alcuni utenti esclude una possibilità senza prove. "
            "Le segnalazioni da sole non bastano per individuare la causa tecnica."
        )
    },

    "LOG-CRI-FAC-0101": {
        "opzioni": [
            "Fido è un animale",
            "Fido potrebbe non essere un animale anche se è un cane",
            "Ogni animale è un cane",
            "Alcuni cani non appartengono agli animali"
        ],
        "spiegazione": (
            "La premessa dice che tutti i cani sono animali. "
            "Dato che Fido è un cane, Fido appartiene al gruppo degli animali. "
            "Non vale il contrario: dal fatto che i cani siano animali non segue che ogni animale sia un cane. "
            "Non si può neanche dire che Fido potrebbe non essere un animale, perché contraddice direttamente la premessa."
        )
    },

    "LOG-CRI-INT-0101": {
        "opzioni": [
            "Alcuni programmatori sanno usare variabili",
            "Tutti i programmatori sanno usare variabili",
            "Chi sa usare variabili conosce Python",
            "I programmatori che non conoscono Python non sanno usare variabili"
        ],
        "spiegazione": (
            "Alcuni programmatori conoscono Python. "
            "Tutti quelli che conoscono Python sanno usare variabili. "
            "Quindi almeno alcuni programmatori sanno usare variabili. "
            "Non si può concludere che tutti i programmatori sappiano usare variabili. "
            "Non si può invertire la regola dicendo che chi sa usare variabili conosce Python. "
            "Non sappiamo nulla sui programmatori che non conoscono Python."
        )
    },

    "LOG-CRI-AV-0101": {
        "opzioni": [
            "Alcune persone che usano Git lavorano su database",
            "Alcuni sviluppatori del team lavorano su database",
            "Tutti gli sviluppatori del team lavorano su database",
            "Chi usa Git appartiene al team di sviluppo"
        ],
        "spiegazione": (
            "La seconda premessa afferma direttamente che alcune persone che usano Git lavorano anche su database. "
            "Questa è quindi la conclusione sicuramente vera. "
            "Non sappiamo se quelle persone siano sviluppatori del team. "
            "Non possiamo concludere che tutti gli sviluppatori lavorino su database. "
            "Non possiamo nemmeno dire che chi usa Git appartenga al team, perché potrebbero usare Git anche persone esterne."
        )
    },

    "LOG-CRI-FAC-0102": {
        "opzioni": [
            "Marco prende l'ombrello",
            "Marco prende l'ombrello solo se piove molto forte",
            "Marco prende l'ombrello perché non piove",
            "Marco prende l'ombrello solo quando deve uscire"
        ],
        "spiegazione": (
            "La regola dice che se oggi piove, Marco prende l'ombrello. "
            "Poiché oggi piove, la conclusione corretta è che Marco prende l'ombrello. "
            "Non si può aggiungere la condizione della pioggia molto forte. "
            "Non si può dire che lo prenda perché non piove, perché contraddice il dato. "
            "Non si può introdurre la condizione dell'uscire, perché non è presente nella premessa."
        )
    },

    "LOG-CRI-INT-0102": {
        "opzioni": [
            "L'app non ha superato tutti i test",
            "L'app ha superato i test, ma è stata bloccata per un altro motivo",
            "L'app potrebbe essere pubblicata anche senza superare i test",
            "Ogni app pubblicata supera tutti i test"
        ],
        "spiegazione": (
            "La regola dice: se un'app supera tutti i test, allora viene pubblicata. "
            "Se l'app non viene pubblicata, si può concludere per contrapposizione che non ha superato tutti i test. "
            "Dire che abbia superato i test ma sia stata bloccata per un altro motivo contraddice la regola data. "
            "Dire che possa essere pubblicata senza superare i test aggiunge una possibilità non prevista. "
            "La frase sulle app pubblicate inverte o estende la regola oltre ciò che è richiesto."
        )
    },

    "LOG-CRI-0201": {
        "opzioni": [
            "Marco non può entrare",
            "Marco può entrare se riceve un'autorizzazione non indicata dal cartello",
            "Marco può entrare perché il cartello parla solo dei dipendenti",
            "Marco può entrare se accompagna un dipendente"
        ],
        "spiegazione": (
            "Il cartello dice che l'ingresso è consentito solo ai dipendenti. "
            "Marco non è dipendente, quindi non rientra tra le persone autorizzate dalla regola indicata. "
            "Le altre opzioni aggiungono eccezioni non presenti: autorizzazioni esterne, accompagnamento o interpretazioni diverse del cartello."
        )
    },

    "LOG-CRI-0202": {
        "opzioni": [
            "Anna prende l'ombrello",
            "Anna non esce di casa",
            "Anna prende l'ombrello solo se piove molto",
            "Anna prende anche il cappotto"
        ],
        "spiegazione": (
            "La regola è: se piove, Anna prende l'ombrello. "
            "Oggi piove, quindi segue che Anna prende l'ombrello. "
            "Non si può concludere che non esca di casa. "
            "Non si può aggiungere la condizione della pioggia forte. "
            "Non si può dedurre che prenda anche il cappotto, perché non è indicato."
        )
    },

    "LOG-CRI-0203": {
        "opzioni": [
            "Il biglietto non è valido",
            "Il biglietto potrebbe essere valido anche senza codice QR",
            "Il codice QR potrebbe essere nascosto",
            "Il biglietto è valido se è stato acquistato online"
        ],
        "spiegazione": (
            "La premessa dice che tutti i biglietti validi hanno un codice QR. "
            "Questo biglietto non ha codice QR. "
            "Per contrapposizione, il biglietto non può essere valido. "
            "Le altre opzioni introducono eccezioni non presenti: validità senza QR, QR nascosto o acquisto online."
        )
    },

    "LOG-CRI-0204": {
        "opzioni": [
            "I nuovi corsi potrebbero aver contribuito all'aumento",
            "I nuovi corsi sono l'unica causa dell'aumento",
            "L'aumento dipende solo dal periodo dell'anno",
            "Il numero di iscritti dimostra già la causa precisa"
        ],
        "spiegazione": (
            "Il fatto che gli iscritti aumentino dopo l'introduzione di nuovi corsi suggerisce una possibile relazione. "
            "La conclusione più prudente è che i nuovi corsi potrebbero aver contribuito all'aumento. "
            "Non si può dire che siano l'unica causa. "
            "Non si può attribuire l'aumento solo al periodo dell'anno senza altri dati. "
            "Il numero di iscritti da solo non dimostra la causa precisa."
        )
    },

    "LOG-CRI-0205": {
        "opzioni": [
            "Le recensioni sono incoraggianti, ma il campione è ancora limitato",
            "Le recensioni positive rendono già il giudizio solido",
            "I pochi download annullano il valore delle recensioni positive",
            "Le recensioni bastano senza altri dati d'uso"
        ],
        "spiegazione": (
            "Le recensioni positive sono un segnale utile, ma pochi download rendono il campione limitato. "
            "La valutazione più equilibrata è quindi positiva ma prudente. "
            "Dire che il giudizio sia già solido ignora la dimensione ridotta del campione. "
            "Dire che i pochi download annullino le recensioni è troppo drastico. "
            "Dire che le recensioni bastino senza altri dati d'uso è una conclusione non abbastanza prudente."
        )
    },

    "LOG-CRI-0206": {
        "opzioni": [
            "Serve provarla anche in condizioni più ampie",
            "Il test piccolo dimostra che funzionerà nei casi principali",
            "Il test piccolo va ignorato finché non viene ripetuto su larga scala",
            "La soluzione è valida se il primo test non mostra errori"
        ],
        "spiegazione": (
            "Un test piccolo è utile, ma non permette di generalizzare con sicurezza a contesti più ampi. "
            "La conclusione più corretta è che serve provarla anche in condizioni più ampie. "
            "Dire che funzionerà nei casi principali generalizza troppo. "
            "Dire che il test piccolo vada ignorato è eccessivo, perché fornisce comunque un primo segnale. "
            "Dire che la soluzione sia valida solo perché il primo test non mostra errori è una conclusione troppo rapida."
        )
    },

    "LOG-CRI-0207": {
        "opzioni": [
            "Il punto esatto in cui gli studenti abbandonano",
            "La percentuale di studenti che si iscrivono per curiosità",
            "Il numero di lezioni viste prima dell'abbandono medio",
            "Il livello dichiarato dagli studenti prima del corso"
        ],
        "spiegazione": (
            "Per capire perché molti iscritti non completano il corso, il dato più utile è il punto esatto in cui abbandonano. "
            "Questo permette di individuare difficoltà, contenuti deboli o passaggi poco chiari. "
            "La percentuale di iscritti per curiosità può aiutare, ma non mostra dove si rompe il percorso. "
            "La media delle lezioni viste è utile, ma meno precisa del punto esatto. "
            "Il livello iniziale degli studenti può essere rilevante, ma da solo non identifica il punto critico."
        )
    },

    "LOG-CRI-0208": {
        "opzioni": [
            "Il campione potrebbe non rappresentare tutti gli utenti",
            "Il risultato positivo dimostra che l'app piace al pubblico generale",
            "Il sondaggio è utile solo per valutare la grafica dell'app",
            "La community dei fan elimina il rischio di risposte sbilanciate"
        ],
        "spiegazione": (
            "Il sondaggio è stato pubblicato solo nella community dei fan, quindi il campione potrebbe essere sbilanciato. "
            "Il limite principale è che il campione potrebbe non rappresentare tutti gli utenti. "
            "Il risultato positivo non dimostra automaticamente il gradimento del pubblico generale. "
            "Il sondaggio non riguarda solo la grafica. "
            "La community dei fan aumenta, non elimina, il rischio di risposte poco neutrali."
        )
    },

    "LOG-CRI-0209": {
        "opzioni": [
            "Se nello stesso periodo sono cambiati anche personale o procedure",
            "Se il nuovo software ha un'interfaccia più moderna",
            "Se i monitor usati dagli operatori sono stati sostituiti",
            "Se il nome del software è più facile da ricordare"
        ],
        "spiegazione": (
            "Per valutare se il miglioramento dipenda davvero dal cambio di software bisogna controllare possibili fattori alternativi. "
            "La cosa più utile è sapere se nello stesso periodo sono cambiati anche personale o procedure. "
            "Un'interfaccia più moderna può essere collegata all'esperienza d'uso, ma non basta a spiegare i tempi di risposta. "
            "La sostituzione dei monitor è un fattore secondario e non centrale nella conclusione. "
            "Il nome del software non aiuta a valutare la causa del miglioramento."
        )
    },

    "LOG-CRI-0210": {
        "opzioni": [
            "Esiste un'associazione, ma servono altri dati per parlare di causa",
            "Dormire di più causa direttamente risultati migliori nel test",
            "Il test misura soprattutto quante ore dormono i partecipanti",
            "Chi dorme poco ottiene necessariamente risultati più bassi"
        ],
        "spiegazione": (
            "Il dato mostra che chi dorme di più ottiene risultati migliori nel test. "
            "Questo indica un'associazione, ma non basta da solo a dimostrare una causa. "
            "Potrebbero esserci altri fattori, come salute, stress, metodo di studio o routine quotidiana. "
            "Dire che il sonno causi direttamente il risultato è troppo rapido. "
            "Dire che il test misuri soprattutto il sonno cambia il significato del dato. "
            "Dire che chi dorme poco ottenga necessariamente risultati più bassi trasforma una tendenza in una certezza non dimostrata."
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
        raise SystemExit("ERRORE: data/logica/ragionamento_critico.json non trovato.")

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
            "Ogni risposta errata deve essere vicina alla corretta per ragionamento critico, "
            "ma sbagliata per un dettaglio preciso: inversione della regola, generalizzazione eccessiva, "
            "causa confusa con correlazione, eccezione non indicata o deduzione non garantita."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Logica - quarto blocco distrattori forti",
        "",
        "File aggiornato: `data/logica/ragionamento_critico.json`",
        "",
        "Backup salvato fuori dai dati ufficiali: `backups/ragionamento_critico.backup_prima_quarto_blocco_distrattori_forti.json`",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: distrattori vicini al ragionamento corretto e sbagliati per un dettaglio logico preciso.",
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

    print("===== MIGLIORAMENTO LOGICA - QUARTO BLOCCO =====")
    print("File: data/logica/ragionamento_critico.json")
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
    print("OK: quarto blocco Logica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
