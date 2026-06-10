from difflib import SequenceMatcher
from pathlib import Path
from fastapi.responses import FileResponse
# Importiamo gli strumenti principali di Python.
import json
import re
import sqlite3
from datetime import datetime
from typing import Literal, Optional

# Importiamo FastAPI.
from fastapi import FastAPI, HTTPException

# Importiamo il middleware per permettere al frontend React di parlare con il backend.
from fastapi.middleware.cors import CORSMiddleware

# Importiamo Pydantic per controllare i dati in entrata e in uscita.
from pydantic import BaseModel

# Importiamo Ollama per usare una AI locale, senza API key esterne.
import ollama


# ============================================================
# CONFIGURAZIONE GENERALE
# ============================================================

# Nome del database SQLite locale.
NOME_DATABASE = "alex_ai_workspace.db"

# Modello locale usato da Ollama.
# Prima devi averlo scaricato con:
# ollama run gemma4:12b
MODELLO_OLLAMA = "gemma3:4b"


# ============================================================
# CONFIGURAZIONE FINALE SEZIONE INFORMATICA
# ============================================================

SOTTO_ARGOMENTI_INFORMATICA_COMPLETI = [
    "reti e protocolli TCP/IP",
    "database SQL, indici e query",
    "database NoSQL e coerenza dei dati",
    "programmazione Python e gestione memoria",
    "API REST, HTTP e JSON",
    "sicurezza informatica, autenticazione e autorizzazione",
    "sistemi distribuiti e message queue",
    "cache, memoria e ottimizzazione performance",
    "algoritmi e strutture dati",
    "programmazione orientata agli oggetti",
    "sistemi operativi, processi e thread",
    "Git, versionamento e collaborazione",
    "testing, debugging e gestione errori",
    "architettura client-server",
    "cloud, container e deployment",
    "complessità algoritmica Big O",
    "strutture dati avanzate",
    "concorrenza e asincronia",
    "file system e gestione file",
    "formati dati XML, CSV e YAML",
]


PAROLE_CHIAVE_SOTTO_ARGOMENTI_INFORMATICA = {
    "reti e protocolli TCP/IP": [
        "tcp", "udp", "ip", "http", "https", "dns", "pacchetto",
        "checksum", "ack", "ritrasmissione", "porta", "socket",
        "router", "switch", "lan", "latenza", "banda"
    ],
    "database SQL, indici e query": [
        "sql", "query", "select", "where", "join", "indice",
        "indici", "b-tree", "tabella", "colonna", "chiave primaria",
        "chiave esterna", "ordine", "cliente"
    ],
    "database NoSQL e coerenza dei dati": [
        "nosql", "documento", "mongodb", "redis", "cassandra",
        "consistenza", "coerenza", "replica", "sharding",
        "eventual consistency"
    ],
    "programmazione Python e gestione memoria": [
        "python", "generatore", "generatori", "iteratore", "iteratori",
        "yield", "lista", "tuple", "memoria", "ram", "dataset",
        "on-demand"
    ],
    "API REST, HTTP e JSON": [
        "api", "rest", "endpoint", "http", "json", "get", "post",
        "put", "delete", "status code", "request", "response"
    ],
    "sicurezza informatica, autenticazione e autorizzazione": [
        "sicurezza", "password", "token", "jwt", "oauth",
        "autenticazione", "autorizzazione", "crittografia",
        "hash", "permessi", "firewall"
    ],
    "sistemi distribuiti e message queue": [
        "distribuito", "microservizi", "message queue", "coda",
        "kafka", "rabbitmq", "evento", "asincrono", "consumatore",
        "produttore"
    ],
    "cache, memoria e ottimizzazione performance": [
        "cache", "caching", "performance", "ottimizzazione",
        "buffer", "latenza", "tempo di risposta", "throughput"
    ],
    "algoritmi e strutture dati": [
        "algoritmo", "array", "lista collegata", "stack", "queue",
        "coda", "albero", "grafo", "hash table", "ricerca",
        "ordinamento"
    ],
    "programmazione orientata agli oggetti": [
        "classe", "oggetto", "metodo", "attributo", "ereditarietà",
        "polimorfismo", "incapsulamento", "interfaccia"
    ],
    "sistemi operativi, processi e thread": [
        "processo", "thread", "sistema operativo", "kernel",
        "scheduling", "deadlock", "memoria virtuale"
    ],
    "Git, versionamento e collaborazione": [
        "git", "commit", "branch", "merge", "pull request",
        "repository", "versionamento", "conflitto"
    ],
    "testing, debugging e gestione errori": [
        "test", "debug", "debugging", "errore", "eccezione",
        "unit test", "assert", "log", "bug"
    ],
    "architettura client-server": [
        "client", "server", "frontend", "backend", "richiesta",
        "risposta", "architettura", "servizio"
    ],
    "cloud, container e deployment": [
        "cloud", "docker", "container", "kubernetes", "deploy",
        "deployment", "immagine", "scalabilità"
    ],
    "complessità algoritmica Big O": [
        "big o", "o(n)", "o(log n)", "o(n^2)", "complessità",
        "tempo", "spazio", "scalabilità"
    ],
    "strutture dati avanzate": [
        "heap", "trie", "grafo", "albero bilanciato", "hash map",
        "priority queue", "struttura dati"
    ],
    "concorrenza e asincronia": [
        "async", "await", "asincrono", "concorrenza", "parallelismo",
        "thread", "lock", "race condition"
    ],
    "file system e gestione file": [
        "file", "cartella", "path", "percorso", "lettura",
        "scrittura", "filesystem", "permessi file"
    ],
    "formati dati XML, CSV e YAML": [
        "xml", "csv", "yaml", "json", "formato dati",
        "serializzazione", "parsing"
    ],
}


# ============================================================
# CREAZIONE APP FASTAPI
# ============================================================

app = FastAPI(
    title="Alex AI Workspace",
    description="Agente personale locale con chat, memoria e generatore quiz AI.",
    version="2.0.0",
)


# Permettiamo al frontend React di collegarsi al backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELLI DATI: CHAT
# ============================================================

class RichiestaChat(BaseModel):
    messaggio: str


class RispostaChat(BaseModel):
    reply: str


# ============================================================
# MODELLI DATI: MEMORIA
# ============================================================

class RichiestaMemoria(BaseModel):
    title: str
    content: str
    category: str = "generale"


class MemoriaSalvata(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str


# ============================================================
# MODELLI DATI: QUIZ
# ============================================================

class RichiestaQuiz(BaseModel):
    categoria: str
    livello: str
    numero_domande: int


class OpzioneRisposta(BaseModel):
    lettera: Literal["A", "B", "C", "D"]
    testo: str


class DomandaQuiz(BaseModel):
    id: int
    categoria: str
    livello: str
    domanda: str
    opzioni: list[OpzioneRisposta]
    risposta_corretta: Literal["A", "B", "C", "D"]
    spiegazione: str


class QuizGenerato(BaseModel):
    quiz: list[DomandaQuiz]


# ============================================================
# MODELLI DATI: AGENT ROUTER
# ============================================================

class RichiestaAgente(BaseModel):
    tipo: Literal["chat", "quiz", "memoria"]
    messaggio: Optional[str] = None

    categoria: Optional[str] = None
    livello: Optional[str] = None
    numero_domande: Optional[int] = None

    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


# ============================================================
# FUNZIONI DATABASE
# ============================================================

def apri_connessione_database():
    connessione = sqlite3.connect(NOME_DATABASE)
    connessione.row_factory = sqlite3.Row
    return connessione


def inizializza_database():
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    # Tabella per salvare le conversazioni.
    cursore.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_reply TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Tabella per salvare le memorie.
    cursore.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Tabella per salvare i quiz generati.
    cursore.execute(
        """
        CREATE TABLE IF NOT EXISTS generated_quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            livello TEXT NOT NULL,
            numero_domande INTEGER NOT NULL,
            quiz_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connessione.commit()
    connessione.close()


def salva_conversazione(messaggio_utente: str, risposta_ai: str):
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    cursore.execute(
        """
        INSERT INTO conversations (user_message, ai_reply, created_at)
        VALUES (?, ?, ?)
        """,
        (
            messaggio_utente,
            risposta_ai,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    connessione.commit()
    connessione.close()


def salva_memoria(titolo: str, contenuto: str, categoria: str):
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    cursore.execute(
        """
        INSERT INTO memories (title, content, category, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            titolo,
            contenuto,
            categoria,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    id_memoria = cursore.lastrowid

    connessione.commit()
    connessione.close()

    return id_memoria


def salva_quiz_generato(
    categoria: str,
    livello: str,
    numero_domande: int,
    quiz_json: dict,
):
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    cursore.execute(
        """
        INSERT INTO generated_quizzes
        (categoria, livello, numero_domande, quiz_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            categoria,
            livello,
            numero_domande,
            json.dumps(quiz_json, ensure_ascii=False),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    id_quiz = cursore.lastrowid

    connessione.commit()
    connessione.close()

    return id_quiz


# ============================================================
# FUNZIONI AI CON OLLAMA
# ============================================================

def controlla_ollama_attivo():
    try:
        ollama.list()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Ollama non sembra attivo. "
                "Apri il terminale e avvia il modello con: "
                "ollama run gemma4:12b"
            ),
        )


def chiama_ollama_chat(messaggio_utente: str):
    controlla_ollama_attivo()

    try:
        risposta = ollama.chat(
            model=MODELLO_OLLAMA,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei l'agente personale di Alessandro. "
                        "Rispondi in italiano, in modo chiaro, pratico e ordinato."
                    ),
                },
                {
                    "role": "user",
                    "content": messaggio_utente,
                },
            ],
            options={
                "temperature": 0.4,
            },
        )

        return risposta["message"]["content"]

    except Exception as errore:
        raise HTTPException(
            status_code=500,
            detail=f"Errore nella chiamata a Ollama: {str(errore)}",
        )


def estrai_json_da_testo(testo_ai: str):
    testo_pulito = testo_ai.strip()

    # Se il modello mette il JSON dentro ```json ... ```,
    # togliamo quei simboli.
    testo_pulito = testo_pulito.replace("```json", "")
    testo_pulito = testo_pulito.replace("```", "")
    testo_pulito = testo_pulito.strip()

    # Cerchiamo il primo blocco che inizia con { e finisce con }.
    ricerca_json = re.search(r"\{.*\}", testo_pulito, re.DOTALL)

    if not ricerca_json:
        raise HTTPException(
            status_code=500,
            detail="La AI locale non ha restituito un JSON valido.",
        )

    blocco_json = ricerca_json.group(0)

    try:
        return json.loads(blocco_json)
    except json.JSONDecodeError as errore:
        raise HTTPException(
            status_code=500,
            detail=f"JSON generato non valido: {str(errore)}",
        )




def normalizza_quiz_generato(dati_quiz: dict):
    """
    Corregge piccoli errori comuni del modello AI prima della validazione.
    Esempio: "lettere" viene trasformato in "lettera".
    """

    if not isinstance(dati_quiz, dict):
        return dati_quiz

    # Se il modello usa "domande" invece di "quiz", lo correggiamo.
    if "quiz" not in dati_quiz and "domande" in dati_quiz:
        dati_quiz["quiz"] = dati_quiz.pop("domande")

    if "quiz" not in dati_quiz:
        return dati_quiz

    for domanda in dati_quiz["quiz"]:
        if not isinstance(domanda, dict):
            continue

        opzioni = domanda.get("opzioni", [])

        for opzione in opzioni:
            if not isinstance(opzione, dict):
                continue

            # Errore comune: il modello scrive "lettere" invece di "lettera".
            if "lettera" not in opzione and "lettere" in opzione:
                opzione["lettera"] = opzione.pop("lettere")

            # Errore possibile: il modello scrive "opzione" invece di "lettera".
            if "lettera" not in opzione and "opzione" in opzione:
                opzione["lettera"] = opzione.pop("opzione")

            # Errore possibile: il modello scrive "risposta" invece di "testo".
            if "testo" not in opzione and "risposta" in opzione:
                opzione["testo"] = opzione.pop("risposta")

    return dati_quiz


def valida_quiz_generato(dati_quiz: dict):
    dati_quiz = normalizza_quiz_generato(dati_quiz)

    try:
        quiz_validato = QuizGenerato.model_validate(dati_quiz)
    except Exception as errore:
        raise HTTPException(
            status_code=500,
            detail=f"Il quiz generato non rispetta la struttura richiesta: {str(errore)}",
        )

    return quiz_validato.model_dump()





def controlla_ollama():
    """
    Controlla che Ollama sia acceso e raggiungibile.
    Se Ollama non risponde, blocca la richiesta con un errore chiaro.
    """

    try:
        ollama.list()

    except Exception as errore:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama non risponde: {str(errore)}",
        )


def trova_famiglia_tecnica(testo_opzione: str):
    testo = testo_opzione.lower()

    famiglie = {
        "indici_sql": [
            "indice", "indici", "b-tree", "btree", "hash", "where",
            "join", "statistiche", "analyze", "tabella", "colonna",
            "query", "sql", "clausola", "piano di esecuzione"
        ],
        "rete": [
            "tcp", "udp", "pacchetto", "pacchetti", "latenza",
            "banda", "router", "switch", "ethernet", "lan",
            "rete", "protocollo", "qos"
        ],
        "cache_memoria": [
            "cache", "ram", "memoria", "buffer", "buffer pool",
            "allocazione", "heap", "stack"
        ],
        "api_rest": [
            "api", "rest", "endpoint", "http", "get", "post",
            "put", "delete", "status code", "json"
        ],
        "sicurezza": [
            "token", "jwt", "oauth", "autenticazione", "autorizzazione",
            "crittografia", "firewall", "rate limiting", "password",
            "permessi"
        ],
        "codice_applicativo": [
            "codice", "funzione", "variabile", "ciclo", "puntatore",
            "classe", "oggetto", "metodo", "applicazione"
        ],
    }

    punteggi = {}

    for famiglia, parole in famiglie.items():
        punteggio = 0

        for parola in parole:
            if parola in testo:
                punteggio += 1

        if punteggio > 0:
            punteggi[famiglia] = punteggio

    if not punteggi:
        return "generico"

    famiglia_migliore = max(
        punteggi,
        key=punteggi.get,
    )

    return famiglia_migliore





def controlla_domanda_ambigua(domanda: dict):
    """
    Controlla se una domanda è troppo ambigua o discutibile.
    Versione più intelligente:
    - blocca domande generiche e assolute;
    - accetta domande con un contesto tecnico preciso.
    """

    testo_domanda = domanda.get("domanda", "").lower()
    spiegazione = domanda.get("spiegazione", "").lower()

    frasi_rischiose = [
        "più efficace",
        "migliore",
        "miglior",
        "garantisce",
        "garantire",
        "garantito",
        "assicura",
        "assicurare",
        "fondamentale",
    ]

    frasi_molto_assolute = [
        "in assoluto",
        "sempre",
        "mai",
        "automaticamente",
    ]

    sotto_argomenti_delicati = [
        "frammentazione",
        "file system",
        "filesystem",
        "latenza",
        "prestazioni",
        "ottimizzazione",
        "sicurezza",
        "coerenza",
        "consistenza",
        "database distribuito",
        "nosql",
        "sincronizzazione",
        "message queue",
        "sistema distribuito",
    ]

    indicatori_contesto_preciso = [
        "in un sistema",
        "in una applicazione",
        "in un'applicazione",
        "in un database",
        "in una rete",
        "che utilizza",
        "considerando",
        "in caso di",
        "durante",
        "quando",
        "tra servizi",
        "con message queue",
        "per la propagazione",
        "per la comunicazione",
        "dopo una modifica",
        "in ambiente distribuito",
    ]

    contiene_frase_rischiosa = any(
        frase in testo_domanda
        for frase in frasi_rischiose
    )

    contiene_frase_molto_assoluta = any(
        frase in testo_domanda
        for frase in frasi_molto_assolute
    )

    contiene_argomento_delicato = any(
        argomento in testo_domanda
        for argomento in sotto_argomenti_delicati
    )

    ha_contesto_preciso = any(
        indicatore in testo_domanda
        for indicatore in indicatori_contesto_preciso
    )

    # Se usa parole molto assolute su argomenti delicati, blocchiamo.
    if contiene_frase_molto_assoluta and contiene_argomento_delicato:
        return (
            "La domanda usa una formula troppo assoluta. "
            "Deve essere riscritta con un contesto più preciso."
        )

    # Se usa formule rischiose ma ha un contesto tecnico preciso,
    # la lasciamo passare.
    if contiene_frase_rischiosa and contiene_argomento_delicato:
        if ha_contesto_preciso:
            return None

        return (
            "La domanda usa una formula troppo assoluta o discutibile. "
            "Deve essere riscritta con un contesto più preciso e una risposta "
            "corretta meno ambigua."
        )

    # Se la spiegazione dice apertamente che dipende dal contesto,
    # la domanda non è abbastanza precisa.
    if "dipende dal contesto" in spiegazione:
        return (
            "La spiegazione suggerisce che la risposta dipende dal contesto. "
            "La domanda deve essere resa più precisa."
        )

    return None



def controlla_errori_tecnici_specifici(domanda: dict):
    """
    Blocca errori tecnici ricorrenti del modello AI.
    Esempio: TCP non deve essere confuso con coerenza eventuale.
    """

    testi = []

    testi.append(domanda.get("domanda", ""))
    testi.append(domanda.get("spiegazione", ""))

    for opzione in domanda.get("opzioni", []):
        testi.append(opzione.get("testo", ""))

    testo_completo = " ".join(testi).lower()

    contiene_tcp = (
        "tcp" in testo_completo
        or "checksum" in testo_completo
        or "pacchetto" in testo_completo
        or "ritrasmissione" in testo_completo
    )

    contiene_coerenza_eventuale = (
        "coerenza eventuale" in testo_completo
        or "consistenza eventuale" in testo_completo
    )

    if contiene_tcp and contiene_coerenza_eventuale:
        return (
            "Errore tecnico: TCP non fornisce coerenza eventuale. "
            "TCP riguarda affidabilità, ordinamento, checksum, ACK e ritrasmissione."
        )

    parla_di_header_tcp = (
        "header tcp" in testo_completo
        or "intestazione tcp" in testo_completo
    )

    confonde_tcp_con_ip = (
        "indirizzi ip" in testo_completo
        or "indirizzo ip" in testo_completo
        or "routing" in testo_completo
        or "instradamento" in testo_completo
        or "indirizzi di destinazione e sorgente" in testo_completo
        or "indirizzi di origine e destinazione" in testo_completo
    )

    if parla_di_header_tcp and confonde_tcp_con_ip:
        return (
            "Errore tecnico: l'header TCP non contiene gli indirizzi IP "
            "e non gestisce il routing. Gli indirizzi IP e il routing appartengono "
            "al livello IP. TCP gestisce porte, numeri di sequenza, ACK, finestra, "
            "checksum, affidabilità e ordinamento del flusso."
        )

    if "::1" in testo_completo and "link-local" in testo_completo:
        return (
            "Errore tecnico: l'indirizzo IPv6 ::1 è loopback/localhost, "
            "non link-local. Gli indirizzi link-local usano fe80::/10."
        )

    return None


def controlla_qualita_quiz(quiz_finale: dict):
    problemi = []

    domande = quiz_finale.get("quiz", [])

    for domanda in domande:
        numero_domanda = domanda.get("id", "?")

        problema_ambiguita = controlla_domanda_ambigua(domanda)

        if problema_ambiguita:
            problemi.append(
                f"Domanda {numero_domanda}: {problema_ambiguita}"
            )

        problema_tecnico = controlla_errori_tecnici_specifici(domanda)

        if problema_tecnico:
            problemi.append(
                f"Domanda {numero_domanda}: {problema_tecnico}"
            )

        opzioni = domanda.get("opzioni", [])

        famiglie_trovate = []

        for opzione in opzioni:
            testo_opzione = opzione.get("testo", "")
            famiglia = trova_famiglia_tecnica(testo_opzione)

            if famiglia != "generico":
                famiglie_trovate.append(famiglia)

        famiglie_uniche = set(famiglie_trovate)

        if len(famiglie_uniche) > 1:
            problemi.append(
                f"Domanda {numero_domanda}: le opzioni mescolano famiglie diverse: "
                f"{sorted(famiglie_uniche)}"
            )

        lunghezze = []

        for opzione in opzioni:
            testo_opzione = opzione.get("testo", "")
            lunghezze.append(len(testo_opzione))

        if lunghezze:
            lunghezza_minima = min(lunghezze)
            lunghezza_massima = max(lunghezze)

            if lunghezza_minima > 0 and lunghezza_massima > lunghezza_minima * 3:
                problemi.append(
                    f"Domanda {numero_domanda}: una risposta è molto più lunga delle altre."
                )

    problemi_tecnici = controlla_errori_tecnici_informatica(quiz_finale)
    problemi.extend(problemi_tecnici)

    problemi_duplicati = controlla_duplicati_informatica(quiz_finale)
    problemi.extend(problemi_duplicati)

    return problemi


def crea_prompt_quiz_avanzato(richiesta: RichiestaQuiz, problemi_precedenti: str = ""):
    testo_problemi = ""

    if problemi_precedenti:
        testo_problemi = f"""
ATTENZIONE:
Il tentativo precedente è stato rifiutato dal controllo qualità.

Problemi trovati:
{problemi_precedenti}

Rigenera il quiz correggendo questi problemi.
"""

    return f"""
Crea un quiz in italiano.

Categoria: {richiesta.categoria}
Livello: {richiesta.livello}
Numero domande: {richiesta.numero_domande}

{testo_problemi}

REGOLE PRINCIPALI:
- Rispondi solo con JSON valido.
- Non usare markdown.
- Non restituire mai {{}}.
- Il JSON deve contenere sempre la chiave "quiz".
- La lista "quiz" deve contenere esattamente {richiesta.numero_domande} domande.
- Ogni domanda deve avere 4 opzioni: A, B, C, D.
- Ogni opzione deve avere le chiavi esatte "lettera" e "testo".
- Non usare "lettere", usa solo "lettera".
- Deve esserci una sola risposta corretta.



REGOLE PER DATABASE, NOSQL E SISTEMI DISTRIBUITI:
- Se parli di coerenza dei dati, specifica sempre se intendi:
  coerenza eventuale, sincronizzazione asincrona o coerenza forte.
- Non usare frasi generiche come "garantire la coerenza dei dati"
  senza dire il tipo di coerenza.
- Se la domanda parla di message queue, deve essere chiaro che si parla
  di propagazione asincrona o coerenza eventuale.
- Se la domanda parla di Paxos o Raft, deve essere chiaro che si parla
  di consenso distribuito o coerenza forte.




REGOLE TECNICHE FINALI PER TCP/IP:
- TCP non corregge direttamente gli errori nei dati.
- TCP rileva errori tramite checksum e gestisce ritrasmissioni tramite ACK, timeout o ACK duplicati.
- Non scrivere "TCP corregge gli errori"; scrivi "TCP rileva errori e richiede/gestisce la ritrasmissione".
- L'header TCP non contiene indirizzi IP.
- Gli indirizzi IP sorgente e destinazione stanno nell'header IP.
- Il routing/instradamento appartiene al livello IP, non al TCP.
- L'header TCP contiene porte, numeri di sequenza, ACK, flag, finestra e checksum.
- TCP gestisce affidabilità, ordinamento del flusso, controllo del flusso e ritrasmissione.
- Non usare concetti come "coerenza eventuale" per spiegare TCP.


FORMULAZIONE DOMANDE NON AMBIGUE:
- Non usare formule troppo assolute come:
  "più efficace", "migliore", "in assoluto", "garantisce", "sempre", "mai".
- Non scrivere domande generiche del tipo:
  "Quale tecnica è più efficace per ottimizzare..."
- Scrivi sempre un contesto preciso.
- La risposta corretta deve dipendere chiaramente dal contesto dato nella domanda.
- Preferisci domande pratiche e contestualizzate.

Esempio buono:
"In un programma Python che deve elaborare un file CSV molto grande senza caricarlo tutto in RAM, quale scelta è più adatta?"

Esempio cattivo:
"Quale tecnica è più efficace per ridurre la memoria?"


QUALITÀ DELLE DOMANDE:
- Ogni domanda deve testare un concetto reale.
- Le domande non devono essere banali.
- Le risposte devono essere simili tra loro.
- La risposta corretta non deve essere evidente solo perché è più lunga o più tecnica.

REGOLA FONDAMENTALE SULLE RISPOSTE:
Scegli un sotto-argomento preciso per ogni domanda.
Tutte e 4 le opzioni devono appartenere allo stesso sotto-argomento.

Esempio corretto se il tema è "indici SQL":
A) Creare un indice sulle colonne usate in WHERE e JOIN
B) Creare indici su tutte le colonne della tabella
C) Usare solo indici hash anche per ricerche per intervallo
D) Aggiornare le statistiche degli indici dopo grandi modifiche ai dati

Esempio sbagliato da evitare:
A) Creare un indice
B) Aumentare la RAM
C) Usare cache applicativa
D) Cambiare server

SPIEGAZIONE:
La spiegazione deve dire:
- perché la risposta corretta è giusta;
- perché le altre risposte sono sbagliate, incomplete o meno precise.

STRUTTURA JSON OBBLIGATORIA:
{{
  "quiz": [
    {{
      "id": 1,
      "categoria": "{richiesta.categoria}",
      "livello": "{richiesta.livello}",
      "domanda": "Testo della domanda",
      "opzioni": [
        {{"lettera": "A", "testo": "Prima opzione"}},
        {{"lettera": "B", "testo": "Seconda opzione"}},
        {{"lettera": "C", "testo": "Terza opzione"}},
        {{"lettera": "D", "testo": "Quarta opzione"}}
      ],
      "risposta_corretta": "A",
      "spiegazione": "Spiegazione chiara."
    }}
  ]
}}
"""








# ============================================================
# PROFILO SICURO INFORMATICA
# ============================================================

SOTTO_ARGOMENTI_INFORMATICA_COMPLETI = [
    "database SQL, indici e query",
    "database NoSQL e coerenza dei dati",
    "programmazione Python e gestione memoria",
    "API REST, HTTP e JSON",
    "sicurezza informatica, autenticazione e autorizzazione",
    "cache, memoria e ottimizzazione performance",
    "algoritmi e strutture dati",
    "programmazione orientata agli oggetti",
    "sistemi operativi, processi e thread",
    "Git, versionamento e collaborazione",
    "testing, debugging e gestione errori",
    "architettura client-server",
    "cloud, container e deployment",
    "complessità algoritmica Big O",
    "strutture dati avanzate",
    "concorrenza e asincronia",
    "file system e gestione file",
    "formati dati XML, CSV e YAML",
]

ARGOMENTI_INFORMATICA_MESSI_IN_PAUSA = [
    "reti e protocolli TCP/IP",
    "sistemi distribuiti e message queue",
]

# ============================================================
# STRUMENTI FINALI PER JSON ANDROID-READY INFORMATICA
# ============================================================

def normalizza_testo_per_confronto(testo: str):
    testo = testo.lower()
    caratteri_da_togliere = ",.;:!?()[]{}'\"`"

    for carattere in caratteri_da_togliere:
        testo = testo.replace(carattere, " ")

    parole = testo.split()

    parole_utili = [
        parola for parola in parole
        if len(parola) > 3
    ]

    return " ".join(parole_utili)


def similarita_testi(testo_1: str, testo_2: str):
    testo_1 = normalizza_testo_per_confronto(testo_1)
    testo_2 = normalizza_testo_per_confronto(testo_2)

    if not testo_1 or not testo_2:
        return 0

    return SequenceMatcher(None, testo_1, testo_2).ratio()


def trova_sotto_argomento_informatica(domanda: dict):
    testo_completo = domanda.get("domanda", "") + " "

    for opzione in domanda.get("opzioni", []):
        testo_completo += opzione.get("testo", "") + " "

    testo_completo += domanda.get("spiegazione", "")
    testo_completo = testo_completo.lower()

    punteggi = {}

    for sotto_argomento, parole_chiave in PAROLE_CHIAVE_SOTTO_ARGOMENTI_INFORMATICA.items():
        punteggio = 0

        for parola in parole_chiave:
            if parola.lower() in testo_completo:
                punteggio += 1

        if punteggio > 0:
            punteggi[sotto_argomento] = punteggio

    if not punteggi:
        return "informatica generale"

    return max(
        punteggi,
        key=punteggi.get,
    )


def prepara_quiz_informatica_android_ready(quiz_finale: dict, richiesta: RichiestaQuiz):
    """
    Aggiunge il campo sotto_argomento dentro ogni domanda di Informatica.
    Questo rende il JSON più utile per Android e Codex.
    """

    categoria = richiesta.categoria.lower().strip()

    if categoria != "informatica":
        return quiz_finale

    domande = quiz_finale.get("quiz", [])

    for domanda in domande:
        if not isinstance(domanda, dict):
            continue

        domanda["categoria"] = "Informatica"

        if not domanda.get("sotto_argomento"):
            domanda["sotto_argomento"] = trova_sotto_argomento_informatica(domanda)

    return quiz_finale


def leggi_domande_informatica_gia_generate():
    """
    Legge le domande già presenti nei JSON generati.
    Serve per evitare domande troppo simili quando generiamo blocchi grandi.
    """

    domande_esistenti = []

    cartella_file = Path("generated_files")

    if not cartella_file.exists():
        return domande_esistenti

    for file_json in cartella_file.glob("*.json"):
        try:
            with open(file_json, "r", encoding="utf-8") as file:
                dati = json.load(file)

            for domanda in dati.get("quiz", []):
                if not isinstance(domanda, dict):
                    continue

                categoria = domanda.get("categoria", "").lower()

                if categoria == "informatica":
                    testo_domanda = domanda.get("domanda", "")

                    if testo_domanda:
                        domande_esistenti.append(testo_domanda)

        except Exception:
            continue

    return domande_esistenti




def controlla_errori_tecnici_informatica(quiz_finale: dict):
    """
    Controllo tecnico specifico per Informatica.
    Serve a bloccare domande formalmente valide ma tecnicamente sbagliate.
    """

    problemi = []

    for domanda in quiz_finale.get("quiz", []):
        if not isinstance(domanda, dict):
            continue

        categoria = domanda.get("categoria", "").lower()

        if categoria != "informatica":
            continue

        testo_domanda = domanda.get("domanda", "").lower()
        spiegazione = domanda.get("spiegazione", "").lower()
        risposta_corretta = domanda.get("risposta_corretta", "").strip().upper()

        opzioni = domanda.get("opzioni", [])

        testo_risposta_corretta = ""

        for opzione in opzioni:
            if opzione.get("lettera", "").strip().upper() == risposta_corretta:
                testo_risposta_corretta = opzione.get("testo", "").lower()

        testo_totale = (
            testo_domanda + " " +
            testo_risposta_corretta + " " +
            spiegazione
        )

        # Caso 1: exactly once nei sistemi distribuiti.
        # Paxos/Raft/consenso non bastano da soli a garantire processing exactly-once.
        if (
            "esattamente una volta" in testo_totale
            or "exactly once" in testo_totale
        ):
            parole_buone = [
                "idempotenza",
                "idempotente",
                "deduplicazione",
                "deduplica",
                "transazione",
                "transaction",
                "offset",
                "commit atomico",
                "outbox",
            ]

            contiene_concetto_giusto = any(
                parola in testo_totale
                for parola in parole_buone
            )

            if not contiene_concetto_giusto:
                problemi.append(
                    "Domanda Informatica tecnicamente rischiosa: "
                    "exactly-once senza idempotenza/deduplicazione/transazioni."
                )

            if (
                "paxos" in testo_risposta_corretta
                or "raft" in testo_risposta_corretta
                or "consenso distribuito" in testo_risposta_corretta
            ):
                problemi.append(
                    "Domanda Informatica errata: Paxos/Raft non garantiscono "
                    "da soli il processing exactly-once dei messaggi."
                )

        # Caso 2: TCP payload size.
        # TCP non ha un campo semplice che dica 'dimensione payload'.
        # Window Size non indica il payload; Data Offset indica lunghezza header.
        if (
            "tcp" in testo_domanda
            and "payload" in testo_domanda
            and (
                "dimensione" in testo_domanda
                or "size" in testo_domanda
                or "lunghezza" in testo_domanda
            )
        ):
            if "window size" in testo_risposta_corretta:
                problemi.append(
                    "Domanda Informatica errata: TCP Window Size non indica "
                    "la dimensione del payload."
                )

            if "data offset" in testo_risposta_corretta:
                problemi.append(
                    "Domanda Informatica imprecisa: TCP Data Offset indica "
                    "la lunghezza dell'header, non direttamente la dimensione payload."
                )


        # Caso 2B: TCP flow control vs congestion control.
        # Il flow control protegge il ricevente tramite receive window.
        # Il congestion control protegge la rete dalla congestione.
        if (
            "tcp" in testo_domanda
            and (
                "controllo del flusso" in testo_domanda
                or "flow control" in testo_domanda
                or "host ricevente" in testo_domanda
                or "ricevente venga sopraffatto" in testo_domanda
            )
        ):
            if "congestion control" in spiegazione:
                problemi.append(
                    "Domanda Informatica errata: confonde TCP flow control "
                    "con congestion control."
                )

            if (
                "ritrasmettendo i pacchetti persi" in testo_risposta_corretta
                or "pacchetti persi" in testo_risposta_corretta
            ):
                problemi.append(
                    "Domanda Informatica imprecisa: nel TCP flow control "
                    "il punto centrale è la receive window, non la ritrasmissione "
                    "dei pacchetti persi."
                )

            parole_giuste_flow_control = [
                "receive window",
                "finestra di ricezione",
                "rwnd",
                "riduce la finestra",
                "attende che la finestra",
                "advertised window",
            ]

            contiene_flow_control_corretto = any(
                parola in testo_totale
                for parola in parole_giuste_flow_control
            )

            if not contiene_flow_control_corretto:
                problemi.append(
                    "Domanda Informatica rischiosa: parla di TCP flow control "
                    "ma non cita receive window/finestra di ricezione."
                )

        # Caso 3: formulazioni troppo assolute.
        parole_assolute = [
            "garantisce sempre",
            "garantisce che",
            "in ogni caso",
            "sempre corretto",
            "mai necessario",
        ]

        if any(parola in testo_totale for parola in parole_assolute):
            problemi.append(
                "Domanda Informatica con formulazione troppo assoluta: "
                "rischia di essere tecnicamente imprecisa."
            )

    return problemi


def controlla_duplicati_informatica(quiz_finale: dict):
    """
    Controlla se una nuova domanda è troppo simile:
    - a un'altra domanda dello stesso quiz;
    - a domande Informatica già generate in precedenza.
    """

    problemi = []

    domande_nuove = []

    for domanda in quiz_finale.get("quiz", []):
        if not isinstance(domanda, dict):
            continue

        categoria = domanda.get("categoria", "").lower()

        if categoria != "informatica":
            continue

        testo_domanda = domanda.get("domanda", "")

        if testo_domanda:
            domande_nuove.append(testo_domanda)

    # Controllo duplicati dentro lo stesso quiz.
    for indice_1, domanda_1 in enumerate(domande_nuove):
        for indice_2, domanda_2 in enumerate(domande_nuove):
            if indice_2 <= indice_1:
                continue

            valore_similarita = similarita_testi(domanda_1, domanda_2)

            if valore_similarita >= 0.84:
                problemi.append(
                    "Due domande nuove sono troppo simili tra loro."
                )

    # Controllo duplicati con domande già generate.
    domande_esistenti = leggi_domande_informatica_gia_generate()

    for domanda_nuova in domande_nuove:
        for domanda_esistente in domande_esistenti:
            valore_similarita = similarita_testi(
                domanda_nuova,
                domanda_esistente,
            )

            if valore_similarita >= 0.88:
                problemi.append(
                    "Una domanda nuova è troppo simile a una domanda Informatica già generata."
                )
                break

    return problemi


def revisiona_quiz_con_ollama(quiz_validato: dict, richiesta: RichiestaQuiz):
    """
    Secondo passaggio AI:
    controlla se il quiz è corretto, chiaro e con risposte davvero simili.
    Se trova problemi, corregge il quiz mantenendo la stessa struttura JSON.
    """

    prompt_revisione = f"""
Sei un revisore esperto di quiz tecnici.

Controlla questo quiz JSON.

Devi verificare:
- Evita domande dove due opzioni potrebbero essere entrambe corrette.
- Evita domande troppo specialistiche su TCP, checksum, Window Size, flow control, congestion control, Paxos, Raft ed exactly-once.
- Per ora, se la categoria è Informatica, preferisci domande su SQL, Python, REST, OOP, Git, testing, Big O, file system, sicurezza base e strutture dati.
- Per il JSON finale Informatica evita completamente TCP, UDP, Paxos, Raft, message queue, exactly-once e sistemi distribuiti.
- Non generare più di una domanda sullo stesso sotto-argomento nello stesso JSON finale.

Devi verificare:

REGOLE TECNICHE IMPORTANTI PER INFORMATICA:
- Paxos/Raft non garantiscono da soli exactly-once processing.
- Per exactly-once processing servono concetti come idempotenza, deduplicazione, transazioni, offset/commit o transactional outbox.
- TCP Window Size non indica la dimensione del payload.
- TCP flow control e congestion control non sono la stessa cosa.
- TCP flow control protegge il ricevente tramite receive window/finestra di ricezione.
- TCP congestion control protegge la rete dalla congestione.
- Se una domanda parla di flow control TCP, la risposta corretta deve parlare di receive window o finestra di ricezione.
- TCP Data Offset indica la lunghezza dell'header TCP, non direttamente la dimensione del payload.
- Evita domande con formule troppo assolute come "garantisce sempre" se il concetto dipende dal contesto.
- Se una domanda è tecnicamente ambigua, riscrivila in modo più sicuro e verificabile.

Devi verificare:
- la risposta corretta è davvero corretta;
- la domanda è chiara e non contiene frasi strane;
- le 4 opzioni appartengono allo stesso sotto-argomento;
- le risposte non sono troppo facili da distinguere;
- la spiegazione è chiara;
- non ci sono frasi confuse;
- non ci sono risposte che dicono praticamente la stessa cosa;
- la risposta corretta non deve essere discutibile.

Esempio di problema da correggere:
Se una domanda parla di riduzione della memoria in Python,
la risposta corretta dovrebbe spesso riguardare generatori,
iteratori, yield o elaborazione progressiva,
non una frase confusa come "lista compresa invece di comprensione di lista".

Se il quiz va bene, restituisci lo stesso JSON.
Se il quiz ha problemi, correggilo.

REGOLE OBBLIGATORIE:
- Rispondi solo con JSON valido.
- Non usare markdown.
- Mantieni la chiave principale "quiz".
- Ogni opzione deve avere le chiavi esatte "lettera" e "testo".
- Non usare "lettere".
- Mantieni categoria: {richiesta.categoria}
- Mantieni livello: {richiesta.livello}
- Mantieni esattamente lo stesso numero di domande.
- Ogni domanda deve avere 4 opzioni: A, B, C, D.
- Ogni domanda deve avere una sola risposta corretta.

Quiz da revisionare:
{json.dumps(quiz_validato, ensure_ascii=False, indent=2)}
"""

    try:
        risposta = ollama.chat(
            model=MODELLO_OLLAMA,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei un revisore severo di quiz tecnici. "
                        "Devi rispondere solo con JSON valido."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt_revisione,
                },
            ],
            format="json",
            options={
                "temperature": 0.1,
                "num_predict": 1200,
            },
        )

        testo_ai = risposta["message"]["content"]
        dati_json = estrai_json_da_testo(testo_ai)
        quiz_revisionato = valida_quiz_generato(dati_json)

        return quiz_revisionato

    except Exception:
        # Se il revisore AI fallisce, non blocchiamo il backend.
        # Torniamo al quiz originale già validato.
        return quiz_validato




def forza_categoria_livello_quiz(quiz_validato: dict, richiesta: RichiestaQuiz):
    """
    Corregge categoria, livello e id dopo la generazione AI.
    Il modello può cambiare categoria, ma l'app Android deve ricevere
    categorie stabili e coerenti con la richiesta originale.
    """

    domande = quiz_validato.get("quiz", [])

    for indice, domanda in enumerate(domande, start=1):
        domanda["id"] = indice
        domanda["categoria"] = richiesta.categoria
        domanda["livello"] = richiesta.livello

        risposta_corretta = domanda.get("risposta_corretta", "")

        if isinstance(risposta_corretta, str):
            domanda["risposta_corretta"] = risposta_corretta.upper().strip()

    return quiz_validato




def pulisci_testo_generato(testo: str):
    """
    Pulisce piccoli errori linguistici prodotti dal modello AI.
    Non cambia il significato tecnico della domanda.
    """

    if not isinstance(testo, str):
        return testo

    testo = testo.strip()

    correzioni = {
        "delle messaggi": "dei messaggi",
        "della messaggi": "dei messaggi",
        "le messaggi": "i messaggi",
        "delle dati": "dei dati",
        "Questa approccio": "Questo approccio",
        "questa approccio": "questo approccio",
        "un approccio che consente una maggiore latenza accettabile": "un approccio che consente una latenza accettabile",
        "consente una maggiore latenza accettabile": "consente una latenza accettabile",
        "una maggiore latenza accettabile": "una latenza accettabile",
        "è impraticabile": "può essere impraticabile",
        "raramente è necessaria": "non è sempre necessaria",
        "La risposta corretta è": "La risposta corretta è",
    }

    for errore, correzione in correzioni.items():
        testo = testo.replace(errore, correzione)

    while "  " in testo:
        testo = testo.replace("  ", " ")

    testo = testo.replace(" ,", ",")
    testo = testo.replace(" .", ".")
    testo = testo.replace(" ;", ";")
    testo = testo.replace(" :", ":")

    return testo


def pulisci_qualita_linguistica_quiz(quiz_validato: dict):
    """
    Applica la pulizia linguistica a domanda, opzioni e spiegazione.
    """

    domande = quiz_validato.get("quiz", [])

    for domanda in domande:
        domanda["domanda"] = pulisci_testo_generato(
            domanda.get("domanda", "")
        )

        domanda["spiegazione"] = pulisci_testo_generato(
            domanda.get("spiegazione", "")
        )

        opzioni = domanda.get("opzioni", [])

        for opzione in opzioni:
            opzione["testo"] = pulisci_testo_generato(
                opzione.get("testo", "")
            )

    return quiz_validato


def genera_quiz_con_ollama(richiesta: RichiestaQuiz):
    controlla_ollama()

    if richiesta.numero_domande <= 0:
        raise HTTPException(
            status_code=400,
            detail="Il numero di domande deve essere maggiore di zero.",
        )

    if richiesta.numero_domande > 20:
        raise HTTPException(
            status_code=400,
            detail=(
                "Per ora genera massimo 20 domande alla volta. "
                "Con i modelli locali è meglio creare blocchi piccoli."
            ),
        )

    problemi_precedenti = ""
    ultimo_errore = ""

    numero_massimo_tentativi = 4

    for tentativo in range(1, numero_massimo_tentativi + 1):
        prompt_quiz = crea_prompt_quiz_avanzato(
            richiesta=richiesta,
            problemi_precedenti=problemi_precedenti,
        )

        try:
            risposta = ollama.chat(
                model=MODELLO_OLLAMA,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sei un generatore professionale di quiz didattici. "
                            "Devi rispondere solo con JSON valido."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt_quiz,
                    },
                ],
                format="json",
                options={
                    "temperature": 0.3,
                    "num_predict": 1200,
                },
            )

            testo_ai = risposta["message"]["content"]

            dati_json = estrai_json_da_testo(testo_ai)

            quiz_validato = valida_quiz_generato(dati_json)

            quiz_validato = revisiona_quiz_con_ollama(
                quiz_validato=quiz_validato,
                richiesta=richiesta,
            )

            quiz_validato = prepara_quiz_informatica_android_ready(
                quiz_finale=quiz_validato,
                richiesta=richiesta,
            )

            quiz_validato = forza_categoria_livello_quiz(
                quiz_validato=quiz_validato,
                richiesta=richiesta,
            )

            quiz_validato = pulisci_qualita_linguistica_quiz(
                quiz_validato=quiz_validato,
            )

            problemi_qualita = controlla_qualita_quiz(quiz_validato)

            if problemi_qualita:
                problemi_precedenti = "\n".join(problemi_qualita)
                ultimo_errore = problemi_precedenti
                continue

            id_quiz_salvato = salva_quiz_generato(
                categoria=richiesta.categoria,
                livello=richiesta.livello,
                numero_domande=richiesta.numero_domande,
                quiz_json=quiz_validato,
            )

            return {
                "messaggio": "Quiz generato con AI locale tramite Ollama.",
                "modello": MODELLO_OLLAMA,
                "tentativo_usato": tentativo,
                "id_quiz_salvato": id_quiz_salvato,
                "download_latest_url": "/download-latest-quiz-json",
                "download_latest_full_url": "http://127.0.0.1:8000/download-latest-quiz-json",
                "risultato": quiz_validato,
            }

        except HTTPException as errore:
            ultimo_errore = str(errore.detail)
            problemi_precedenti = ultimo_errore
            continue

        except Exception as errore:
            ultimo_errore = str(errore)
            problemi_precedenti = ultimo_errore
            continue

    raise HTTPException(
        status_code=422,
        detail=(
            "Non sono riuscito a generare un quiz con qualità sufficiente "
            f"dopo {numero_massimo_tentativi} tentativi. "
            f"Ultimo problema: {ultimo_errore}"
        ),
    )

# ============================================================
# ENDPOINT PRINCIPALE
# ============================================================

@app.get("/")
def home():
    return {
        "messaggio": "Backend Alex AI Workspace attivo.",
        "ai_locale": "Ollama",
        "modello": MODELLO_OLLAMA,
        "endpoint_disponibili": [
            "GET /",
            "POST /chat",
            "GET /conversations",
            "POST /memory",
            "GET /memories",
            "POST /generate-quiz-json",
            "GET /generated-quizzes",
            "POST /agent_router",
        ],
    }


# ============================================================
# ENDPOINT CHAT
# ============================================================

@app.post("/chat")
def chat(richiesta: RichiestaChat):
    messaggio_utente = richiesta.messaggio.strip()

    if messaggio_utente == "":
        raise HTTPException(
            status_code=400,
            detail="Devi scrivere un messaggio.",
        )

    risposta_ai = chiama_ollama_chat(messaggio_utente)

    salva_conversazione(
        messaggio_utente=messaggio_utente,
        risposta_ai=risposta_ai,
    )

    return {
        "tipo": "chat",
        "messaggio": messaggio_utente,
        "reply": risposta_ai,
    }


# ============================================================
# ENDPOINT CONVERSAZIONI
# ============================================================

@app.get("/conversations")
def get_conversations():
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    cursore.execute(
        """
        SELECT id, user_message, ai_reply, created_at
        FROM conversations
        ORDER BY id DESC
        LIMIT 50
        """
    )

    righe = cursore.fetchall()
    connessione.close()

    conversazioni = []

    for riga in righe:
        conversazioni.append(
            {
                "id": riga["id"],
                "user_message": riga["user_message"],
                "ai_reply": riga["ai_reply"],
                "created_at": riga["created_at"],
            }
        )

    return conversazioni


# ============================================================
# ENDPOINT MEMORIA
# ============================================================

@app.post("/memory")
def create_memory(richiesta: RichiestaMemoria):
    titolo = richiesta.title.strip()
    contenuto = richiesta.content.strip()
    categoria = richiesta.category.strip()

    if titolo == "":
        raise HTTPException(
            status_code=400,
            detail="Il titolo della memoria non può essere vuoto.",
        )

    if contenuto == "":
        raise HTTPException(
            status_code=400,
            detail="Il contenuto della memoria non può essere vuoto.",
        )

    id_memoria = salva_memoria(
        titolo=titolo,
        contenuto=contenuto,
        categoria=categoria,
    )

    return {
        "tipo": "memoria",
        "messaggio": "Memoria salvata.",
        "risultato": {
            "id": id_memoria,
            "title": titolo,
            "content": contenuto,
            "category": categoria,
        },
    }


@app.get("/memories")
def get_memories():
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    cursore.execute(
        """
        SELECT id, title, content, category, created_at
        FROM memories
        ORDER BY id DESC
        LIMIT 50
        """
    )

    righe = cursore.fetchall()
    connessione.close()

    memorie = []

    for riga in righe:
        memorie.append(
            {
                "id": riga["id"],
                "title": riga["title"],
                "content": riga["content"],
                "category": riga["category"],
                "created_at": riga["created_at"],
            }
        )

    return {
        "tipo": "memoria",
        "messaggio": "Ho recuperato le memorie salvate.",
        "risultato": memorie,
    }


# ============================================================
# ENDPOINT QUIZ
# ============================================================

@app.post("/generate-quiz-json")
def generate_quiz_json(richiesta: RichiestaQuiz):
    return genera_quiz_con_ollama(richiesta)


@app.get("/generated-quizzes")
def get_generated_quizzes():
    connessione = apri_connessione_database()
    cursore = connessione.cursor()

    cursore.execute(
        """
        SELECT id, categoria, livello, numero_domande, quiz_json, created_at
        FROM generated_quizzes
        ORDER BY id DESC
        LIMIT 20
        """
    )

    righe = cursore.fetchall()
    connessione.close()

    quiz_salvati = []

    for riga in righe:
        quiz_salvati.append(
            {
                "id": riga["id"],
                "categoria": riga["categoria"],
                "livello": riga["livello"],
                "numero_domande": riga["numero_domande"],
                "quiz_json": json.loads(riga["quiz_json"]),
                "created_at": riga["created_at"],
            }
        )

    return {
        "tipo": "quiz",
        "messaggio": "Ho recuperato i quiz generati.",
        "risultato": quiz_salvati,
    }


# ============================================================
# AGENT ROUTER
# ============================================================

@app.post("/agent_router")
def agent_router(richiesta: RichiestaAgente):
    if richiesta.tipo == "chat":
        if not richiesta.messaggio:
            raise HTTPException(
                status_code=400,
                detail="Per il tipo chat devi inserire messaggio.",
            )

        richiesta_chat = RichiestaChat(
            messaggio=richiesta.messaggio,
        )

        return chat(richiesta_chat)

    if richiesta.tipo == "quiz":
        if not richiesta.categoria:
            raise HTTPException(
                status_code=400,
                detail="Per il tipo quiz devi inserire categoria.",
            )

        if not richiesta.livello:
            raise HTTPException(
                status_code=400,
                detail="Per il tipo quiz devi inserire livello.",
            )

        if not richiesta.numero_domande:
            raise HTTPException(
                status_code=400,
                detail="Per il tipo quiz devi inserire numero_domande.",
            )

        richiesta_quiz = RichiestaQuiz(
            categoria=richiesta.categoria,
            livello=richiesta.livello,
            numero_domande=richiesta.numero_domande,
        )

        return genera_quiz_con_ollama(richiesta_quiz)

    if richiesta.tipo == "memoria":
        if not richiesta.title:
            raise HTTPException(
                status_code=400,
                detail="Per il tipo memoria devi inserire title.",
            )

        if not richiesta.content:
            raise HTTPException(
                status_code=400,
                detail="Per il tipo memoria devi inserire content.",
            )

        categoria_memoria = richiesta.category or "generale"

        richiesta_memoria = RichiestaMemoria(
            title=richiesta.title,
            content=richiesta.content,
            category=categoria_memoria,
        )

        return create_memory(richiesta_memoria)

    raise HTTPException(
        status_code=400,
        detail="Tipo agente non valido.",
    )


# ============================================================
# AVVIO DATABASE
# ============================================================

inizializza_database()

# ============================================================
# ENDPOINT CONTROLLO OLLAMA
# ============================================================

@app.get("/health-ollama")
def health_ollama():
    try:
        modelli = ollama.list()

        return {
            "stato": "ok",
            "messaggio": "Ollama è attivo.",
            "modello_usato": MODELLO_OLLAMA,
            "modelli_installati": modelli,
        }

    except Exception as errore:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama non risponde: {str(errore)}",
        )


# ============================================================
# DOWNLOAD JSON QUIZ GENERATI
# ============================================================

def trova_ultimo_file_json_generato():
    """
    Trova l'ultimo file JSON generato nella cartella generated_files.
    """

    cartella_file = Path("generated_files")

    if not cartella_file.exists():
        raise HTTPException(
            status_code=404,
            detail="La cartella generated_files non esiste ancora.",
        )

    file_json = list(cartella_file.glob("*.json"))

    if not file_json:
        raise HTTPException(
            status_code=404,
            detail="Non ci sono ancora file JSON generati.",
        )

    ultimo_file = max(
        file_json,
        key=lambda file: file.stat().st_mtime,
    )

    return ultimo_file


@app.get("/download-latest-quiz-json")
def download_latest_quiz_json():
    """
    Scarica l'ultimo JSON generato.
    Utile per passarlo a Codex o usarlo nell'app Android.
    """

    ultimo_file = trova_ultimo_file_json_generato()

    return FileResponse(
        path=str(ultimo_file),
        filename=ultimo_file.name,
        media_type="application/json",
    )




# ============================================================
# GENERAZIONE QUIZ IN BLOCCHI CON ROTAZIONE SOTTO-ARGOMENTI
# ============================================================

class RichiestaQuizBatch(BaseModel):
    categoria: str
    livello: str
    numero_totale_domande: int
    dimensione_blocco: int = 5


def scegli_sotto_argomenti_categoria(categoria: str):
    """
    Restituisce una lista di sotto-argomenti per rendere il batch più vario.
    """

    categoria_normale = categoria.lower().strip()

    mappa_sotto_argomenti = {
        "informatica": [
            "reti e protocolli TCP/IP",
            "database SQL, indici e query",
            "database NoSQL e coerenza dei dati",
            "programmazione Python e gestione memoria",
            "API REST, HTTP e JSON",
            "sicurezza informatica, autenticazione e autorizzazione",
            "sistemi distribuiti e message queue",
            "cache, memoria e ottimizzazione performance",
            "algoritmi e strutture dati",
            "programmazione orientata agli oggetti",
        ],
        "ai": [
            "machine learning supervisionato",
            "reti neurali e deep learning",
            "LLM e prompt engineering",
            "RAG e basi vettoriali",
            "agenti AI e tool use",
            "valutazione dei modelli AI",
            "bias, sicurezza ed etica AI",
            "embedding e similarità semantica",
            "fine-tuning e adattamento modelli",
            "computer vision e classificazione immagini",
        ],
        "matematica": [
            "percentuali e proporzioni",
            "equazioni di primo grado",
            "geometria piana",
            "statistica di base",
            "probabilità",
            "funzioni e grafici",
            "potenze e radici",
            "aritmetica e calcolo mentale",
            "problemi con formule",
            "logica matematica",
        ],
        "inglese": [
            "comprensione del testo",
            "tempi verbali",
            "preposizioni",
            "lessico tecnico informatico",
            "phrasal verbs semplici",
            "conditionals",
            "comparativi e superlativi",
            "modali",
            "formazione delle domande",
            "false friends",
        ],
        "logica": [
            "logica verbale",
            "ragionamento critico",
            "logica numerica",
            "ragionamento astratto",
            "serie numeriche",
            "analogie",
            "deduzioni",
            "sillogismi",
            "sequenze alfabetiche",
            "pattern visivi descritti a parole",
        ],
    }

    if categoria_normale in mappa_sotto_argomenti:
        return mappa_sotto_argomenti[categoria_normale]

    return [
        f"concetti base di {categoria}",
        f"concetti intermedi di {categoria}",
        f"applicazioni pratiche di {categoria}",
        f"problemi tipici di {categoria}",
        f"errori comuni in {categoria}",
    ]


def crea_categoria_prompt_con_sotto_argomenti(
    categoria_finale: str,
    sotto_argomenti_blocco: list,
):
    """
    Crea una categoria descrittiva solo per guidare Gemma.
    Nel JSON finale la categoria viene poi riportata alla categoria originale.
    """

    elenco = []

    for indice, sotto_argomento in enumerate(sotto_argomenti_blocco, start=1):
        elenco.append(
            f"Domanda {indice}: {sotto_argomento}"
        )

    testo_elenco = "; ".join(elenco)

    return (
        f"{categoria_finale}. "
        f"Sotto-argomenti obbligatori e diversi per questo blocco: "
        f"{testo_elenco}. "
        f"Ogni domanda deve rispettare il proprio sotto-argomento."
    )


def genera_singola_domanda_batch(
    categoria_finale: str,
    livello: str,
    sotto_argomento: str,
):
    """
    Genera una singola domanda usando un sotto-argomento preciso.
    Serve come fallback quando un blocco più grande fallisce.
    """

    categoria_prompt = (
        f"{categoria_finale}. "
        f"Sotto-argomento obbligatorio: {sotto_argomento}. "
        f"Crea una sola domanda su questo sotto-argomento."
    )

    richiesta_singola = RichiestaQuiz(
        categoria=categoria_prompt,
        livello=livello,
        numero_domande=1,
    )

    risultato = genera_quiz_con_ollama(richiesta_singola)

    quiz_blocco = risultato.get("risultato", {})
    domande = quiz_blocco.get("quiz", [])

    if len(domande) != 1:
        raise HTTPException(
            status_code=500,
            detail="La generazione singola non ha prodotto esattamente 1 domanda.",
        )

    return {
        "domande": domande,
        "id_quiz_salvato": risultato.get("id_quiz_salvato"),
        "tentativo_usato": risultato.get("tentativo_usato"),
        "modalita": "singola",
        "sotto_argomento": sotto_argomento,
    }


def genera_blocco_batch_con_fallback(
    categoria_finale: str,
    livello: str,
    sotto_argomenti_blocco: list,
):
    """
    Prova prima a generare un blocco intero con sotto-argomenti diversi.
    Se fallisce, divide il blocco in domande singole.
    """

    numero_domande_blocco = len(sotto_argomenti_blocco)

    # Se il blocco contiene una sola domanda, evitiamo il tentativo "blocco".
    # Generiamo direttamente la domanda singola: è più veloce e stabile.
    if numero_domande_blocco == 1:
        sotto_argomento = sotto_argomenti_blocco[0]

        risultato_singola = genera_singola_domanda_batch(
            categoria_finale=categoria_finale,
            livello=livello,
            sotto_argomento=sotto_argomento,
        )

        return {
            "domande": risultato_singola["domande"],
            "id_quiz_salvato": risultato_singola.get("id_quiz_salvato"),
            "tentativo_usato": risultato_singola.get("tentativo_usato"),
            "modalita": "singola_diretta",
            "errore_blocco": None,
            "sotto_argomenti": sotto_argomenti_blocco,
            "report_singole": [
                {
                    "numero_singola": 1,
                    "modalita": "singola_diretta",
                    "sotto_argomento": sotto_argomento,
                    "id_quiz_salvato": risultato_singola.get("id_quiz_salvato"),
                    "tentativo_usato": risultato_singola.get("tentativo_usato"),
                }
            ],
        }

    categoria_prompt = crea_categoria_prompt_con_sotto_argomenti(
        categoria_finale=categoria_finale,
        sotto_argomenti_blocco=sotto_argomenti_blocco,
    )

    richiesta_blocco = RichiestaQuiz(
        categoria=categoria_prompt,
        livello=livello,
        numero_domande=numero_domande_blocco,
    )

    try:
        risultato_blocco = genera_quiz_con_ollama(richiesta_blocco)

        quiz_blocco = risultato_blocco.get("risultato", {})
        domande_blocco = quiz_blocco.get("quiz", [])

        if len(domande_blocco) != numero_domande_blocco:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Il blocco doveva contenere {numero_domande_blocco} domande, "
                    f"ma ne contiene {len(domande_blocco)}."
                ),
            )

        return {
            "domande": domande_blocco,
            "id_quiz_salvato": risultato_blocco.get("id_quiz_salvato"),
            "tentativo_usato": risultato_blocco.get("tentativo_usato"),
            "modalita": "blocco",
            "errore_blocco": None,
            "sotto_argomenti": sotto_argomenti_blocco,
        }

    except HTTPException as errore_blocco:
        domande_finali_blocco = []
        report_singole = []

        for indice, sotto_argomento in enumerate(sotto_argomenti_blocco, start=1):
            try:
                risultato_singola = genera_singola_domanda_batch(
                    categoria_finale=categoria_finale,
                    livello=livello,
                    sotto_argomento=sotto_argomento,
                )

                domande_finali_blocco.extend(
                    risultato_singola["domande"]
                )

                report_singole.append(
                    {
                        "numero_singola": indice,
                        "modalita": "singola",
                        "sotto_argomento": sotto_argomento,
                        "id_quiz_salvato": risultato_singola.get("id_quiz_salvato"),
                        "tentativo_usato": risultato_singola.get("tentativo_usato"),
                    }
                )

            except HTTPException as errore_singola:
                raise HTTPException(
                    status_code=errore_singola.status_code,
                    detail=(
                        "Anche il fallback a domanda singola è fallito. "
                        f"Errore blocco originale: {errore_blocco.detail}. "
                        f"Errore domanda singola {indice}: {errore_singola.detail}"
                    ),
                )

        return {
            "domande": domande_finali_blocco,
            "id_quiz_salvato": None,
            "tentativo_usato": None,
            "modalita": "fallback_singole",
            "errore_blocco": str(errore_blocco.detail),
            "sotto_argomenti": sotto_argomenti_blocco,
            "report_singole": report_singole,
        }


@app.post("/generate-quiz-batch-json")
def generate_quiz_batch_json(richiesta_batch: RichiestaQuizBatch):
    """
    Genera un quiz grande dividendolo in piccoli blocchi.
    Ogni domanda viene guidata da un sotto-argomento diverso.
    Se un blocco fallisce, prova automaticamente con domande singole.
    Alla fine salva un unico JSON finale scaricabile.
    """

    if richiesta_batch.numero_totale_domande <= 0:
        raise HTTPException(
            status_code=400,
            detail="Il numero totale di domande deve essere maggiore di zero.",
        )

    if richiesta_batch.dimensione_blocco <= 0:
        raise HTTPException(
            status_code=400,
            detail="La dimensione del blocco deve essere maggiore di zero.",
        )

    if richiesta_batch.dimensione_blocco > 10:
        raise HTTPException(
            status_code=400,
            detail=(
                "Per stabilità, usa blocchi da massimo 10 domande. "
                "Consigliato: 1, 2, 3 o 5."
            ),
        )

    if richiesta_batch.numero_totale_domande > 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "Per ora genera massimo 100 domande per richiesta batch. "
                "Per numeri più grandi, fai più batch separati."
            ),
        )

    sotto_argomenti_disponibili = scegli_sotto_argomenti_categoria(
        richiesta_batch.categoria
    )

    domande_finali = []
    report_blocchi = []

    domande_rimanenti = richiesta_batch.numero_totale_domande
    numero_blocco = 0
    indice_sotto_argomento = 0

    while domande_rimanenti > 0:
        numero_blocco += 1

        numero_domande_blocco = min(
            richiesta_batch.dimensione_blocco,
            domande_rimanenti,
        )

        sotto_argomenti_blocco = []

        for _ in range(numero_domande_blocco):
            sotto_argomento = sotto_argomenti_disponibili[
                indice_sotto_argomento % len(sotto_argomenti_disponibili)
            ]

            sotto_argomenti_blocco.append(sotto_argomento)
            indice_sotto_argomento += 1

        risultato_blocco = genera_blocco_batch_con_fallback(
            categoria_finale=richiesta_batch.categoria,
            livello=richiesta_batch.livello,
            sotto_argomenti_blocco=sotto_argomenti_blocco,
        )

        domande_blocco = risultato_blocco.get("domande", [])

        if len(domande_blocco) != numero_domande_blocco:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Il blocco {numero_blocco} doveva contenere "
                    f"{numero_domande_blocco} domande, ma ne contiene "
                    f"{len(domande_blocco)}."
                ),
            )

        for domanda in domande_blocco:
            domanda["id"] = len(domande_finali) + 1
            domanda["categoria"] = richiesta_batch.categoria
            domanda["livello"] = richiesta_batch.livello

            domande_finali.append(domanda)

        report_blocco = {
            "blocco": numero_blocco,
            "domande_generate": numero_domande_blocco,
            "modalita": risultato_blocco.get("modalita"),
            "sotto_argomenti": sotto_argomenti_blocco,
            "id_quiz_blocco_salvato": risultato_blocco.get("id_quiz_salvato"),
            "tentativo_usato": risultato_blocco.get("tentativo_usato"),
            "errore_blocco": risultato_blocco.get("errore_blocco"),
        }

        if "report_singole" in risultato_blocco:
            report_blocco["report_singole"] = risultato_blocco["report_singole"]

        report_blocchi.append(report_blocco)

        domande_rimanenti -= numero_domande_blocco

    quiz_finale = {
        "quiz": domande_finali,
    }

    richiesta_finale = RichiestaQuiz(
        categoria=richiesta_batch.categoria,
        livello=richiesta_batch.livello,
        numero_domande=richiesta_batch.numero_totale_domande,
    )

    quiz_finale = forza_categoria_livello_quiz(
        quiz_validato=quiz_finale,
        richiesta=richiesta_finale,
    )

    quiz_finale = pulisci_qualita_linguistica_quiz(
        quiz_validato=quiz_finale,
    )

    id_quiz_finale = salva_quiz_generato(
        categoria=richiesta_batch.categoria,
        livello=richiesta_batch.livello,
        numero_domande=richiesta_batch.numero_totale_domande,
        quiz_json=quiz_finale,
    )

    return {
        "messaggio": "Quiz batch generato correttamente con rotazione sotto-argomenti.",
        "modello": MODELLO_OLLAMA,
        "categoria": richiesta_batch.categoria,
        "livello": richiesta_batch.livello,
        "numero_domande_generate": len(domande_finali),
        "dimensione_blocco": richiesta_batch.dimensione_blocco,
        "blocchi_generati": numero_blocco,
        "sotto_argomenti_usati": sotto_argomenti_disponibili,
        "id_quiz_finale_salvato": id_quiz_finale,
        "download_latest_url": "/download-latest-quiz-json",
        "download_latest_full_url": "http://127.0.0.1:8000/download-latest-quiz-json",
        "report_blocchi": report_blocchi,
        "risultato": quiz_finale,
    }




# ============================================================
# FILTRO FINALE SICURO INFORMATICA
# ============================================================

SOTTO_ARGOMENTI_INFORMATICA_SICURI_FINALI = [
    "database SQL, indici e query",
    "programmazione Python e gestione memoria",
    "API REST, HTTP e JSON",
    "sicurezza informatica, autenticazione e autorizzazione",
    "cache, memoria e ottimizzazione performance",
    "algoritmi e strutture dati",
    "programmazione orientata agli oggetti",
    "sistemi operativi, processi e thread",
    "Git, versionamento e collaborazione",
    "testing, debugging e gestione errori",
    "architettura client-server",
    "cloud, container e deployment",
    "complessità algoritmica Big O",
    "strutture dati avanzate",
    "concorrenza e asincronia",
    "file system e gestione file",
    "formati dati XML, CSV e YAML",
]

PAROLE_BLOCCATE_INFORMATICA_FINALE = [
    "tcp",
    "udp",
    "checksum",
    "window size",
    "receive window",
    "flow control",
    "congestion control",
    "paxos",
    "raft",
    "exactly once",
    "esattamente una volta",
    "message queue",
    "coda di messaggi",
    "messaggistica distribuita",
    "sistema distribuito",
    "sistemi distribuiti",
    "replicati su più server",
]


def testo_completo_domanda(domanda: dict):
    testo = domanda.get("domanda", "") + " "
    testo += domanda.get("spiegazione", "") + " "

    for opzione in domanda.get("opzioni", []):
        testo += opzione.get("testo", "") + " "

    return testo.lower()


def domanda_informatica_finale_sicura(domanda: dict):
    testo = testo_completo_domanda(domanda)

    for parola in PAROLE_BLOCCATE_INFORMATICA_FINALE:
        if parola in testo:
            return False, f"contiene argomento rischioso: {parola}"

    sotto_argomento = domanda.get("sotto_argomento", "")

    if sotto_argomento not in SOTTO_ARGOMENTI_INFORMATICA_SICURI_FINALI:
        return False, f"sotto_argomento non sicuro: {sotto_argomento}"

    return True, "ok"


def scegli_sotto_argomento_informatica_sicuro(indice: int):
    posizione = indice % len(SOTTO_ARGOMENTI_INFORMATICA_SICURI_FINALI)

    return SOTTO_ARGOMENTI_INFORMATICA_SICURI_FINALI[posizione]


# ============================================================
# ENDPOINT FINALE INFORMATICA ANDROID-READY
# ============================================================

@app.post("/generate-informatica-final-json")
def generate_informatica_final_json(richiesta: RichiestaQuiz):
    """
    Genera un JSON finale di Informatica pronto per Android/Codex.

    Invece di chiedere tante domande insieme al modello,
    genera una domanda alla volta e poi unisce tutto.
    Questo evita errori JSON lunghi tipo virgole mancanti.
    """

    if richiesta.categoria.lower().strip() != "informatica":
        raise HTTPException(
            status_code=400,
            detail="Questo endpoint serve solo per la categoria Informatica.",
        )

    if richiesta.numero_domande <= 0:
        raise HTTPException(
            status_code=400,
            detail="Il numero di domande deve essere maggiore di zero.",
        )

    if richiesta.numero_domande > 50:
        raise HTTPException(
            status_code=400,
            detail=(
                "Per sicurezza genera massimo 50 domande alla volta. "
                "Poi puoi ripetere il comando per creare altri blocchi."
            ),
        )

    quiz_finale = {
        "quiz": []
    }

    report_generazione = []
    tentativi_totali = 0
    massimo_tentativi_totali = richiesta.numero_domande * 8

    while (
        len(quiz_finale["quiz"]) < richiesta.numero_domande
        and tentativi_totali < massimo_tentativi_totali
    ):
        tentativi_totali += 1

        richiesta_singola = RichiestaQuiz(
            categoria="Informatica",
            livello=richiesta.livello,
            numero_domande=1,
        )

        try:
            risultato_singolo = genera_quiz_con_ollama(richiesta_singola)

            domande_generate = risultato_singolo.get(
                "risultato",
                {},
            ).get(
                "quiz",
                [],
            )

            if not domande_generate:
                report_generazione.append({
                    "tentativo": tentativi_totali,
                    "stato": "scartato",
                    "motivo": "nessuna domanda generata",
                })
                continue

            domanda = domande_generate[0]

            nuovo_id = len(quiz_finale["quiz"]) + 1
            domanda["id"] = nuovo_id
            domanda["categoria"] = "Informatica"

            if not domanda.get("sotto_argomento"):
                domanda["sotto_argomento"] = trova_sotto_argomento_informatica(domanda)

            domanda_sicura, motivo_scarto = domanda_informatica_finale_sicura(domanda)

            if not domanda_sicura:
                report_generazione.append({
                    "tentativo": tentativi_totali,
                    "stato": "scartato",
                    "motivo": motivo_scarto,
                })
                continue

            sotto_argomenti_gia_usati = [
                domanda_gia_accettata.get("sotto_argomento")
                for domanda_gia_accettata in quiz_finale["quiz"]
            ]

            if domanda.get("sotto_argomento") in sotto_argomenti_gia_usati:
                report_generazione.append({
                    "tentativo": tentativi_totali,
                    "stato": "scartato",
                    "motivo": "sotto_argomento già usato nel JSON finale",
                })
                continue

            quiz_finale["quiz"].append(domanda)

            print(
                f"Informatica finale: accettata domanda {nuovo_id}/{richiesta.numero_domande}",
                flush=True,
            )

            report_generazione.append({
                "tentativo": tentativi_totali,
                "stato": "accettato",
                "numero_domanda_finale": nuovo_id,
                "sotto_argomento": domanda.get("sotto_argomento"),
                "id_quiz_singolo_salvato": risultato_singolo.get("id_quiz_salvato"),
                "tentativo_usato": risultato_singolo.get("tentativo_usato"),
            })

        except Exception as errore:
            report_generazione.append({
                "tentativo": tentativi_totali,
                "stato": "errore",
                "motivo": str(errore),
            })
            continue

    if len(quiz_finale["quiz"]) < richiesta.numero_domande:
        raise HTTPException(
            status_code=422,
            detail={
                "messaggio": (
                    "Non sono riuscito a generare tutte le domande richieste "
                    "con qualità sufficiente."
                ),
                "domande_generate": len(quiz_finale["quiz"]),
                "domande_richieste": richiesta.numero_domande,
                "report": report_generazione,
            },
        )

    quiz_finale = prepara_quiz_informatica_android_ready(
        quiz_finale=quiz_finale,
        richiesta=richiesta,
    )

    id_quiz_finale_salvato = salva_quiz_generato(
        categoria="Informatica",
        livello=richiesta.livello,
        numero_domande=richiesta.numero_domande,
        quiz_json=quiz_finale,
    )

    return {
        "messaggio": "JSON finale Informatica generato correttamente.",
        "modello": MODELLO_OLLAMA,
        "categoria": "Informatica",
        "livello": richiesta.livello,
        "numero_domande_generate": len(quiz_finale["quiz"]),
        "id_quiz_finale_salvato": id_quiz_finale_salvato,
        "download_latest_url": "/download-latest-quiz-json",
        "download_latest_full_url": "http://127.0.0.1:8000/download-latest-quiz-json",
        "report_generazione": report_generazione,
        "risultato": quiz_finale,
    }
