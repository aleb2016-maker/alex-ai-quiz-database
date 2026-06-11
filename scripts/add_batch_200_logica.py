import json
from pathlib import Path


# Questo script aggiunge il blocco Logica della seconda espansione.
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_logica = [
    {
        "id": "LOG-VER-FAC-0101",
        "categoria": "logica",
        "sottocategoria": "logica_verbale",
        "livello": "facile",
        "domanda": "Quale parola completa meglio l'analogia: caldo sta a freddo come alto sta a ___?",
        "opzioni": [
            "basso",
            "grande",
            "lungo",
            "vicino"
        ],
        "risposta_corretta": "basso",
        "spiegazione": "Caldo e freddo sono contrari. Seguendo la stessa logica, il contrario di alto è basso.",
        "tags": [
            "analogia",
            "contrari",
            "logica_verbale"
        ],
        "difficolta": 1
    },
    {
        "id": "LOG-VER-FAC-0102",
        "categoria": "logica",
        "sottocategoria": "logica_verbale",
        "livello": "facile",
        "domanda": "Quale parola non appartiene allo stesso gruppo?",
        "opzioni": [
            "tavolo",
            "sedia",
            "armadio",
            "martello"
        ],
        "risposta_corretta": "martello",
        "spiegazione": "Tavolo, sedia e armadio sono mobili. Martello è un attrezzo, quindi non appartiene allo stesso gruppo.",
        "tags": [
            "classificazione",
            "intruso",
            "logica_verbale"
        ],
        "difficolta": 1
    },
    {
        "id": "LOG-NUM-FAC-0101",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "facile",
        "domanda": "Una macchina produce 4 pezzi al minuto. Quanti pezzi produce in 5 minuti?",
        "opzioni": [
            "20",
            "18",
            "22",
            "24"
        ],
        "risposta_corretta": "20",
        "spiegazione": "La macchina produce 4 pezzi ogni minuto. In 5 minuti produce 4 × 5 = 20 pezzi.",
        "tags": [
            "moltiplicazione",
            "problemi",
            "logica_numerica"
        ],
        "difficolta": 1
    },
    {
        "id": "LOG-NUM-FAC-0102",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "facile",
        "domanda": "Partendo da 3, un numero viene raddoppiato quattro volte. Quale valore si ottiene?",
        "opzioni": [
            "48",
            "36",
            "42",
            "50"
        ],
        "risposta_corretta": "48",
        "spiegazione": "Partiamo da 3. Primo raddoppio: 6. Secondo: 12. Terzo: 24. Quarto: 48.",
        "tags": [
            "raddoppio",
            "calcolo",
            "logica_numerica"
        ],
        "difficolta": 1
    },
    {
        "id": "LOG-CRI-FAC-0101",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "facile",
        "domanda": "Tutti i cani sono animali. Fido è un cane. Quale conclusione è corretta?",
        "opzioni": [
            "Fido è un animale",
            "Tutti gli animali sono cani",
            "Fido non è un animale",
            "Alcuni cani non sono animali"
        ],
        "risposta_corretta": "Fido è un animale",
        "spiegazione": "Se tutti i cani sono animali e Fido è un cane, allora Fido appartiene al gruppo degli animali.",
        "tags": [
            "deduzione",
            "sillogismi",
            "ragionamento_critico"
        ],
        "difficolta": 1
    },
    {
        "id": "LOG-CRI-FAC-0102",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "facile",
        "domanda": "Se oggi piove, Marco prende l'ombrello. Oggi piove. Cosa si può concludere?",
        "opzioni": [
            "Marco prende l'ombrello",
            "Marco non prende l'ombrello",
            "Oggi non piove",
            "Marco prende sempre l'ombrello"
        ],
        "risposta_corretta": "Marco prende l'ombrello",
        "spiegazione": "La regola dice che quando piove Marco prende l'ombrello. Poiché oggi piove, la conclusione corretta è che Marco prende l'ombrello.",
        "tags": [
            "condizione",
            "deduzione",
            "ragionamento_critico"
        ],
        "difficolta": 1
    },
    {
        "id": "LOG-VER-INT-0101",
        "categoria": "logica",
        "sottocategoria": "logica_verbale",
        "livello": "intermedio",
        "domanda": "Completa l'analogia: medico sta a ospedale come insegnante sta a ___?",
        "opzioni": [
            "scuola",
            "libro",
            "classe",
            "lezione"
        ],
        "risposta_corretta": "scuola",
        "spiegazione": "Il medico lavora tipicamente in ospedale. Allo stesso modo, l'insegnante lavora tipicamente in una scuola. Classe e lezione sono collegate, ma non rappresentano il luogo generale equivalente.",
        "tags": [
            "analogie",
            "relazioni",
            "logica_verbale"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-VER-INT-0102",
        "categoria": "logica",
        "sottocategoria": "logica_verbale",
        "livello": "intermedio",
        "domanda": "Quale coppia mantiene la stessa relazione di: seme : pianta?",
        "opzioni": [
            "uovo : uccello",
            "foglia : ramo",
            "radice : terra",
            "frutto : albero"
        ],
        "risposta_corretta": "uovo : uccello",
        "spiegazione": "Dal seme può svilupparsi una pianta. In modo simile, dall'uovo può svilupparsi un uccello. Le altre coppie indicano parti o collegamenti, non una relazione di sviluppo.",
        "tags": [
            "analogie",
            "relazioni",
            "logica_verbale"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-NUM-INT-0101",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "intermedio",
        "domanda": "Un algoritmo parte da 2. A ogni passaggio raddoppia il valore e aggiunge 1. Dopo quattro passaggi quale valore ottiene?",
        "opzioni": [
            "47",
            "45",
            "46",
            "49"
        ],
        "risposta_corretta": "47",
        "spiegazione": "Partiamo da 2. Passaggio 1: 2 × 2 + 1 = 5. Passaggio 2: 5 × 2 + 1 = 11. Passaggio 3: 11 × 2 + 1 = 23. Passaggio 4: 23 × 2 + 1 = 47.",
        "tags": [
            "algoritmo",
            "pattern",
            "logica_numerica"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-NUM-INT-0102",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "intermedio",
        "domanda": "Completa la successione: 30, 27, 23, 18, ?",
        "opzioni": [
            "12",
            "14",
            "13",
            "15"
        ],
        "risposta_corretta": "12",
        "spiegazione": "Le diminuzioni aumentano di 1 ogni volta: -3, -4, -5. Dopo 18 bisogna togliere 6, quindi 18 - 6 = 12.",
        "tags": [
            "successioni",
            "differenze",
            "logica_numerica"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-CRI-INT-0101",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "intermedio",
        "domanda": "Alcuni programmatori conoscono Python. Tutti quelli che conoscono Python sanno usare variabili. Quale conclusione è sicuramente vera?",
        "opzioni": [
            "Alcuni programmatori sanno usare variabili",
            "Tutti i programmatori conoscono Python",
            "Chi sa usare variabili è sempre programmatore",
            "Nessun programmatore conosce Python"
        ],
        "risposta_corretta": "Alcuni programmatori sanno usare variabili",
        "spiegazione": "Se alcuni programmatori conoscono Python e tutti quelli che conoscono Python sanno usare variabili, allora almeno quei programmatori sanno usare variabili.",
        "tags": [
            "sillogismi",
            "deduzione",
            "ragionamento_critico"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-CRI-INT-0102",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "intermedio",
        "domanda": "Se un'app supera tutti i test, viene pubblicata. L'app non viene pubblicata. Quale conclusione è logicamente corretta?",
        "opzioni": [
            "L'app non ha superato tutti i test",
            "L'app ha superato tutti i test",
            "I test non sono mai stati eseguiti",
            "Ogni app pubblicata supera i test"
        ],
        "risposta_corretta": "L'app non ha superato tutti i test",
        "spiegazione": "La regola dice: se supera tutti i test, allora viene pubblicata. Se non viene pubblicata, possiamo concludere che non ha superato tutti i test. È un caso di ragionamento per contrapposizione.",
        "tags": [
            "condizioni",
            "contrapposizione",
            "ragionamento_critico"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-AST-INT-0101",
        "categoria": "logica",
        "sottocategoria": "ragionamento_astratto",
        "livello": "intermedio",
        "domanda": "Una sequenza alterna numero di lati così: triangolo, quadrato, pentagono, esagono, ?. Quale forma segue?",
        "opzioni": [
            "ettagono",
            "pentagono",
            "ottagono",
            "triangolo"
        ],
        "risposta_corretta": "ettagono",
        "spiegazione": "Le forme aumentano di un lato alla volta: triangolo 3 lati, quadrato 4, pentagono 5, esagono 6. Dopo viene l'ettagono, che ha 7 lati.",
        "tags": [
            "forme",
            "sequenze",
            "ragionamento_astratto"
        ],
        "difficolta": 2
    },
    {
        "id": "LOG-VER-AV-0101",
        "categoria": "logica",
        "sottocategoria": "logica_verbale",
        "livello": "avanzato",
        "domanda": "Completa l'analogia: allenamento sta a miglioramento come studio sta a ___?",
        "opzioni": [
            "apprendimento",
            "interrogazione",
            "lezione",
            "materia"
        ],
        "risposta_corretta": "apprendimento",
        "spiegazione": "L'allenamento può portare a un miglioramento. Allo stesso modo, lo studio può portare ad apprendimento. Interrogazione, lezione e materia sono collegate allo studio, ma non rappresentano il risultato logico più diretto.",
        "tags": [
            "analogie",
            "causa_effetto",
            "logica_verbale"
        ],
        "difficolta": 3
    },
    {
        "id": "LOG-NUM-AV-0101",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "avanzato",
        "domanda": "Completa la successione: 1, 4, 9, 16, 25, ?",
        "opzioni": [
            "36",
            "30",
            "35",
            "49"
        ],
        "risposta_corretta": "36",
        "spiegazione": "La sequenza contiene quadrati perfetti: 1²=1, 2²=4, 3²=9, 4²=16, 5²=25. Il successivo è 6²=36.",
        "tags": [
            "successioni",
            "quadrati",
            "logica_numerica"
        ],
        "difficolta": 3
    },
    {
        "id": "LOG-NUM-AV-0102",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "avanzato",
        "domanda": "Le differenze tra valori consecutivi sono 4, 6, 8 e 10. Se l'ultimo valore noto è 30, quale sarà il valore successivo?",
        "opzioni": [
            "42",
            "40",
            "44",
            "48"
        ],
        "risposta_corretta": "42",
        "spiegazione": "Le differenze aumentano di 2: 4, 6, 8, 10. La differenza successiva è 12. Quindi 30 + 12 = 42.",
        "tags": [
            "differenze",
            "pattern",
            "logica_numerica"
        ],
        "difficolta": 3
    },
    {
        "id": "LOG-CRI-AV-0101",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "avanzato",
        "domanda": "Tutti gli sviluppatori del team usano Git. Alcune persone che usano Git lavorano anche su database. Quale conclusione è sicuramente vera?",
        "opzioni": [
            "Alcune persone che usano Git lavorano su database",
            "Tutti gli sviluppatori lavorano su database",
            "Tutti quelli che usano Git sono sviluppatori",
            "Nessuno sviluppatore usa database"
        ],
        "risposta_corretta": "Alcune persone che usano Git lavorano su database",
        "spiegazione": "La seconda premessa afferma direttamente che alcune persone che usano Git lavorano anche su database. Non possiamo però concludere che siano sviluppatori o che tutti gli sviluppatori lavorino su database.",
        "tags": [
            "deduzione",
            "quantificatori",
            "ragionamento_critico"
        ],
        "difficolta": 3
    },
    {
        "id": "LOG-CRI-AV-0102",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "avanzato",
        "domanda": "Se il server è inattivo, l'app mostra un errore. L'app mostra un errore. Quale conclusione è corretta?",
        "opzioni": [
            "Il server potrebbe essere inattivo, ma non è certo",
            "Il server è sicuramente inattivo",
            "L'app non può mostrare errori per altri motivi",
            "Il server è sicuramente attivo"
        ],
        "risposta_corretta": "Il server potrebbe essere inattivo, ma non è certo",
        "spiegazione": "La regola dice che server inattivo implica errore, ma l'errore potrebbe avere anche altre cause. Concludere che il server è sicuramente inattivo sarebbe un errore logico.",
        "tags": [
            "implicazione",
            "errore_logico",
            "ragionamento_critico"
        ],
        "difficolta": 3
    },
    {
        "id": "LOG-AST-AV-0101",
        "categoria": "logica",
        "sottocategoria": "ragionamento_astratto",
        "livello": "avanzato",
        "domanda": "Una sequenza segue questa regola: una figura aumenta di un lato e cambia colore a ogni passaggio. Dopo triangolo rosso, quadrato blu, pentagono rosso, esagono blu, cosa viene?",
        "opzioni": [
            "ettagono rosso",
            "ettagono blu",
            "ottagono rosso",
            "pentagono blu"
        ],
        "risposta_corretta": "ettagono rosso",
        "spiegazione": "Il numero di lati aumenta: 3, 4, 5, 6, quindi 7 lati, cioè ettagono. Il colore alterna rosso, blu, rosso, blu, quindi il prossimo è rosso.",
        "tags": [
            "forme",
            "sequenze",
            "ragionamento_astratto"
        ],
        "difficolta": 3
    },
    {
        "id": "LOG-AST-AV-0102",
        "categoria": "logica",
        "sottocategoria": "ragionamento_astratto",
        "livello": "avanzato",
        "domanda": "In una sequenza, ogni figura ruota di 90° in senso orario a ogni passaggio. Se una freccia punta in alto, poi a destra, poi in basso, quale direzione segue?",
        "opzioni": [
            "sinistra",
            "alto",
            "destra",
            "basso"
        ],
        "risposta_corretta": "sinistra",
        "spiegazione": "La rotazione è sempre di 90° in senso orario: alto, destra, basso, sinistra.",
        "tags": [
            "rotazioni",
            "sequenze",
            "ragionamento_astratto"
        ],
        "difficolta": 3
    }
]


def carica_domande_esistenti():
    if not PERCORSO_OUTPUT.exists():
        return []

    with open(PERCORSO_OUTPUT, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_domande(domande):
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            domande,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():
    domande_esistenti = carica_domande_esistenti()

    nuovi_id = {
        domanda["id"]
        for domanda in nuove_domande_logica
    }

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_logica

    salva_domande(domande_finali)

    print("Blocco Logica aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Logica:", len(nuove_domande_logica))
    print("Domande totali in batch_200:", len(domande_finali))


main()
