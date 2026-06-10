# Importiamo sqlite3, il database leggero già incluso in Python.
import sqlite3


# Questo è il nome del file database che viene creato.
NOME_DATABASE = "alex_workspace.db"


# Questa funzione crea il database e le tabelle, se non esistono già.
def inizializza_database():
    connessione = sqlite3.connect(NOME_DATABASE)

    # Tabella per salvare le conversazioni della chat.
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_reply TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Tabella per salvare le memorie personali.
    connessione.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connessione.commit()
    connessione.close()


# Questa funzione salva una conversazione nel database.
def salva_conversazione(messaggio_utente, risposta_backend):
    connessione = sqlite3.connect(NOME_DATABASE)

    connessione.execute(
        """
        INSERT INTO conversations (user_message, ai_reply)
        VALUES (?, ?)
        """,
        (messaggio_utente, risposta_backend)
    )

    connessione.commit()
    connessione.close()


# Questa funzione recupera le ultime conversazioni salvate.
def recupera_conversazioni():
    connessione = sqlite3.connect(NOME_DATABASE)
    connessione.row_factory = sqlite3.Row

    risultati = connessione.execute(
        """
        SELECT id, user_message, ai_reply, created_at
        FROM conversations
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    connessione.close()

    conversazioni = []

    for riga in risultati:
        conversazioni.append(dict(riga))

    return conversazioni


# Questa funzione salva una memoria personale.
def salva_memoria(titolo, contenuto, categoria):
    connessione = sqlite3.connect(NOME_DATABASE)

    connessione.execute(
        """
        INSERT INTO memories (title, content, category)
        VALUES (?, ?, ?)
        """,
        (titolo, contenuto, categoria)
    )

    connessione.commit()
    connessione.close()


# Questa funzione recupera le ultime memorie salvate.
def recupera_memorie():
    connessione = sqlite3.connect(NOME_DATABASE)
    connessione.row_factory = sqlite3.Row

    risultati = connessione.execute(
        """
        SELECT id, title, content, category, created_at
        FROM memories
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    connessione.close()

    memorie = []

    for riga in risultati:
        memorie.append(dict(riga))

    return memorie