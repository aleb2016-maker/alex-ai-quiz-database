import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "AI-INT-0104": {
        "opzioni": [
            "Specificare ruolo, obiettivo, formato di risposta e vincoli",
            "Specificare solo il ruolo senza chiarire obiettivo, formato e vincoli",
            "Chiedere al modello di fare il meglio possibile senza istruzioni precise",
            "Lasciare la richiesta generica senza indicare criteri di risposta",
        ],
        "risposta_corretta": "Specificare ruolo, obiettivo, formato di risposta e vincoli",
        "spiegazione": (
            "Ruolo, obiettivo, formato e vincoli aiutano il modello a produrre una risposta più coerente con ciò che serve davvero. "
            "Specificare solo il ruolo può aiutare, ma non basta se mancano obiettivo, formato e vincoli."
        ),
        "distrattore_forte": "Specificare solo il ruolo senza chiarire obiettivo, formato e vincoli",
        "motivo_distrattore_forte": (
            "È vicino perché il ruolo è davvero utile nel prompt, "
            "ma è incompleto: per controllare meglio la risposta servono anche obiettivo, formato e vincoli."
        ),
    },
    "AI-INT-0105": {
        "opzioni": [
            "Il modello può funzionare bene su alcuni casi e male su altri meno rappresentati",
            "Il modello può favorire i casi più presenti e sbagliare più spesso quelli rari",
            "Il modello diventa automaticamente più equo su tutte le classi",
            "Il modello corregge da solo la mancanza di esempi nelle classi rare",
        ],
        "risposta_corretta": "Il modello può funzionare bene su alcuni casi e male su altri meno rappresentati",
        "spiegazione": (
            "Se alcune classi o situazioni sono poco rappresentate, il modello può imparare soprattutto i casi più frequenti "
            "e commettere più errori sui casi rari. Per questo bisogna controllare distribuzione dei dati e metriche."
        ),
        "distrattore_forte": "Il modello può favorire i casi più presenti e sbagliare più spesso quelli rari",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive un effetto reale dello sbilanciamento, "
            "ma la risposta corretta è più generale: il modello può andare bene su alcuni casi e male su altri meno rappresentati."
        ),
    },
    "AI-INT-0106": {
        "opzioni": [
            "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
            "Per scegliere una sequenza di azioni, ma senza verificare se sono coerenti con l'obiettivo",
            "Per trasformare ogni risposta in una lista casuale di operazioni",
            "Per saltare completamente il controllo del risultato finale",
        ],
        "risposta_corretta": "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
        "spiegazione": (
            "Un agente AI può pianificare prima di agire per decidere quali passaggi seguire, quali strumenti usare e in quale ordine. "
            "Questo riduce il rischio di azioni impulsive o poco coerenti con l'obiettivo."
        ),
        "distrattore_forte": "Per scegliere una sequenza di azioni, ma senza verificare se sono coerenti con l'obiettivo",
        "motivo_distrattore_forte": (
            "È vicino perché parla di sequenza di azioni, "
            "ma è sbagliato perché la pianificazione deve restare coerente con l'obiettivo e non essere solo una lista di passaggi."
        ),
    },
    "AI-INT-0107": {
        "opzioni": [
            "Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose",
            "Per ridurre i rischi limitando alcune azioni automatiche, ma senza richiedere mai conferme",
            "Per impedire al modello di leggere qualsiasi istruzione dell'utente",
            "Per rendere impossibile ogni controllo umano sulle azioni dell'agente",
        ],
        "risposta_corretta": "Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose",
        "spiegazione": (
            "Un agente con troppi permessi può fare danni se interpreta male un comando o subisce prompt injection. "
            "Limitare permessi e richiedere conferme nei casi delicati rende il sistema più sicuro."
        ),
        "distrattore_forte": "Per ridurre i rischi limitando alcune azioni automatiche, ma senza richiedere mai conferme",
        "motivo_distrattore_forte": (
            "È vicino perché parla di limitare azioni automatiche, "
            "ma è incompleto: nei casi delicati possono servire anche conferme o controlli umani."
        ),
    },
    "AI-AV-0101": {
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto fuorviante",
            "Il modello può generare una risposta fluida usando documenti recuperati solo in apparenza pertinenti",
            "Il modello rifiuta automaticamente ogni documento non perfettamente pertinente",
            "Il database vettoriale elimina da solo tutti i documenti non usati",
        ],
        "risposta_corretta": "Il modello può generare una risposta ben scritta ma basata su contesto fuorviante",
        "spiegazione": (
            "Se i documenti recuperati sembrano pertinenti ma non rispondono davvero alla domanda, il modello può appoggiarsi "
            "a informazioni sbagliate o parziali e produrre una risposta convincente ma non affidabile."
        ),
        "distrattore_forte": "Il modello può generare una risposta fluida usando documenti recuperati solo in apparenza pertinenti",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive lo stesso rischio di una risposta fluida basata su retrieval debole, "
            "ma è meno completo: il punto centrale è che il contesto può essere fuorviante."
        ),
    },
    "AI-AV-0102": {
        "opzioni": [
            "Quando serve modificare stabilmente il comportamento del modello su molti esempi simili",
            "Quando serve un comportamento stabile, ma si dispone solo di pochi esempi isolati e non coerenti",
            "Quando bisogna correggere una singola risposta occasionale",
            "Quando basta cambiare il tono di una frase una sola volta",
        ],
        "risposta_corretta": "Quando serve modificare stabilmente il comportamento del modello su molti esempi simili",
        "spiegazione": (
            "Il fine-tuning è utile se si hanno esempi di qualità e si vuole rendere stabile un comportamento su una famiglia di compiti. "
            "Per modifiche leggere o occasionali spesso basta il prompt."
        ),
        "distrattore_forte": "Quando serve un comportamento stabile, ma si dispone solo di pochi esempi isolati e non coerenti",
        "motivo_distrattore_forte": (
            "È vicino perché parla di comportamento stabile, "
            "ma è sbagliato perché il fine-tuning richiede esempi coerenti e sufficienti, non casi isolati."
        ),
    },
    "AI-AV-0103": {
        "opzioni": [
            "Perché possono contare anche completezza, fonti, robustezza, sicurezza e chiarezza",
            "Perché basta aggiungere la completezza alla valutazione, senza considerare sicurezza e fonti",
            "Perché ogni risposta generata è corretta se è scritta in modo fluido",
            "Perché la valutazione deve ignorare il contesto della domanda",
        ],
        "risposta_corretta": "Perché possono contare anche completezza, fonti, robustezza, sicurezza e chiarezza",
        "spiegazione": (
            "Molti sistemi AI non producono solo una risposta secca. Serve valutare qualità, affidabilità, aderenza al contesto, "
            "sicurezza e capacità di gestire casi difficili."
        ),
        "distrattore_forte": "Perché basta aggiungere la completezza alla valutazione, senza considerare sicurezza e fonti",
        "motivo_distrattore_forte": (
            "È vicino perché la completezza è davvero un criterio importante, "
            "ma è sbagliato perché da sola non basta: servono anche fonti, sicurezza, robustezza e chiarezza."
        ),
    },
    "AI-AV-0104": {
        "opzioni": [
            "Un documento contiene istruzioni nascoste che provano a far ignorare le regole del sistema",
            "Un documento contiene testo che il modello potrebbe scambiare per istruzioni operative",
            "Un utente scrive una domanda troppo breve per essere capita",
            "Una risposta contiene una parola inglese invece di una italiana",
        ],
        "risposta_corretta": "Un documento contiene istruzioni nascoste che provano a far ignorare le regole del sistema",
        "spiegazione": (
            "La prompt injection può arrivare anche da contenuti esterni. Un documento può contenere istruzioni malevole "
            "che cercano di far cambiare comportamento al modello o ai tool collegati."
        ),
        "distrattore_forte": "Un documento contiene testo che il modello potrebbe scambiare per istruzioni operative",
        "motivo_distrattore_forte": (
            "È vicino perché descrive il meccanismo della prompt injection da documenti esterni, "
            "ma è meno preciso: la risposta corretta indica istruzioni nascoste progettate per far ignorare le regole del sistema."
        ),
    },
    "AI-AV-0105": {
        "opzioni": [
            "Per rendere più chiaro dove nasce un errore e migliorare ogni fase separatamente",
            "Per analizzare ogni fase separatamente, ma senza collegare gli errori al risultato finale",
            "Per fare in modo che il modello non riceva mai alcun contesto",
            "Per impedire all'app di usare database o API",
        ],
        "risposta_corretta": "Per rendere più chiaro dove nasce un errore e migliorare ogni fase separatamente",
        "spiegazione": (
            "Separare le fasi aiuta a capire se il problema nasce dal retrieval, dal prompt, dalla generazione o dal controllo finale. "
            "Questo rende debug e miglioramento molto più ordinati."
        ),
        "distrattore_forte": "Per analizzare ogni fase separatamente, ma senza collegare gli errori al risultato finale",
        "motivo_distrattore_forte": (
            "È vicino perché parla di analisi separata delle fasi, "
            "ma è sbagliato perché separare le fasi serve proprio a collegare gli errori al risultato finale."
        ),
    },
    "AI-AV-0106": {
        "opzioni": [
            "Può conservare informazioni inutili, sensibili o non più valide e usarle fuori contesto",
            "Può conservare informazioni personali utili, ma senza distinguere tra dati pertinenti e dati sensibili",
            "Diventa automaticamente incapace di rispondere a domande generali",
            "Trasforma ogni informazione salvata in codice eseguibile",
        ],
        "risposta_corretta": "Può conservare informazioni inutili, sensibili o non più valide e usarle fuori contesto",
        "spiegazione": (
            "La memoria può migliorare la personalizzazione, ma va gestita con criteri: cosa salvare, cosa evitare, "
            "quando aggiornare e come rispettare privacy e pertinenza."
        ),
        "distrattore_forte": "Può conservare informazioni personali utili, ma senza distinguere tra dati pertinenti e dati sensibili",
        "motivo_distrattore_forte": (
            "È vicino perché parla di memoria personale e dati sensibili, "
            "ma è incompleto: il rischio riguarda anche informazioni inutili, non più valide o usate fuori contesto."
        ),
    },
    "AI-AV-0107": {
        "opzioni": [
            "Per individuare casi problematici reali e migliorare sicurezza, qualità e affidabilità",
            "Per individuare problemi reali, ma senza usarli per migliorare il sistema",
            "Per sostituire ogni test prima del rilascio",
            "Per evitare qualsiasi aggiornamento futuro del sistema",
        ],
        "risposta_corretta": "Per individuare casi problematici reali e migliorare sicurezza, qualità e affidabilità",
        "spiegazione": (
            "I test iniziali non coprono tutti gli scenari. Log e feedback aiutano a scoprire errori ricorrenti, "
            "casi limite e problemi di sicurezza emersi nell'uso reale."
        ),
        "distrattore_forte": "Per individuare problemi reali, ma senza usarli per migliorare il sistema",
        "motivo_distrattore_forte": (
            "È vicino perché parla di individuare problemi reali, "
            "ma è sbagliato perché log e feedback servono proprio a migliorare sicurezza, qualità e affidabilità."
        ),
    },
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            dati,
            file,
            ensure_ascii=False,
            indent=2
        )
        file.write("\n")


def trova_liste_domande(dati):
    liste = []

    if isinstance(dati, list):
        liste.append(dati)

    elif isinstance(dati, dict):
        for valore in dati.values():
            if isinstance(valore, list):
                liste.append(valore)

    return liste


def aggiorna_file(percorso):
    dati = carica_json(percorso)
    liste_domande = trova_liste_domande(dati)

    modificato = False
    id_modificati = []

    for lista_domande in liste_domande:
        for domanda in lista_domande:
            if not isinstance(domanda, dict):
                continue

            id_domanda = domanda.get("id")

            if id_domanda in AGGIORNAMENTI:
                domanda.update(AGGIORNAMENTI[id_domanda])
                modificato = True
                id_modificati.append(id_domanda)

    if modificato:
        salva_json(percorso, dati)

    return id_modificati


def main():
    tutti_modificati = []

    for percorso in DATA_DIR.rglob("*.json"):
        id_modificati = aggiorna_file(percorso)

        if id_modificati:
            print("File aggiornato:", percorso)

            for id_domanda in id_modificati:
                print(" -", id_domanda)

            tutti_modificati.extend(id_modificati)

    mancanti = sorted(
        set(AGGIORNAMENTI.keys()) - set(tutti_modificati)
    )

    print("")
    print("Domande AI certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Categoria AI completata: tutte le AI sono ora certificate per il motore.")


main()