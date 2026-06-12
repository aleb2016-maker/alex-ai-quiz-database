import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "AI-AV-0008": {
        "opzioni": [
            "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
            "Per valutare separatamente le fasi, ma senza collegare gli errori alla risposta finale",
            "Per controllare solo il recupero dei documenti ignorando la generazione",
            "Per controllare solo la generazione ignorando retrieval e verifica finale",
        ],
        "risposta_corretta": "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
        "spiegazione": (
            "Separare recupero, generazione e controllo finale rende la pipeline più osservabile e più facile da correggere. "
            "Non basta guardare una fase isolata: bisogna capire come ogni fase contribuisce alla qualità della risposta finale."
        ),
        "distrattore_forte": "Per valutare separatamente le fasi, ma senza collegare gli errori alla risposta finale",
        "motivo_distrattore_forte": (
            "È vicino perché parla davvero di valutare le fasi separatamente, "
            "ma è sbagliato perché separare le fasi serve proprio a collegare gli errori al punto della pipeline in cui nascono."
        ),
    },
    "AI-AV-0009": {
        "opzioni": [
            "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
            "Perché i dati sbilanciati possono introdurre distorsioni, ma obiettivi e metriche non incidono",
            "Perché solo una metrica scelta male può creare distorsioni, mentre i dati restano sempre neutrali",
            "Perché solo l'obiettivo di addestramento può creare distorsioni, mentre dati e metriche non contano",
        ],
        "risposta_corretta": "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
        "spiegazione": (
            "Un modello può essere implementato correttamente ma produrre risultati distorti se dati, obiettivi o metriche sono sbilanciati. "
            "Le altre opzioni indicano cause reali, ma le restringono troppo e quindi non spiegano il problema generale."
        ),
        "distrattore_forte": "Perché i dati sbilanciati possono introdurre distorsioni, ma obiettivi e metriche non incidono",
        "motivo_distrattore_forte": (
            "È vicino perché riconosce il ruolo dei dati sbilanciati, "
            "ma è sbagliato perché anche obiettivi e metriche possono introdurre distorsioni."
        ),
    },
    "AI-FAC-0101": {
        "opzioni": [
            "Riconoscere schemi nei dati e usare questi schemi per produrre risposte o previsioni",
            "Riconoscere schemi nei dati ma usarli solo per copiare risposte già presenti negli esempi",
            "Memorizzare dati senza estrarre schemi utili per fare previsioni",
            "Salvare file del computer senza usarli per produrre risposte o previsioni",
        ],
        "risposta_corretta": "Riconoscere schemi nei dati e usare questi schemi per produrre risposte o previsioni",
        "spiegazione": (
            "Un modello di intelligenza artificiale impara schemi dai dati e li usa per classificare, prevedere, generare testo o prendere decisioni. "
            "Non si limita a copiare esempi già presenti e non è semplicemente un archivio di file."
        ),
        "distrattore_forte": "Riconoscere schemi nei dati ma usarli solo per copiare risposte già presenti negli esempi",
        "motivo_distrattore_forte": (
            "È vicino perché parla di schemi nei dati, "
            "ma è sbagliato perché un modello AI non serve solo a copiare risposte già presenti: usa gli schemi per generalizzare."
        ),
    },
    "AI-FAC-0102": {
        "opzioni": [
            "Riassumi questo testo in 5 righe indicando le idee principali.",
            "Riassumi questo testo indicando le idee principali.",
            "Spiega questo testo mantenendo tutti i dettagli importanti.",
            "Riscrivi questo testo senza ridurlo e senza selezionare le idee principali.",
        ],
        "risposta_corretta": "Riassumi questo testo in 5 righe indicando le idee principali.",
        "spiegazione": (
            "Un prompt chiaro specifica cosa fare e con quale formato. "
            "Dire 'in 5 righe' e 'idee principali' rende il compito più controllabile. "
            "Le altre opzioni sono vicine al lavoro sul testo, ma non danno lo stesso vincolo preciso di riassunto breve."
        ),
        "distrattore_forte": "Riassumi questo testo indicando le idee principali.",
        "motivo_distrattore_forte": (
            "È molto vicino perché chiede comunque un riassunto delle idee principali, "
            "ma è meno preciso perché manca il vincolo delle 5 righe."
        ),
    },
    "AI-FAC-0103": {
        "opzioni": [
            "Perché influenzano ciò che il modello impara e come risponde",
            "Perché influenzano il modello, ma rendono inutile controllare le risposte generate",
            "Perché servono solo a verificare il modello dopo l'addestramento",
            "Perché definiscono manualmente ogni risposta che il modello dovrà dare",
        ],
        "risposta_corretta": "Perché influenzano ciò che il modello impara e come risponde",
        "spiegazione": (
            "Il modello impara dai dati disponibili durante l'addestramento. "
            "Se i dati sono incompleti, distorti o poco adatti, anche le risposte possono risentirne. "
            "Questo però non elimina la necessità di controllare le risposte generate."
        ),
        "distrattore_forte": "Perché influenzano il modello, ma rendono inutile controllare le risposte generate",
        "motivo_distrattore_forte": (
            "È vicino perché riconosce che i dati influenzano il modello, "
            "ma è sbagliato perché le risposte vanno comunque controllate."
        ),
    },
    "AI-FAC-0104": {
        "opzioni": [
            "Stabilire se un messaggio è spam o non spam",
            "Raggruppare messaggi simili senza etichette già definite",
            "Generare una risposta automatica a un messaggio",
            "Scrivere un nuovo messaggio partendo da un tema",
        ],
        "risposta_corretta": "Stabilire se un messaggio è spam o non spam",
        "spiegazione": (
            "La classificazione assegna un'etichetta a un input. "
            "Spam/non spam è un esempio classico perché il modello sceglie una categoria tra alternative definite. "
            "Il clustering raggruppa elementi simili, mentre la generazione produce nuovi contenuti."
        ),
        "distrattore_forte": "Raggruppare messaggi simili senza etichette già definite",
        "motivo_distrattore_forte": (
            "È vicino perché anche il clustering lavora su gruppi di dati, "
            "ma è sbagliato perché nella classificazione le categorie sono già definite."
        ),
    },
    "AI-FAC-0105": {
        "opzioni": [
            "Che crea una risposta nuova seguendo il contesto ricevuto",
            "Che riformula il testo ricevuto senza produrre realmente contenuto nuovo",
            "Che copia sempre una frase già presente nei dati",
            "Che seleziona una frase già scritta senza adattarla al contesto",
        ],
        "risposta_corretta": "Che crea una risposta nuova seguendo il contesto ricevuto",
        "spiegazione": (
            "Un modello generativo produce una continuazione o una risposta in base al contesto. "
            "Non si limita necessariamente a copiare una frase identica o a selezionare testo già scritto."
        ),
        "distrattore_forte": "Che riformula il testo ricevuto senza produrre realmente contenuto nuovo",
        "motivo_distrattore_forte": (
            "È vicino perché parla comunque di testo e contesto, "
            "ma è sbagliato perché un modello generativo può produrre contenuto nuovo, non solo riformulare."
        ),
    },
    "AI-FAC-0106": {
        "opzioni": [
            "A una risposta plausibile ma falsa o non verificata",
            "A una risposta plausibile ma incompleta, senza informazioni false",
            "A una risposta corretta ma troppo breve per essere utile",
            "A una risposta prudente che dichiara chiaramente incertezza",
        ],
        "risposta_corretta": "A una risposta plausibile ma falsa o non verificata",
        "spiegazione": (
            "Un'allucinazione in AI è una risposta che può sembrare credibile, ma contiene informazioni false, inventate o non verificate. "
            "Una risposta breve, incompleta o prudente può essere migliorabile, ma non è necessariamente un'allucinazione."
        ),
        "distrattore_forte": "A una risposta plausibile ma incompleta, senza informazioni false",
        "motivo_distrattore_forte": (
            "È vicino perché descrive una risposta plausibile ma problematica, "
            "ma è sbagliato perché l'allucinazione implica falsità, invenzione o mancanza di verifica."
        ),
    },
    "AI-INT-0102": {
        "opzioni": [
            "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
            "La ricerca semantica può usare parole diverse, ma funziona solo se restano presenti gli stessi termini principali",
            "La ricerca per parole esatte interpreta sempre il significato profondo della domanda",
            "La ricerca per parole esatte trova sinonimi anche quando non compaiono termini uguali",
        ],
        "risposta_corretta": "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
        "spiegazione": (
            "La ricerca per parole esatte cerca corrispondenze letterali. "
            "La ricerca semantica invece prova a confrontare il significato dei contenuti, quindi può trovare testi pertinenti anche se usano parole diverse dalla domanda."
        ),
        "distrattore_forte": "La ricerca semantica può usare parole diverse, ma funziona solo se restano presenti gli stessi termini principali",
        "motivo_distrattore_forte": (
            "È vicino perché parla di parole diverse e ricerca semantica, "
            "ma è sbagliato perché la ricerca semantica può basarsi sul significato anche senza gli stessi termini principali."
        ),
    },
    "AI-INT-0103": {
        "opzioni": [
            "Per misurare se generalizza oltre i casi usati per costruirlo",
            "Per verificare se ricorda con precisione gli esempi usati durante lo sviluppo",
            "Per misurare solo la velocità sui casi nuovi senza valutare l'accuratezza",
            "Per ridurre il tempo di esecuzione eliminando i dati di validazione",
        ],
        "risposta_corretta": "Per misurare se generalizza oltre i casi usati per costruirlo",
        "spiegazione": (
            "Un modello deve funzionare anche su casi nuovi. "
            "Testarlo solo su esempi già visti rischia di misurare la memoria, non la capacità di generalizzare."
        ),
        "distrattore_forte": "Per verificare se ricorda con precisione gli esempi usati durante lo sviluppo",
        "motivo_distrattore_forte": (
            "È vicino perché parla degli esempi usati nello sviluppo, "
            "ma è sbagliato perché il test deve misurare generalizzazione, non memoria."
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
        print("Terzo blocco AI certificato correttamente.")


main()