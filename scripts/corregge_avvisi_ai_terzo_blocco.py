import json
from pathlib import Path

FILE_AI = Path("data/ai.json")
BACKUP = Path("data/ai.backup_prima_correzione_avvisi_terzo_blocco.json")
REPORT = Path("reports/corregge_avvisi_ai_terzo_blocco.md")

PATCH = {
    "AI-FAC-0006": {
        "opzioni": [
            "È una classificazione, perché assegna l'email a una categoria come spam o non spam",
            "È clustering, perché raggruppa email simili anche se usa categorie già definite",
            "È regressione, perché produce una decisione binaria invece di stimare un valore numerico continuo",
            "È analisi semantica libera, perché interpreta il testo senza assegnare una classe finale"
        ],
        "spiegazione": (
            "Decidere se una email è spam oppure no è un problema di classificazione, perché l'input viene assegnato a una categoria. "
            "Il clustering raggruppa elementi senza etichette già definite, la regressione stima valori numerici e l'analisi libera non descrive la scelta tra classi."
        )
    },

    "AI-FAC-0008": {
        "opzioni": [
            "È un'allucinazione, perché il modello produce contenuto falso presentandolo come sicuro",
            "È un errore di grounding, perché la risposta sembra fondata ma non è supportata dai dati disponibili",
            "È bias del dataset, perché la risposta falsa nasce da una distorsione sistematica nei dati",
            "È overfitting, perché il modello ripete una risposta appresa invece di generare contenuto inventato"
        ],
        "spiegazione": (
            "Quando un modello inventa una risposta falsa e la presenta come sicura si parla normalmente di allucinazione. "
            "Un errore di grounding può essere collegato, ma non è il nome principale del fenomeno; bias e overfitting indicano problemi diversi."
        )
    },

    "AI-FAC-0208": {
        "opzioni": [
            "Una risposta plausibile nella forma ma non corretta o non supportata dai dati",
            "Una risposta fluida e sicura, ma supportata solo da fonti che il modello non ha realmente verificato",
            "Una risposta non supportata dai dati, ma considerata corretta perché coerente con il tono della conversazione",
            "Una risposta plausibile ma imprecisa, corretta durante la generazione senza verifiche esterne"
        ],
        "spiegazione": (
            "Un'allucinazione è una risposta plausibile nella forma ma non corretta o non supportata dai dati. "
            "Una risposta non diventa affidabile solo perché è fluida, coerente nel tono o formulata con sicurezza."
        )
    },

    "AI-INT-0208": {
        "opzioni": [
            "Per controllare meglio quando l'agente deve pensare, chiamare strumenti, verificare risultati o fermarsi",
            "Per separare ragionamento e azioni, ma permettere comunque all'agente di eseguire strumenti senza verifica finale",
            "Per controllare le fasi dell'agente, ma trattare la chiamata agli strumenti come sicura quando il ragionamento sembra coerente",
            "Per distinguere pensiero e azione, ma eliminando log e controlli quando l'agente produce una risposta fluida"
        ],
        "spiegazione": (
            "Separare ragionamento e azioni rende l'agente più controllabile: si può decidere quando pensare, chiamare strumenti, verificare risultati o fermarsi. "
            "Il ragionamento coerente non basta a rendere sicura una chiamata a strumenti esterni, e log, controlli e verifica finale restano necessari."
        )
    },

    "AI-INT-0210": {
        "opzioni": [
            "Una tendenza sistematica del modello a favorire o penalizzare certi risultati o gruppi",
            "Una tendenza del modello verso certi risultati, ma dovuta soltanto a errori casuali non ripetibili",
            "Una distorsione sistematica nei risultati, ma intenzionale e progettata manualmente dagli sviluppatori",
            "Una preferenza del modello per alcuni output, ma priva di effetti misurabili su gruppi, decisioni o risultati"
        ],
        "spiegazione": (
            "Il bias indica una tendenza sistematica del modello a favorire o penalizzare certi risultati o gruppi. "
            "Non è semplice rumore casuale, non deve essere per forza intenzionale e può avere effetti misurabili sui risultati."
        )
    }
}


def carica_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path, contenuto):
    path.write_text(
        json.dumps(contenuto, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def estrai_domande(contenuto):
    if isinstance(contenuto, list):
        return contenuto

    for chiave in ["domande", "questions", "quiz", "items"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave]

    raise ValueError("Formato JSON non riconosciuto.")


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
        "# Correzione avvisi AI - terzo blocco",
        "",
        "Corrette le 5 domande che producevano avvisi nel motore qualità generale.",
        "",
        f"Domande corrette: {len(aggiornate)}",
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

    print("===== CORREZIONE AVVISI AI - TERZO BLOCCO =====")
    print(f"Domande corrette: {len(aggiornate)}")

    for id_domanda in aggiornate:
        print(f"- {id_domanda}")

    if non_trovate:
        print()
        print("ID non trovati:")
        for id_domanda in non_trovate:
            print(f"- {id_domanda}")

    print()
    print(f"Report creato: {REPORT}")
    print("OK: avvisi corretti.")


if __name__ == "__main__":
    main()
