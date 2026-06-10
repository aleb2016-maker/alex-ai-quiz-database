# Importiamo il generatore quiz.
from quiz_generator import genera_quiz_json

# Importiamo la funzione che recupera le memorie.
from database import recupera_memorie


# Questa funzione decide quale azione deve fare l'agente.
def scegli_azione_da_richiesta(messaggio_utente):
    testo = messaggio_utente.lower()

    if "quiz" in testo or "domande" in testo or "test" in testo:
        return "quiz"

    if "memoria" in testo or "ricorda" in testo or "preferenze" in testo:
        return "memoria"

    return "chat"


# Questa funzione esegue l'azione scelta.
def esegui_agente(messaggio_utente):
    azione = scegli_azione_da_richiesta(messaggio_utente)

    if azione == "quiz":
        quiz = genera_quiz_json(
            categoria="AI",
            difficolta="intermedio",
            numero_domande=5
        )

        return {
            "tipo": "quiz",
            "messaggio": "Ho capito che vuoi creare un quiz.",
            "risultato": quiz
        }

    if azione == "memoria":
        memorie = recupera_memorie()

        return {
            "tipo": "memoria",
            "messaggio": "Ho recuperato le memorie salvate.",
            "risultato": memorie
        }

    return {
        "tipo": "chat",
        "messaggio": "Risposta chat normale.",
        "risultato": "Hai scritto: " + messaggio_utente
    }