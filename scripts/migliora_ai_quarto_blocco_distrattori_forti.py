import json
from pathlib import Path

FILE_AI = Path("data/ai.json")
BACKUP = Path("data/ai.backup_prima_quarto_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_ai_quarto_blocco_distrattori_forti.md")

PATCH = {
    "AI-AV-0206": {
        "opzioni": [
            "Perché cerca di dividere i documenti in parti coerenti dal punto di vista del significato",
            "Perché divide i documenti in parti coerenti, ma elimina il bisogno di controllare se il contesto resta completo",
            "Perché conserva meglio il significato dei passaggi, ma evita la creazione degli embedding per la ricerca",
            "Perché crea blocchi più vicini al significato, ma tratta ogni blocco come indipendente dalla domanda"
        ],
        "spiegazione": "Il chunking semantico può migliorare una pipeline RAG perché cerca di dividere i documenti in parti coerenti dal punto di vista del significato. Non elimina il controllo sul contesto, non sostituisce gli embedding e non basta creare blocchi coerenti se poi non vengono confrontati con la domanda."
    },

    "AI-AV-0210": {
        "opzioni": [
            "Un'architettura che può attivare solo una parte di esperti specializzati per elaborare un input",
            "Un'architettura con esperti specializzati, ma attivati tutti insieme per ogni input ricevuto",
            "Un modello con più esperti, ma scelti senza usare il contenuto o le caratteristiche dell'input",
            "Un sistema con componenti specializzati, ma usati per sostituire la tokenizzazione iniziale"
        ],
        "spiegazione": "Un modello Mixture of Experts usa un'architettura in cui una parte di esperti specializzati può essere attivata per elaborare un input. Non richiede di attivare tutti gli esperti, non sceglie gli esperti senza considerare l'input e non sostituisce la tokenizzazione."
    },

    "AI-AV-0214": {
        "opzioni": [
            "Per evitare che errori, risultati vuoti o dati inattesi vengano usati come se fossero corretti",
            "Per controllare l'esito dello strumento, ma procedere comunque se la risposta dell'agente sembra coerente",
            "Per verificare i risultati ottenuti, ma senza distinguere tra dati vuoti, parziali o fuori formato",
            "Per ridurre la propagazione degli errori, ma usando la verifica come semplice messaggio finale all'utente"
        ],
        "spiegazione": "Un agente deve verificare l'esito di uno strumento per evitare che errori, risultati vuoti o dati inattesi vengano usati come se fossero corretti. Una risposta apparentemente coerente non basta, perché il risultato del tool può essere mancante, parziale, fuori formato o non adatto al passo successivo."
    },

    "AI-INT-0105": {
        "opzioni": [
            "Il modello può funzionare bene su alcuni casi e male su altri meno rappresentati",
            "Il modello può favorire i casi più presenti, ma mantenere uguale affidabilità sui casi rari",
            "Il modello può imparare soprattutto dai casi frequenti, ma compensare i casi rari senza dati aggiuntivi",
            "Il modello può sembrare accurato nel totale, ma perché corregge automaticamente gli errori sulle classi rare"
        ],
        "spiegazione": "Se un dataset è molto sbilanciato, il modello può funzionare bene sui casi più rappresentati e male su quelli meno presenti. Non mantiene necessariamente la stessa affidabilità sui casi rari e non compensa da solo la mancanza di esempi o tecniche di bilanciamento."
    },

    "AI-FAC-0202": {
        "opzioni": [
            "L'istruzione o il testo iniziale dato al modello per guidare la risposta",
            "Il testo dato al modello, ma usato come risultato finale invece che come input",
            "L'indicazione iniziale per guidare la risposta, ma senza influenzare formato e contenuto",
            "Il messaggio usato per orientare il modello, ma coincidente con i pesi interni del sistema"
        ],
        "spiegazione": "Un prompt è l'istruzione o il testo iniziale dato al modello per guidare la risposta. Non è il risultato finale, può influenzare formato e contenuto, e non coincide con i pesi interni del modello."
    },

    "AI-FAC-0210": {
        "opzioni": [
            "Adattare un modello già addestrato a un compito o dominio più specifico",
            "Adattare un modello a un dominio specifico, ma partendo ogni volta da pesi casuali",
            "Specializzare un modello già addestrato, ma senza usare esempi collegati al nuovo compito",
            "Modificare il comportamento del modello, ma cambiando soltanto il prompt usato dall'utente"
        ],
        "spiegazione": "Il fine-tuning consiste nell'adattare un modello già addestrato a un compito o dominio più specifico. Non significa ripartire da pesi casuali, non funziona bene senza esempi pertinenti e non coincide con il semplice prompt engineering."
    },

    "AI-FAC-0211": {
        "opzioni": [
            "Perché i dati inseriti dall'utente possono contenere informazioni personali o sensibili",
            "Perché i dati dell'utente possono essere personali, ma diventano innocui appena entrano nel prompt",
            "Perché l'app può ricevere dati sensibili, ma il problema riguarda soltanto il salvataggio in memoria",
            "Perché le informazioni personali vanno gestite con attenzione, ma solo se l'utente scrive il proprio nome"
        ],
        "spiegazione": "La privacy è importante perché i dati inseriti dall'utente possono contenere informazioni personali o sensibili. Questi dati non diventano innocui solo perché sono nel prompt, e la tutela non riguarda soltanto la memoria o la presenza del nome dell'utente."
    },

    "AI-INT-0204": {
        "opzioni": [
            "Perché gli embedding possono catturare somiglianze di significato anche quando le parole usate sono diverse",
            "Perché gli embedding confrontano il significato, ma trovano risultati validi solo se le parole coincidono",
            "Perché la ricerca semantica può superare le parole chiave, ma evita la verifica dei risultati recuperati",
            "Perché gli embedding rappresentano il significato, ma sostituiscono completamente la domanda dell'utente"
        ],
        "spiegazione": "Gli embedding possono rendere la ricerca semantica più efficace perché catturano somiglianze di significato anche quando le parole usate sono diverse. Non richiedono parole identiche, non eliminano la verifica dei risultati e non sostituiscono la domanda dell'utente."
    },

    "AI-AV-0101": {
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto fuorviante",
            "Il modello può usare documenti apparentemente pertinenti, ma correggere il contesto durante la generazione",
            "Il sistema può recuperare testi simili alla domanda, ma considerarli affidabili anche senza pertinenza reale",
            "Il modello può produrre una risposta fluida, ma il problema riguarda solo la forma della risposta"
        ],
        "spiegazione": "Se il retrieval recupera documenti solo apparentemente pertinenti, il modello può generare una risposta ben scritta ma basata su contesto fuorviante. La generazione non corregge necessariamente un contesto sbagliato, la somiglianza non basta a garantire pertinenza e il problema non riguarda solo la forma."
    },

    "AI-AV-0107": {
        "opzioni": [
            "Per individuare casi problematici reali e migliorare sicurezza, qualità e affidabilità",
            "Per individuare casi problematici reali, ma lasciarli separati dal miglioramento del sistema",
            "Per raccogliere feedback degli utenti, ma usarli come sostituto dei test prima del rilascio",
            "Per registrare errori in produzione, ma senza collegarli a sicurezza, qualità o affidabilità"
        ],
        "spiegazione": "Un'app AI in produzione dovrebbe registrare errori e feedback per individuare casi problematici reali e migliorare sicurezza, qualità e affidabilità. I feedback non devono restare separati dal miglioramento, non sostituiscono i test iniziali e vanno collegati all'analisi del sistema."
    },

    "AI-INT-0205": {
        "opzioni": [
            "Riordinare i documenti recuperati in base alla loro rilevanza rispetto alla domanda",
            "Riordinare i documenti recuperati, ma senza confrontarli con la domanda specifica dell'utente",
            "Migliorare l'ordine dei risultati, ma usando solo la data del documento come criterio principale",
            "Selezionare documenti già recuperati, ma sostituendo la generazione della risposta finale"
        ],
        "spiegazione": "Un reranker riordina i documenti recuperati in base alla loro rilevanza rispetto alla domanda. Non basta ordinare senza guardare la domanda, non si basa solo sulla data del documento e non sostituisce la generazione della risposta."
    },

    "AI-AV-0213": {
        "opzioni": [
            "Deve conservare informazioni utili senza salvare dati inutili, sensibili o fuori contesto",
            "Deve conservare informazioni utili, ma senza permettere all'utente di correggere preferenze memorizzate",
            "Deve salvare elementi della conversazione, ma senza distinguere tra dati pertinenti e dati sensibili",
            "Deve migliorare la personalizzazione, ma trattando la memoria come archivio completo della chat"
        ],
        "spiegazione": "La memoria a lungo termine è delicata perché deve conservare informazioni utili senza salvare dati inutili, sensibili o fuori contesto. L'utente deve poter correggere le preferenze, e la memoria non dovrebbe diventare un archivio completo e indiscriminato della conversazione."
    },

    "AI-AV-0102": {
        "opzioni": [
            "Quando serve modificare stabilmente il comportamento del modello su molti esempi simili",
            "Quando serve stabilità su molti esempi, ma si dispone di casi isolati e poco coerenti",
            "Quando si vuole correggere una singola risposta, ma rendendo permanente quel comportamento",
            "Quando basta cambiare tono o formato di una risposta, ma si vuole evitare di scrivere prompt più chiari"
        ],
        "spiegazione": "Il fine-tuning è più adatto quando serve modificare stabilmente il comportamento del modello su molti esempi simili. Per pochi casi isolati, correzioni occasionali o modifiche leggere di tono e formato, spesso è più adatto lavorare sul prompt."
    },

    "AI-AV-0103": {
        "opzioni": [
            "Perché possono contare anche completezza, fonti, robustezza, sicurezza e chiarezza",
            "Perché oltre alla correttezza conta la completezza, ma fonti e sicurezza restano aspetti secondari",
            "Perché una risposta può essere corretta nei fatti, ma non adatta per contesto, chiarezza o sicurezza",
            "Perché la valutazione deve includere più criteri, ma ignorare la robustezza sui casi difficili"
        ],
        "spiegazione": "Valutare un sistema AI solo con risposta corretta o sbagliata può essere insufficiente perché contano anche completezza, fonti, robustezza, sicurezza e chiarezza. Una risposta può essere parzialmente corretta ma poco utile, poco sicura, non chiara o non robusta in casi difficili."
    },

    "AI-INT-0103": {
        "opzioni": [
            "Per misurare se generalizza oltre i casi usati per costruirlo",
            "Per misurare la generalizzazione, ma usando esempi molto simili a quelli già memorizzati",
            "Per verificare se funziona su casi nuovi, ma senza confrontare le risposte con risultati attesi",
            "Per controllare esempi non visti, ma valutando solo la velocità e non la qualità delle previsioni"
        ],
        "spiegazione": "Testare un modello su esempi che non ha visto durante lo sviluppo serve a misurare se generalizza oltre i casi usati per costruirlo. Non basta usare esempi quasi memorizzati, non basta osservare casi nuovi senza risultati attesi e la velocità non sostituisce la qualità delle previsioni."
    },

    "AI-INT-0104": {
        "opzioni": [
            "Specificare ruolo, obiettivo, formato di risposta e vincoli",
            "Specificare ruolo e formato, ma lasciare implicito l'obiettivo principale della risposta",
            "Indicare obiettivo e vincoli, ma senza chiarire il formato in cui deve rispondere il modello",
            "Fornire molte istruzioni al modello, ma senza definire priorità quando i vincoli entrano in conflitto"
        ],
        "spiegazione": "Un prompt è più controllabile quando specifica ruolo, obiettivo, formato di risposta e vincoli. Se mancano obiettivo, formato o priorità tra vincoli, il modello può produrre una risposta meno coerente con ciò che serve."
    },

    "AI-FAC-0105": {
        "opzioni": [
            "Che crea una risposta nuova seguendo il contesto ricevuto",
            "Che crea testo seguendo il contesto, ma scegliendo frasi già pronte senza adattarle alla richiesta",
            "Che produce una risposta nuova, ma senza usare il significato del prompt come guida",
            "Che genera testo, ma limitandosi a riformulare l'input senza aggiungere contenuto utile"
        ],
        "spiegazione": "Dire che un modello generativo produce testo significa che crea una risposta nuova seguendo il contesto ricevuto. Non si limita a scegliere frasi già pronte, non ignora il significato del prompt e non coincide con una semplice riformulazione dell'input."
    },

    "AI-AV-0106": {
        "opzioni": [
            "Può conservare informazioni inutili, sensibili o non più valide e usarle fuori contesto",
            "Può conservare memoria personale utile, ma senza distinguere tra dati pertinenti e dati sensibili",
            "Può salvare informazioni non più valide, ma aggiornarle correttamente senza criteri espliciti",
            "Può migliorare la personalizzazione, ma usare ricordi deboli come se fossero ancora affidabili"
        ],
        "spiegazione": "Se un agente salva memoria personale senza criteri chiari, può conservare informazioni inutili, sensibili o non più valide e usarle fuori contesto. La memoria deve distinguere dati pertinenti e sensibili, prevedere aggiornamenti e non trattare ricordi deboli o vecchi come automaticamente affidabili."
    },

    "AI-INT-0106": {
        "opzioni": [
            "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
            "Per scegliere una sequenza di azioni, ma senza verificare se resta coerente con l'obiettivo",
            "Per decidere gli strumenti da usare, ma eseguendo il primo passaggio anche se mancano dati necessari",
            "Per preparare le azioni dell'agente, ma evitando il controllo del risultato finale"
        ],
        "spiegazione": "Un agente AI può usare una fase di pianificazione per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni. La pianificazione deve restare coerente con l'obiettivo, considerare i dati necessari e mantenere il controllo sul risultato finale."
    },

    "AI-FAC-0204": {
        "opzioni": [
            "Assegnare il dato a una categoria tra quelle previste",
            "Assegnare il dato a una categoria, ma senza usare etichette o classi definite",
            "Decidere la categoria di un dato, ma trasformando prima ogni input in nuovo contenuto generato",
            "Collegare un dato a una classe, ma senza produrre una decisione finale tra le categorie"
        ],
        "spiegazione": "Classificare un dato con l'intelligenza artificiale significa assegnarlo a una categoria tra quelle previste. Non è classificazione se mancano classi definite, se l'obiettivo principale è generare nuovo contenuto o se non viene prodotta una decisione finale."
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
        "# Miglioramento AI - quarto blocco distrattori forti",
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

    print("===== MIGLIORAMENTO AI - QUARTO BLOCCO =====")
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
    print("OK: quarto blocco AI aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
