from __future__ import annotations

def get_profile() -> dict:
    return {
        "profile_id": "business_document_v394u",
        "domain_name": "documento aziendale",
        "detection_terms": ["azienda", "procedura", "cliente", "processo", "reparto", "budget", "obiettivo", "responsabile", "scadenza", "report"],
        "core_concepts": ["processo aziendale", "obiettivi", "responsabilità", "scadenze", "risultati"],
        "main_concepts": ["obiettivi aziendali", "processi", "responsabilità", "risorse", "scadenze"],
        "memory_concepts": ["responsabilità", "priorità", "scadenze", "procedure", "risultati attesi"],
        "risk_concepts": ["ritardi", "errori operativi", "mancanza di responsabilità", "costi non controllati", "comunicazione insufficiente"],
        "procedure_concepts": ["assegnare responsabilità", "definire scadenze", "monitorare attività", "verificare risultati"],
    }
