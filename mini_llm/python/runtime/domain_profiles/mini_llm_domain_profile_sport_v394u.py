from __future__ import annotations

def get_profile() -> dict:
    return {
        "profile_id": "sport_training_v394u",
        "domain_name": "sport e allenamento",
        "detection_terms": ["allenamento", "esercizi", "serie", "ripetizioni", "recupero", "forza", "resistenza", "mobilità", "infortunio", "carico"],
        "core_concepts": ["allenamento", "esercizi", "recupero", "carico", "progressione", "tecnica"],
        "main_concepts": ["obiettivo atletico", "esercizi principali", "serie", "ripetizioni", "recupero", "progressione del carico"],
        "memory_concepts": ["tecnica corretta", "riscaldamento", "recupero", "progressione", "ascolto del corpo"],
        "risk_concepts": ["sovraccarico", "infortunio", "tecnica scorretta", "recupero insufficiente", "carico eccessivo"],
        "procedure_concepts": ["riscaldamento", "serie", "ripetizioni", "recupero", "defaticamento"],
    }
