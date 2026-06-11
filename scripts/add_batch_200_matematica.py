import json
from pathlib import Path


# Questo script aggiunge il blocco Matematica della seconda espansione.
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_matematica = [
    {
        "id": "MAT-FAC-0101",
        "categoria": "matematica",
        "sottocategoria": "calcolo",
        "livello": "facile",
        "domanda": "Quanto fa 45 + 18?",
        "opzioni": [
            "63",
            "53",
            "61",
            "73"
        ],
        "risposta_corretta": "63",
        "spiegazione": "Sommiamo prima le unità: 5 + 8 = 13, scriviamo 3 e riportiamo 1. Poi sommiamo le decine: 4 + 1 + 1 di riporto = 6. Il risultato è 63.",
        "tags": [
            "somma",
            "calcolo",
            "aritmetica"
        ],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0102",
        "categoria": "matematica",
        "sottocategoria": "calcolo",
        "livello": "facile",
        "domanda": "Quanto fa 72 - 28?",
        "opzioni": [
            "44",
            "46",
            "54",
            "40"
        ],
        "risposta_corretta": "44",
        "spiegazione": "Per calcolare 72 - 28 possiamo fare 72 - 30 = 42 e poi aggiungere 2, perché abbiamo tolto 2 in più. Quindi 42 + 2 = 44.",
        "tags": [
            "sottrazione",
            "calcolo",
            "aritmetica"
        ],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0103",
        "categoria": "matematica",
        "sottocategoria": "moltiplicazioni",
        "livello": "facile",
        "domanda": "Quanto fa 12 × 6?",
        "opzioni": [
            "72",
            "62",
            "68",
            "78"
        ],
        "risposta_corretta": "72",
        "spiegazione": "12 × 6 significa sommare 12 per 6 volte oppure fare 10 × 6 + 2 × 6. Quindi 60 + 12 = 72.",
        "tags": [
            "moltiplicazione",
            "calcolo",
            "aritmetica"
        ],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0104",
        "categoria": "matematica",
        "sottocategoria": "divisioni",
        "livello": "facile",
        "domanda": "Se 56 caramelle vengono divise in 8 sacchetti uguali, quante caramelle ci sono in ogni sacchetto?",
        "opzioni": [
            "7",
            "6",
            "8",
            "9"
        ],
        "risposta_corretta": "7",
        "spiegazione": "Dividere 56 caramelle in 8 sacchetti uguali significa calcolare 56 / 8. Poiché 8 × 7 = 56, ogni sacchetto contiene 7 caramelle.",
        "tags": [
            "divisione",
            "problemi",
            "calcolo"
        ],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0105",
        "categoria": "matematica",
        "sottocategoria": "decimali",
        "livello": "facile",
        "domanda": "Quanto vale 0,5 di 30?",
        "opzioni": [
            "15",
            "10",
            "20",
            "25"
        ],
        "risposta_corretta": "15",
        "spiegazione": "0,5 significa metà. Calcolare 0,5 di 30 significa trovare la metà di 30. Quindi 30 / 2 = 15.",
        "tags": [
            "decimali",
            "meta",
            "calcolo"
        ],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0106",
        "categoria": "matematica",
        "sottocategoria": "geometria",
        "livello": "facile",
        "domanda": "Un triangolo ha base 10 cm e altezza 6 cm. Qual è la sua area?",
        "opzioni": [
            "30 cm²",
            "60 cm²",
            "16 cm²",
            "40 cm²"
        ],
        "risposta_corretta": "30 cm²",
        "spiegazione": "L'area del triangolo si calcola con base × altezza / 2. Quindi 10 × 6 = 60, poi 60 / 2 = 30 cm². 60 cm² sarebbe l'errore di dimenticare la divisione per 2.",
        "tags": [
            "triangolo",
            "area",
            "geometria"
        ],
        "difficolta": 1
    },
    {
        "id": "MAT-INT-0101",
        "categoria": "matematica",
        "sottocategoria": "percentuali",
        "livello": "intermedio",
        "domanda": "Un prezzo passa da 200 euro a 180 euro. Qual è la percentuale di diminuzione?",
        "opzioni": [
            "10%",
            "20%",
            "15%",
            "5%"
        ],
        "risposta_corretta": "10%",
        "spiegazione": "La diminuzione è 200 - 180 = 20 euro. La percentuale si calcola rispetto al valore iniziale: 20 / 200 × 100 = 10%.",
        "tags": [
            "percentuali",
            "diminuzione",
            "problemi"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0102",
        "categoria": "matematica",
        "sottocategoria": "proporzioni",
        "livello": "intermedio",
        "domanda": "Se 4 litri di vernice coprono 28 m², quanti metri quadrati coprono 7 litri allo stesso rendimento?",
        "opzioni": [
            "49 m²",
            "42 m²",
            "56 m²",
            "35 m²"
        ],
        "risposta_corretta": "49 m²",
        "spiegazione": "Prima calcoliamo quanto copre 1 litro: 28 / 4 = 7 m². Con 7 litri si coprono 7 × 7 = 49 m².",
        "tags": [
            "proporzioni",
            "problemi",
            "calcolo"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0103",
        "categoria": "matematica",
        "sottocategoria": "equazioni",
        "livello": "intermedio",
        "domanda": "Un servizio costa 6 euro di attivazione più 5 euro al mese. Se il totale è 31 euro, quanti mesi sono stati pagati?",
        "opzioni": [
            "5 mesi",
            "4 mesi",
            "6 mesi",
            "7 mesi"
        ],
        "risposta_corretta": "5 mesi",
        "spiegazione": "Prima togliamo il costo fisso di attivazione: 31 - 6 = 25 euro. Ogni mese costa 5 euro, quindi 25 / 5 = 5 mesi.",
        "tags": [
            "problemi",
            "equazioni",
            "calcolo"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0104",
        "categoria": "matematica",
        "sottocategoria": "media",
        "livello": "intermedio",
        "domanda": "La media di 12, 15, 18 e 19 è:",
        "opzioni": [
            "16",
            "15",
            "17",
            "18"
        ],
        "risposta_corretta": "16",
        "spiegazione": "Sommiamo i valori: 12 + 15 + 18 + 19 = 64. Poi dividiamo per 4 numeri: 64 / 4 = 16.",
        "tags": [
            "media",
            "statistica",
            "calcolo"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0105",
        "categoria": "matematica",
        "sottocategoria": "frazioni",
        "livello": "intermedio",
        "domanda": "Quale frazione è maggiore tra 3/5 e 4/7?",
        "opzioni": [
            "3/5",
            "4/7",
            "Sono uguali",
            "Non si possono confrontare"
        ],
        "risposta_corretta": "3/5",
        "spiegazione": "Per confrontarle possiamo usare il prodotto incrociato: 3 × 7 = 21 e 4 × 5 = 20. Poiché 21 è maggiore di 20, 3/5 è maggiore di 4/7.",
        "tags": [
            "frazioni",
            "confronto",
            "calcolo"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0106",
        "categoria": "matematica",
        "sottocategoria": "geometria",
        "livello": "intermedio",
        "domanda": "Un cerchio ha raggio 5 cm. Usando π ≈ 3,14, qual è circa la sua circonferenza?",
        "opzioni": [
            "31,4 cm",
            "15,7 cm",
            "78,5 cm",
            "25 cm"
        ],
        "risposta_corretta": "31,4 cm",
        "spiegazione": "La circonferenza si calcola con 2 × π × r. Quindi 2 × 3,14 × 5 = 31,4 cm. 78,5 cm² sarebbe invece l'area approssimata.",
        "tags": [
            "cerchio",
            "circonferenza",
            "geometria"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0107",
        "categoria": "matematica",
        "sottocategoria": "probabilita",
        "livello": "intermedio",
        "domanda": "In una scatola ci sono 5 penne nere, 3 blu e 2 rosse. Qual è la probabilità di estrarre una penna blu?",
        "opzioni": [
            "3/10",
            "3/8",
            "5/10",
            "2/10"
        ],
        "risposta_corretta": "3/10",
        "spiegazione": "Le penne totali sono 5 + 3 + 2 = 10. Le penne blu sono 3. La probabilità è casi favorevoli / casi totali, quindi 3/10.",
        "tags": [
            "probabilita",
            "frazioni",
            "problemi"
        ],
        "difficolta": 2
    },
    {
        "id": "MAT-AV-0101",
        "categoria": "matematica",
        "sottocategoria": "equazioni",
        "livello": "avanzato",
        "domanda": "Un rettangolo ha perimetro 34 cm e base 10 cm. Qual è la sua altezza?",
        "opzioni": [
            "7 cm",
            "6 cm",
            "8 cm",
            "5 cm"
        ],
        "risposta_corretta": "7 cm",
        "spiegazione": "Il perimetro del rettangolo è 2 × (base + altezza). Quindi 34 = 2 × (10 + altezza). Dividendo per 2 otteniamo 17 = 10 + altezza, quindi altezza = 7 cm.",
        "tags": [
            "geometria",
            "rettangolo",
            "problemi"
        ],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0102",
        "categoria": "matematica",
        "sottocategoria": "sistemi",
        "livello": "avanzato",
        "domanda": "La somma di due numeri è 35 e la loro differenza è 9. Qual è il numero maggiore?",
        "opzioni": [
            "22",
            "21",
            "23",
            "26"
        ],
        "risposta_corretta": "22",
        "spiegazione": "Se il numero maggiore è A e il minore è B, allora A + B = 35 e A - B = 9. Sommando le due equazioni otteniamo 2A = 44, quindi A = 22.",
        "tags": [
            "sistemi",
            "problemi",
            "algebra"
        ],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0103",
        "categoria": "matematica",
        "sottocategoria": "velocita",
        "livello": "avanzato",
        "domanda": "Un'auto percorre 150 km a 75 km/h. Quanto tempo impiega?",
        "opzioni": [
            "2 ore",
            "1,5 ore",
            "2,5 ore",
            "3 ore"
        ],
        "risposta_corretta": "2 ore",
        "spiegazione": "Il tempo si calcola facendo distanza / velocità. Quindi 150 / 75 = 2 ore.",
        "tags": [
            "velocita",
            "tempo",
            "problemi"
        ],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0104",
        "categoria": "matematica",
        "sottocategoria": "combinatoria",
        "livello": "avanzato",
        "domanda": "Da un gruppo di 5 persone bisogna scegliere presidente e vice. I ruoli sono diversi. Quante scelte possibili ci sono?",
        "opzioni": [
            "20",
            "10",
            "25",
            "15"
        ],
        "risposta_corretta": "20",
        "spiegazione": "Per scegliere il presidente ci sono 5 possibilità. Dopo aver scelto il presidente, restano 4 possibilità per il vice. Poiché i ruoli sono diversi, il totale è 5 × 4 = 20.",
        "tags": [
            "combinatoria",
            "ruoli",
            "calcolo"
        ],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0105",
        "categoria": "matematica",
        "sottocategoria": "percentuali",
        "livello": "avanzato",
        "domanda": "Un valore diminuisce del 20% e diventa 96. Qual era il valore iniziale?",
        "opzioni": [
            "120",
            "116",
            "100",
            "128"
        ],
        "risposta_corretta": "120",
        "spiegazione": "Se un valore diminuisce del 20%, resta l'80% del valore iniziale. Quindi 0,8x = 96. Dividendo 96 per 0,8 otteniamo x = 120.",
        "tags": [
            "percentuali",
            "valore_iniziale",
            "problemi"
        ],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0106",
        "categoria": "matematica",
        "sottocategoria": "rapporti",
        "livello": "avanzato",
        "domanda": "In una miscela il rapporto tra succo e acqua è 2:3. Se la miscela totale è 25 litri, quanti litri sono di succo?",
        "opzioni": [
            "10 litri",
            "15 litri",
            "12 litri",
            "8 litri"
        ],
        "risposta_corretta": "10 litri",
        "spiegazione": "Il rapporto 2:3 ha 5 parti totali. Se 5 parti valgono 25 litri, una parte vale 25 / 5 = 5 litri. Il succo corrisponde a 2 parti, quindi 2 × 5 = 10 litri.",
        "tags": [
            "rapporti",
            "proporzioni",
            "problemi"
        ],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0107",
        "categoria": "matematica",
        "sottocategoria": "potenze",
        "livello": "avanzato",
        "domanda": "Qual è il valore di 2³ + 3²?",
        "opzioni": [
            "17",
            "13",
            "25",
            "18"
        ],
        "risposta_corretta": "17",
        "spiegazione": "2³ significa 2 × 2 × 2 = 8. 3² significa 3 × 3 = 9. Sommando 8 + 9 otteniamo 17.",
        "tags": [
            "potenze",
            "calcolo",
            "ordine_operazioni"
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
        for domanda in nuove_domande_matematica
    }

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_matematica

    salva_domande(domande_finali)

    print("Blocco Matematica aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Matematica:", len(nuove_domande_matematica))
    print("Domande totali in batch_200:", len(domande_finali))


main()
