from __future__ import annotations

def get_profile() -> dict:
    return {
        "profile_id": "science_document_v394u",
        "domain_name": "documento scientifico",
        "detection_terms": ["esperimento", "ipotesi", "metodo", "risultati", "dati", "osservazione", "misura", "campione", "variabile", "conclusione"],
        "core_concepts": ["ipotesi", "metodo", "dati", "risultati", "conclusione"],
        "main_concepts": ["ipotesi", "metodo sperimentale", "dati raccolti", "risultati", "conclusioni"],
        "memory_concepts": ["ipotesi", "variabili", "campione", "metodo", "risultati"],
        "risk_concepts": ["errore di misura", "campione limitato", "dati incompleti", "interpretazione errata", "variabili non controllate"],
        "procedure_concepts": ["definire ipotesi", "raccogliere dati", "controllare variabili", "analizzare risultati"],
    }
