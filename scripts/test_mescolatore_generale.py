import random
from collections import Counter

def crea_posizioni_corrette_bilanciate(numero_domande):
    posizioni = []

    for indice in range(numero_domande):
        posizioni.append(indice % 4)

    random.shuffle(posizioni)
    return posizioni

def controlla(numero_domande):
    posizioni = crea_posizioni_corrette_bilanciate(numero_domande)
    conteggio = Counter(posizioni)

    print(f"\nTest con {numero_domande} domande")
    print("A:", conteggio[0])
    print("B:", conteggio[1])
    print("C:", conteggio[2])
    print("D:", conteggio[3])

    minimo = min(conteggio.values())
    massimo = max(conteggio.values())

    if massimo - minimo > 1:
        raise SystemExit("ERRORE: distribuzione non bilanciata")

for numero in [10, 20, 40, 200]:
    controlla(numero)

print("\nOK: il mescolatore generale distribuisce le risposte corrette in modo bilanciato.")
