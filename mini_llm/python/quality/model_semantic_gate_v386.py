#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Semantic Gate V3.8.6 per mini LLM.

Corregge il problema emerso con V3.8:
- V3.8.1 passava frasi tecnicamente "pulite" ma semanticamente brutte;
- questo gate boccia frammenti, liste di parole, frasi senza verbo finito,
  subordinate isolate con "quando", avvii nominali sospetti e falsi verbi
  generati da suffissi troppo larghi come "umano" -> "ano".

Non abbassa il controllo precedente:
- continua a vietare fallback, hardcoded, demo, static, sentence_bank,
  memory_sentence, anchored_memory;
- continua a non vietare la parola generica "sentence" dentro generation_mode.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


GATE_NAME = "model_semantic_gate_v386"
OUT_DIR = Path("mini_llm/data/quality/model_semantic_gate_v386")
REPORT_PATH = Path("mini_llm/reports/model_semantic_gate_v386_report.md")

FORBIDDEN_GENERATION_MODES = {
    "fallback",
    "hardcoded",
    "demo",
    "static",
    "sentence_bank",
    "memory_sentence",
    "anchored_memory",
}

WEAK_FINAL_TOKENS = {
    "e", "o", "ma", "che", "quando", "mentre", "se",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "del", "dello", "della", "dei", "degli", "delle",
}

FUNCTION_WORDS = {
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "e", "o", "che", "quando", "se", "ma", "oltre", "alla", "al",
}

ARTICLES_OR_STARTERS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "l",
    "questo", "questa", "questi", "queste",
}

FINITE_VERBS = {
    "è", "sono", "era", "erano", "sarà", "saranno",
    "ha", "hanno", "aveva", "avevano",
    "può", "possono", "potrebbe", "potrebbero",
    "deve", "devono", "dovrebbe", "dovrebbero",
    "serve", "servono",
    "permette", "permettono",
    "aiuta", "aiutano",
    "protegge", "proteggono",
    "conserva", "conservano",
    "gestisce", "gestiscono",
    "descrive", "descrivono",
    "contiene", "contengono",
    "riduce", "riducono",
    "migliora", "migliorano",
    "aumenta", "aumentano",
    "recupera", "recuperano",
    "organizza", "organizzano",
    "rappresenta", "rappresentano",
    "indica", "indicano",
    "aggiunge", "aggiungono",
    "richiede", "richiedono",
    "usa", "usano",
    "utilizza", "utilizzano",
    "evita", "evitano",
    "blocca", "bloccano",
    "crea", "creano",
    "genera", "generano",
    "controlla", "controllano",
    "verifica", "verificano",
    "riconosce", "riconoscono",
    "segnala", "segnalano",
    "collega", "collegano",
    "trasforma", "trasformano",
    "ruba", "rubano",
    "cifra", "cifrano",
    "chiede", "chiedono",
    "viene", "vengono",
    "riceve", "ricevono",
    "invia", "inviano",
    "inoltra", "inoltrano",
    "prova", "provano",
    "rafforza",
    "rafforzano",
    "corregge",
    "correggono",
    "chiude",
    "chiudono",
}

INFINITIVE_SUFFIXES = ("are", "ere", "ire")
PARTICIPLE_SUFFIXES = (
    "ato", "ata", "ati", "ate",
    "uto", "uta", "uti", "ute",
    "ito", "ita", "iti", "ite",
)

BAD_PATTERNS = [
    r"\bun\s+in\s+una\b",
    r"\buno\s+in\s+una\b",
    r"\buna\s+in\s+una\b",
    r"\bil\s+in\b",
    r"\blo\s+in\b",
    r"\bla\s+in\b",
    r"\bl\s+in\b",
    r"\bl'\s+in\b",
    r"\bè\s+\w+\s+un\s+in\b",
    r"\bè\s+\w+\s+l\s+in\b",
    r"\bcon\s+\w+\s+deve\s+quando\b",
    r"\bdeve\s+quando\s+\w+\b",
    r"\bquando\s+descrive\s+\w+\b",
    r"\babbreviat[ao]\s+in\s+fa\b",
]

SUSPICIOUS_START_TOKENS = {
    "inattesi",
    "temporanei",
    "gestire",
    "salvare",
    "errore",
    "password",
}

BAD_GENERIC_TOKENS = {
    "voce", "cosa", "roba", "elemento",
}

STOPWORDS_FOR_CONTENT = FUNCTION_WORDS | {
    "questo", "questa", "questi", "queste",
    "come", "anche", "più", "meno", "molto", "ogni",
    "dopo", "prima", "caso", "modo",
}


@dataclass
class Issue:
    severity: str
    code: str
    message: str


@dataclass
class Result:
    index: int
    source_file: str
    prompt: str
    output: str
    generation_mode: str
    passed: bool
    issues: List[Issue]


def normalize_text(text: str) -> str:
    text = str(text or "")
    text = text.replace("’", "'").replace("`", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s])", r"\1 \2", text)
    return text


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zàèéìòóù']+", normalize_text(text).lower(), flags=re.IGNORECASE)


def content_tokens(text: str) -> List[str]:
    out = []
    for token in tokenize(text):
        if len(token) <= 2:
            continue
        if token in STOPWORDS_FOR_CONTENT:
            continue
        out.append(token)
    return out


def walk_dicts(data: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(data, dict):
        yield data
        for value in data.values():
            yield from walk_dicts(value)
    elif isinstance(data, list):
        for item in data:
            yield from walk_dicts(item)


def extract_first_string(obj: Dict[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def extract_prompt(obj: Dict[str, Any]) -> str:
    return extract_first_string(obj, ["prompt", "input", "query", "question", "topic", "term", "keyword"])


def extract_output(obj: Dict[str, Any]) -> str:
    return extract_first_string(obj, ["output", "generated_text", "text", "answer", "response", "completion", "sentence", "result"])


def extract_generation_mode(obj: Dict[str, Any]) -> str:
    return extract_first_string(obj, ["generation_mode", "mode", "decoder_mode", "inference_mode", "source_mode"])


def forbidden_mode_reason(mode: str) -> Optional[str]:
    raw = normalize_text(mode).lower()
    for forbidden in FORBIDDEN_GENERATION_MODES:
        if forbidden in raw:
            return forbidden
    return None


def has_finite_verb(tokens: Sequence[str]) -> bool:
    for token in tokens:
        if token in FINITE_VERBS:
            return True

    # Suffix molto selettivi: niente controllo generico su "ano"/"ono",
    # perché "umano" veniva interpretato male.
    for token in tokens:
        if len(token) >= 6 and token.endswith(("iamo", "isce", "iscono")):
            return True

    return False


def first_finite_verb_index(tokens: Sequence[str]) -> Optional[int]:
    for i, token in enumerate(tokens):
        if token in FINITE_VERBS:
            return i
        if len(token) >= 6 and token.endswith(("iamo", "isce", "iscono")):
            return i
    return None


def has_function_word_chain(tokens: Sequence[str], limit: int = 3) -> bool:
    run = 0
    for token in tokens:
        if token in FUNCTION_WORDS:
            run += 1
            if run >= limit:
                return True
        else:
            run = 0
    return False


def has_immediate_repetition(tokens: Sequence[str]) -> bool:
    for a, b in zip(tokens, tokens[1:]):
        if a == b and len(a) > 2:
            return True
    return False


def max_consecutive_content_before_first_verb(tokens: Sequence[str]) -> int:
    first_verb = first_finite_verb_index(tokens)
    scan = tokens if first_verb is None else tokens[:first_verb]

    max_run = 0
    run = 0
    for token in scan:
        if token not in STOPWORDS_FOR_CONTENT and token not in FINITE_VERBS:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    return max_run


def bad_pattern(text: str) -> Optional[str]:
    low = normalize_text(text).lower()
    for pattern in BAD_PATTERNS:
        if re.search(pattern, low):
            return pattern
    return None



def add_v383_semantic_rules(prompt: str, output: str, obj: Dict[str, Any], issues: List[Issue]) -> None:
    """
    Regole V3.8.3:
    - blocca accordi grammaticali falsi;
    - blocca copula + infinito, es. "sono usare";
    - blocca definizioni semantiche del tema sbagliato;
    - blocca ruoli invertiti, es. ransomware che "serve a recuperare".
    """
    p = normalize_text(prompt).lower()
    low = normalize_text(output).lower()
    source = normalize_text(str(obj.get("source_sentence", ""))).lower()

    # Errore grammaticale: "sono usare", "è usare", ecc.
    if re.search(r"\b(è|sono)\s+(usare|gestire|salvare|recuperare|proteggere|controllare|fornire|convincere|cifrare|rubare|ingannare)\b", low):
        issues.append(Issue(
            "blocker",
            "copula_plus_infinitive",
            "Copula seguita da infinito: struttura grammaticale innaturale, es. 'sono usare'."
        ))

    # Errore di accordo: plurale + participio/aggettivo singolare maschile.
    if re.search(r"\bsono\s+(sempre\s+)?(collegato|usato|generato|protetto|rubato|violato|cifrato)\b", low):
        issues.append(Issue(
            "blocker",
            "plural_singular_agreement_error",
            "Accordo sospetto: soggetto plurale con forma singolare, es. 'sono collegato'."
        ))

    # Backup: residuo di frase condizionale trasformato male.
    if p == "backup regolari":
        if "sono sempre collegato" in low:
            issues.append(Issue(
                "blocker",
                "backup_agreement_error",
                "I backup regolari non possono essere descritti con 'sono sempre collegato'."
            ))
        if "un ransomware potrebbe cifrare anche" in low and low.startswith("i backup regolari sono"):
            issues.append(Issue(
                "blocker",
                "malformed_conditional_residue",
                "Residuo di frase condizionale ricostruito male come definizione dei backup."
            ))

    # Dati sensibili: non sono una tecnica di inganno, quello è phishing.
    if p == "dati sensibili":
        if re.search(r"\bi dati sensibili\s+sono\s+una\s+tecnica\b", low):
            issues.append(Issue(
                "blocker",
                "semantic_domain_mismatch",
                "I dati sensibili non sono una tecnica; questa è una definizione del phishing."
            ))
        if "ingannare le persone" in low or "convincerle a fornire" in low:
            issues.append(Issue(
                "blocker",
                "phishing_definition_leaked",
                "L'output sui dati sensibili contiene una definizione tipica del phishing."
            ))
        if source.startswith("il phishing"):
            issues.append(Issue(
                "blocker",
                "source_prompt_drift",
                "La frase sorgente appartiene al phishing, non ai dati sensibili."
            ))

    # Ransomware: un attacco non serve a recuperare; il backup serve a recuperare.
    if p == "attacco ransomware":
        if re.search(r"\battacco ransomware\s+serve\s+a\s+recuperare\b", low):
            issues.append(Issue(
                "blocker",
                "inverse_semantic_role",
                "Ruolo semantico invertito: il backup recupera, il ransomware attacca/cifra."
            ))
        if "errore umano guasto furto cancellazione accidentale" in low:
            issues.append(Issue(
                "blocker",
                "backup_definition_leaked",
                "L'output sul ransomware contiene una definizione/residuo relativo al backup."
            ))
        if source.startswith("serve a recuperare"):
            issues.append(Issue(
                "blocker",
                "source_prompt_drift",
                "La frase sorgente parla di recupero/backup, non di attacco ransomware."
            ))

    # Password sicure: "sono usare" è già bloccato, ma aggiungiamo controllo specifico.
    if p == "password sicure":
        if "password sicure sono usare" in low:
            issues.append(Issue(
                "blocker",
                "password_definition_malformed",
                "Definizione malformata: dovrebbe spiegare che le password sicure richiedono/beneficiano di un password manager."
            ))

    # Evita definizioni costruite con sorgenti troppo lontane dal prompt.
    if source:
        if p == "password" and source.startswith("la 2fa"):
            issues.append(Issue(
                "warning",
                "weak_source_alignment",
                "La sorgente parla di 2FA: frase accettabile solo se l'output resta semanticamente sensato."
            ))


def add_v384_human_quality_rules(prompt: str, output: str, obj: Dict[str, Any], issues: List[Issue]) -> None:
    """
    Regole V3.8.4:
    - blocca soggetto sbagliato preso da frase sorgente diversa;
    - blocca frasi in cui "password" prende il ruolo del "password manager";
    - blocca frasi da report/sezioni operative tipo "sezione 001.1 descrive";
    - blocca verbi accostati senza congiunzione, es. "blocca cifra";
    - blocca liste lunghe senza separatori leggibili.
    """
    p = normalize_text(prompt).lower()
    low = normalize_text(output).lower()
    source = normalize_text(str(obj.get("source_sentence", ""))).lower()

    # V3.10: il soggetto "password" eredita erroneamente il ruolo del password manager.
    if p in {"password", "password sicure"}:
        if re.search(r"\b(password|password sicure)\s+permett\w*\s+di\s+salvare\s+password\b", low):
            issues.append(Issue(
                "blocker",
                "wrong_subject_from_password_manager",
                "Il ruolo del password manager è stato assegnato alla password/password sicure."
            ))

        if source.startswith("un password manager") and "permette di salvare password" in source:
            issues.append(Issue(
                "blocker",
                "source_subject_drift_password_manager",
                "La sorgente parla di password manager: non va trasformata sostituendo solo il soggetto."
            ))

    # V3.10: frase tecnica/artificiale da sezione operativa, non spiegazione naturale.
    if p == "sicurezza informatica":
        if "descrive come gestire sicurezza informatica" in low:
            issues.append(Issue(
                "blocker",
                "self_referential_management_phrase",
                "Frase autoreferenziale/brutta: 'descrive come gestire sicurezza informatica'."
            ))

        if "sezione 001" in source or "it operations" in source:
            issues.append(Issue(
                "blocker",
                "operational_section_source_leak",
                "La sorgente è una sezione operativa numerata, non una frase naturale adatta al mini LLM."
            ))

        if re.search(r"\bsicurezza informatica\s+descrive\b", low):
            issues.append(Issue(
                "blocker",
                "wrong_predicate_for_concept",
                "Il concetto 'sicurezza informatica' non dovrebbe essere il soggetto di 'descrive' in questa forma."
            ))

    # V3.10: "blocca cifra" perde la congiunzione "o".
    if p == "attacco ransomware":
        if re.search(r"\bblocca\s+cifra\b", low):
            issues.append(Issue(
                "blocker",
                "missing_conjunction_between_verbs",
                "Due verbi accostati senza congiunzione: dovrebbe essere 'blocca o cifra'."
            ))

        if "blocca cifra i dati" in low:
            issues.append(Issue(
                "blocker",
                "malformed_ransomware_action",
                "Azione ransomware grammaticalmente malformata: 'blocca cifra i dati'."
            ))

    # V3.10: dati sensibili semanticamente ok, ma troppo lista senza virgole/separatori.
    if p == "dati sensibili":
        if "dati personali informazioni economiche documenti aziendali contratti credenziali" in low:
            issues.append(Issue(
                "blocker",
                "missing_list_separators",
                "Lista lunga senza separatori leggibili tra i concetti."
            ))

    # Regola generale: due verbi finiti operativi consecutivi senza congiunzione.
    if re.search(r"\b(blocca|cifra|ruba|chiede|protegge|salva|gestisce)\s+(blocca|cifra|ruba|chiede|protegge|salva|gestisce)\b", low):
        issues.append(Issue(
            "blocker",
            "adjacent_action_verbs",
            "Verbi d'azione consecutivi senza connettivo."
        ))

    # Regola generale: evitare frasi costruite da sorgenti numerate tipo report/test.
    if re.search(r"\bsezione\s+\d+", source):
        issues.append(Issue(
            "blocker",
            "numbered_section_source",
            "Sorgente da sezione numerata: probabile materiale tecnico non adatto a frase naturale."
        ))


def add_v385_dynamic_decoder_rules(prompt: str, output: str, obj: Dict[str, Any], issues: List[Issue]) -> None:
    """
    Regole V3.8.5:
    - blocca errori introdotti dal dynamic decoder V3.12;
    - blocca perdita della negazione;
    - blocca articoli/accordi sbagliati;
    - blocca definizioni trasferite dal dominio sbagliato;
    - blocca frasi formalmente grammaticali ma semanticamente false.
    """
    p = normalize_text(prompt).lower()
    low = normalize_text(output).lower()
    source = normalize_text(str(obj.get("source_sentence", ""))).lower()

    def block(code: str, message: str) -> None:
        issues.append(Issue("blocker", code, message))

    # Sorgenti sporche da risposte/test: non devono diventare corpus generativo.
    if source.startswith("risposta corretta:"):
        block(
            "answer_metadata_source_leak",
            "La sorgente contiene metadati di risposta corretta: non è una frase naturale da usare per generare."
        )

    # Articoli e accordi evidenti.
    article_patterns = [
        (r"\bil password sicure\b", "wrong_article_password_sicure"),
        (r"\bil backup regolari\b", "wrong_article_backup_regolari"),
        (r"\bla autenticazione\b", "wrong_article_autenticazione"),
        (r"\bil accesso\b", "wrong_article_accesso"),
        (r"\bi aggiornamenti software\b", "wrong_article_aggiornamenti"),
        (r"\bl'account amministrativi\b", "wrong_article_account_amministrativi"),
        (r"\bil furto credenziali\b", "wrong_article_furto_credenziali"),
        (r"\bil ripristino dati sono\b", "wrong_agreement_ripristino_dati"),
    ]

    for pattern, code in article_patterns:
        if re.search(pattern, low):
            block(code, "Articolo o accordo grammaticale sbagliato nel soggetto.")

    if re.search(r"\bpossono essere usato\b", low):
        block("plural_passive_agreement_error", "Accordo errato: 'possono essere usato'.")

    if re.search(r"\bdevono\b.+\bnon deve\b", low):
        block("mixed_plural_singular_modal", "Accordo modale incoerente: 'devono ... non deve'.")

    # Perdita della negazione: cambia il senso della frase.
    if "non devono essere scritte" in source and "devono essere scritte" in low and "non devono essere scritte" not in low:
        block(
            "lost_negation_password_written",
            "La frase sorgente vieta di scrivere le password, ma l'output ha perso la negazione."
        )

    if "non devono essere inviate" in source and "devono essere inviate" in low and "non devono essere inviate" not in low:
        block(
            "lost_negation_sensitive_info",
            "La frase sorgente vieta l'invio, ma l'output ha perso la negazione."
        )

    # 2FA corrotta in 'fa'.
    if re.search(r"\bla fa\b|\bin fa\b|\bdi fa\b", low):
        block("two_factor_abbreviation_corrupted", "La sigla 2FA è stata corrotta in 'fa'.")

    # Definizioni di dominio sbagliato.
    if p == "sicurezza informatica" and "copia di sicurezza dei dati" in low:
        block(
            "backup_definition_leaked_into_security",
            "La sicurezza informatica è stata definita come backup."
        )

    if p == "password sicure" and "devono essere scritte su fogli" in low:
        block(
            "opposite_security_meaning",
            "L'output dice una pratica insicura come se fosse corretta."
        )

    if p == "backup regolari" and "sempre collegato allo stesso computer" in low:
        block(
            "unsafe_backup_meaning",
            "L'output descrive una condizione rischiosa come se fosse definizione dei backup regolari."
        )

    if p == "backup offline" and "sempre collegato allo stesso computer" in low:
        block(
            "offline_backup_contradiction",
            "Un backup offline non può essere definito come sempre collegato."
        )

    if p in {"ransomware", "attacco ransomware"} and "serve a recuperare" in low:
        block(
            "ransomware_backup_role_inversion",
            "Ruolo invertito: il backup recupera, il ransomware attacca/cifra."
        )

    if p == "credenziali rubate" and "sono una tecnica usata per ingannare" in low:
        block(
            "credentials_defined_as_phishing",
            "Le credenziali rubate non sono una tecnica di inganno: è una definizione del phishing."
        )

    if p == "aggiornamenti software" and "sono un software dannoso" in low:
        block(
            "updates_defined_as_malware",
            "Gli aggiornamenti software sono stati definiti come malware."
        )

    if p == "informazioni riservate" and "sono un software dannoso" in low:
        block(
            "confidential_info_defined_as_malware",
            "Le informazioni riservate sono state definite come malware."
        )

    if p == "rischio informatico" and re.search(r"\brischio informatico riduce il rischio\b", low):
        block(
            "risk_reduces_risk_nonsense",
            "Il rischio informatico non riduce il rischio: frase semanticamente invertita."
        )

    if p == "accesso non autorizzato" and "deve proteggere le credenziali" in low:
        block(
            "unauthorized_access_as_actor",
            "L'accesso non autorizzato non è un soggetto che protegge credenziali."
        )

    if p == "codici temporanei" and "devono proteggere le credenziali" in low:
        block(
            "temporary_codes_wrong_actor",
            "I codici temporanei non sono il soggetto che protegge le credenziali personali."
        )

    if p == "account amministrativi" and "insieme di pratiche" in low:
        block(
            "admin_accounts_defined_as_security",
            "Gli account amministrativi sono stati definiti come sicurezza informatica."
        )

    if p == "protezione endpoint" and "serve una protezione aggiuntiva" in low:
        block(
            "endpoint_phrase_fragment",
            "Frase ricostruita male: 'serve una protezione aggiuntiva' senza struttura naturale."
        )

    if p == "furto credenziali" and "possono includere dati personali" in low:
        block(
            "credential_theft_defined_as_sensitive_data_list",
            "Il furto di credenziali è stato definito come una lista di dati sensibili."
        )

    if p == "documenti aziendali" and "possono essere usato" in low:
        block(
            "business_documents_agreement_error",
            "Accordo errato su 'documenti aziendali'."
        )

    # Frasi nominali tronche o senza soggetto corretto.
    if p == "dati sensibili" and low.startswith("sistemi di pagamento"):
        block(
            "missing_main_subject_for_sensitive_data",
            "L'output non definisce i dati sensibili: parte da un frammento di frase."
        )

    # Trasferimento diretto da malware verso concetti non-malware.
    if source.startswith("il malware è un software dannoso") and p not in {"malware", "ransomware"}:
        block(
            "malware_source_domain_drift",
            "Una definizione di malware è stata trasferita a un concetto diverso."
        )

    # Trasferimento diretto da phishing verso concetti che non sono phishing/social engineering.
    if source.startswith("il phishing è una tecnica") and p not in {"phishing", "social engineering"}:
        block(
            "phishing_source_domain_drift",
            "Una definizione di phishing è stata trasferita a un concetto diverso."
        )

    # Trasferimento da backup verso ransomware o sicurezza.
    if source.startswith("il backup serve a recuperare") and p in {"ransomware", "attacco ransomware", "sicurezza informatica"}:
        block(
            "backup_source_domain_drift",
            "Una frase di backup è stata trasferita a un concetto incompatibile."
        )


def add_v386_safe_decoder_rules(prompt: str, output: str, obj: Dict[str, Any], issues: List[Issue]) -> None:
    """
    Regole V3.8.6:
    - blocca copie identiche dal corpus;
    - blocca frammenti interrogativi;
    - blocca frasi che iniziano senza il soggetto del prompt;
    - blocca frasi tronche su preposizione/articolo;
    - blocca output che sono formalmente frasi ma non rispondono al prompt.
    """
    p = normalize_text(prompt).lower()
    low = normalize_text(output).lower()
    source = normalize_text(str(obj.get("source_sentence", ""))).lower()
    notes = obj.get("notes") or []

    if not isinstance(notes, list):
        notes = [str(notes)]

    def block(code: str, message: str) -> None:
        issues.append(Issue("blocker", code, message))

    # Copia identica: V3.13 usa spesso la sorgente tale e quale.
    if source and low and low == source:
        block(
            "exact_source_copy",
            "L'output è identico alla frase sorgente: non è una generazione/riscrittura controllata."
        )

    if "copied_from_corpus" in notes or obj.get("copied_from_corpus") is True:
        block(
            "declared_copied_from_corpus",
            "L'output è marcato come copiato dal corpus."
        )

    # Frammenti interrogativi o punteggiatura corrotta.
    if "?." in low or ".?" in low:
        block(
            "corrupted_question_punctuation",
            "Punteggiatura corrotta: combinazione di punto interrogativo e punto."
        )

    if source.endswith("?") or low.endswith("?"):
        block(
            "question_source_fragment",
            "La sorgente/output è una domanda o frammento interrogativo, non una frase dichiarativa naturale."
        )

    if low.startswith("serve una protezione aggiuntiva"):
        block(
            "missing_prompt_subject_fragment",
            "L'output parte da un frammento senza soggetto del prompt."
        )

    # Frasi tronche: esempio V3.13 'bloccare l'accesso ai.'
    if re.search(r"\b(ai|al|alla|alle|agli|dei|degli|delle|del|dello|della|di|a|da|con|per|su)\.$", low):
        block(
            "truncated_final_preposition",
            "La frase finisce con una preposizione/articolo articolato: output tronco."
        )

    if "l'accesso ai." in low:
        block(
            "truncated_access_phrase",
            "Frase tronca: 'l'accesso ai.' non chiude il complemento."
        )

    # Frasi senza soggetto reale del prompt.
    if low.startswith("possono includere"):
        block(
            "missing_declared_subject",
            "L'output inizia con 'Possono includere' senza dichiarare il soggetto."
        )

    if p in {"dati personali", "documenti aziendali", "informazioni riservate"} and low.startswith("possono includere"):
        block(
            "missing_prompt_subject_for_list",
            "La lista non è agganciata al soggetto del prompt."
        )

    # Output che contiene una parola del prompt ma non lo spiega.
    if p == "account amministrativi" and low.startswith("una buona regola aziendale"):
        block(
            "admin_accounts_not_defined",
            "L'output cita account amministrativi in una regola, ma non spiega cosa sono o perché sono rilevanti."
        )

    if p == "password" and "permessi limitati" in low:
        block(
            "password_fragment_from_permission_domain",
            "L'output per password proviene dal dominio permessi/protezione aggiuntiva e non spiega la password."
        )

    if p == "malware" and "software dannoso" in low and low.endswith("ai."):
        block(
            "malware_truncated_definition",
            "La definizione di malware è tronca."
        )

    # Blocca output con score negativo se il campo esiste: spesso sono copie o frasi deboli.
    try:
        score = float(obj.get("score", 0))
    except Exception:
        score = 0.0

    if score < 0:
        block(
            "negative_generation_score",
            "L'output ha score negativo: non deve essere considerato OK."
        )

    # Se il prompt è composto e l'output non contiene abbastanza ancore del prompt, è debole.
    prompt_tokens = [t for t in re.findall(r"[a-zàèéìòóù']+", p) if len(t) > 2]
    output_tokens = set(re.findall(r"[a-zàèéìòóù']+", low))

    if len(prompt_tokens) >= 2:
        hits = sum(1 for t in prompt_tokens if t in output_tokens)
        if hits == 0:
            block(
                "missing_prompt_terms",
                "L'output non contiene termini significativi del prompt composto."
            )

def evaluate_record(index: int, path: Path, obj: Dict[str, Any]) -> Result:
    prompt = extract_prompt(obj)
    output = normalize_text(extract_output(obj))
    mode = extract_generation_mode(obj)

    tokens = tokenize(output)
    issues: List[Issue] = []

    forbidden = forbidden_mode_reason(mode)
    if forbidden:
        issues.append(Issue("blocker", "forbidden_generation_mode", f"generation_mode proibita: {forbidden}"))

    if not output:
        issues.append(Issue("blocker", "empty_output", "Output vuoto."))

    if len(tokens) < 8:
        issues.append(Issue("blocker", "too_short", "Output troppo corto per essere una frase naturale utile."))

    if len(tokens) > 26:
        issues.append(Issue("blocker", "too_long", "Output troppo lungo e probabilmente incollato/derivato male."))

    if tokens and tokens[-1] in WEAK_FINAL_TOKENS:
        issues.append(Issue("blocker", "weak_final_token", f"Finale debole/non conclusivo: {tokens[-1]}"))

    pattern = bad_pattern(output)
    if pattern:
        issues.append(Issue("blocker", "nonsense_pattern", f"Pattern grammaticale assurdo rilevato: {pattern}"))

    if any(token in BAD_GENERIC_TOKENS for token in tokens):
        hits = sorted(set(t for t in tokens if t in BAD_GENERIC_TOKENS))
        issues.append(Issue("blocker", "generic_bad_token", f"Token generici sospetti: {', '.join(hits)}"))

    if has_function_word_chain(tokens):
        issues.append(Issue("blocker", "function_word_chain", "Troppi articoli/preposizioni/connettivi consecutivi."))

    if has_immediate_repetition(tokens):
        issues.append(Issue("blocker", "immediate_repetition", "Ripetizione immediata sospetta."))

    finite_index = first_finite_verb_index(tokens)
    if finite_index is None:
        issues.append(Issue("blocker", "missing_finite_verb", "Manca un verbo finito reale; infinitivi/participi non bastano."))

    if tokens:
        first = tokens[0]
        if first.endswith(INFINITIVE_SUFFIXES) and finite_index is None:
            issues.append(Issue("blocker", "infinitive_fragment", "La frase parte con un infinito e resta un frammento."))

        if first in SUSPICIOUS_START_TOKENS and finite_index is None:
            issues.append(Issue("blocker", "suspicious_nominal_start", f"Avvio nominale/frammentario sospetto: {first}"))

    if "quando" in tokens:
        idx = tokens.index("quando")
        before = tokens[:idx]
        if not has_finite_verb(before):
            issues.append(Issue("blocker", "orphan_when_clause", "La frase usa 'quando' senza una proposizione principale completa prima."))

    if finite_index is not None and finite_index > 8:
        issues.append(Issue("blocker", "late_main_verb", "Il primo verbo finito arriva troppo tardi: probabile lista di parole prima della frase."))

    content_run = max_consecutive_content_before_first_verb(tokens)
    if content_run >= 5:
        issues.append(Issue("blocker", "noun_salad_before_verb", "Troppi termini pieni consecutivi prima di un verbo: probabile insalata di parole."))

    prompt_content = set(content_tokens(prompt))
    output_content = set(content_tokens(output))
    if prompt_content and not (prompt_content & output_content):
        issues.append(Issue("blocker", "missing_prompt_anchor", "L'output non mantiene un ancoraggio chiaro al prompt."))

    # Controllo specifico per frasi tipo:
    # "Password dati sicurezza account backup usare..."
    if len(content_tokens(output)) >= 8 and finite_index is None:
        issues.append(Issue("blocker", "keyword_list_without_sentence", "Molti concetti in fila senza struttura di frase."))

    add_v383_semantic_rules(prompt, output, obj, issues)
    add_v384_human_quality_rules(prompt, output, obj, issues)
    add_v385_dynamic_decoder_rules(prompt, output, obj, issues)
    add_v386_safe_decoder_rules(prompt, output, obj, issues)

    passed = not any(issue.severity == "blocker" for issue in issues)

    return Result(
        index=index,
        source_file=str(path),
        prompt=prompt,
        output=output,
        generation_mode=mode,
        passed=passed,
        issues=issues,
    )


def load_records(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records: List[Dict[str, Any]] = []

    for obj in walk_dicts(data):
        if extract_output(obj):
            records.append(obj)

    seen = set()
    unique = []
    for obj in records:
        key = (extract_prompt(obj), extract_output(obj), extract_generation_mode(obj))
        if key not in seen:
            seen.add(key)
            unique.append(obj)

    return unique


def evaluate_files(paths: List[Path]) -> Tuple[List[Result], Dict[str, Any]]:
    results: List[Result] = []
    index = 0

    for path in paths:
        if not path.exists():
            results.append(Result(
                index=index,
                source_file=str(path),
                prompt="",
                output="",
                generation_mode="",
                passed=False,
                issues=[Issue("blocker", "file_not_found", "File non trovato.")],
            ))
            index += 1
            continue

        try:
            records = load_records(path)
        except Exception as exc:
            results.append(Result(
                index=index,
                source_file=str(path),
                prompt="",
                output="",
                generation_mode="",
                passed=False,
                issues=[Issue("blocker", "read_error", f"Errore lettura/parsing: {exc}")],
            ))
            index += 1
            continue

        for obj in records:
            results.append(evaluate_record(index, path, obj))
            index += 1

    total = len(results)
    passed = sum(1 for item in results if item.passed)
    failed = total - passed

    summary = {
        "gate": GATE_NAME,
        "total_outputs_checked": total,
        "passed": passed,
        "failed": failed,
        "status": "PASS" if total > 0 and failed == 0 else "FAIL",
        "rule": "La V3.8.2 richiede frase completa, verbo finito reale, niente subordinate isolate e niente liste di parole.",
    }

    return results, summary


def write_outputs(results: List[Result], summary: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    serializable = []
    for item in results:
        row = asdict(item)
        row["issues"] = [asdict(issue) for issue in item.issues]
        serializable.append(row)

    (OUT_DIR / "model_semantic_gate_v386_results.json").write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (OUT_DIR / "model_semantic_gate_v386_manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("# Model Semantic Gate V3.8.6 Report")
    lines.append("")
    lines.append(f"- Status: **{summary['status']}**")
    lines.append(f"- Output controllati: **{summary['total_outputs_checked']}**")
    lines.append(f"- Passati: **{summary['passed']}**")
    lines.append(f"- Falliti: **{summary['failed']}**")
    lines.append("")
    lines.append("## Nuove regole V3.8.2")
    lines.append("")
    lines.append("- Richiede un verbo finito reale, non solo infinito o participio.")
    lines.append("- Rimuove il falso positivo dei suffissi generici tipo `ano`, quindi `umano` non vale come verbo.")
    lines.append("- Boccia frasi con `quando` senza proposizione principale prima.")
    lines.append("- Boccia liste di parole/keyword senza struttura.")
    lines.append("- Boccia primo verbo troppo lontano dall'inizio.")
    lines.append("- Boccia troppi concetti pieni consecutivi prima del verbo.")
    lines.append("- Boccia copula + infinito, es. `sono usare`.")
    lines.append("- Boccia accordi falsi, es. `sono collegato` con soggetto plurale.")
    lines.append("- Boccia definizioni del tema sbagliato, es. dati sensibili definiti come phishing.")
    lines.append("- Boccia ruoli semantici invertiti, es. ransomware che serve a recuperare.")
    lines.append("- Boccia soggetti sostituiti male da una sorgente di altro dominio, es. password che eredita il ruolo del password manager.")
    lines.append("- Boccia sorgenti da sezioni operative numerate, es. `sezione 001.1 descrive`.")
    lines.append("- Boccia verbi d'azione consecutivi senza connettivo, es. `blocca cifra`.")
    lines.append("- Boccia liste lunghe senza separatori leggibili.")
    lines.append("- Boccia perdita della negazione, es. `non devono` trasformato in `devono`.")
    lines.append("- Boccia articoli e accordi errati, es. `Il password sicure`, `Il backup regolari`.")
    lines.append("- Boccia definizioni trasferite dal dominio sbagliato, es. aggiornamenti definiti come malware.")
    lines.append("- Boccia ruoli semantici falsi, es. ransomware che recupera o rischio che riduce il rischio.")
    lines.append("- Boccia copie identiche dal corpus.")
    lines.append("- Boccia frammenti interrogativi e punteggiatura corrotta, es. `?.`.")
    lines.append("- Boccia frasi tronche che finiscono con preposizione/articolo.")
    lines.append("- Boccia output con score negativo marcati come OK.")
    lines.append("- Boccia frasi senza soggetto del prompt, es. `Possono includere...`.")
    lines.append("")
    lines.append("## Output falliti")
    lines.append("")

    failures = [item for item in results if not item.passed]
    if not failures:
        lines.append("Nessun output fallito.")
    else:
        for item in failures:
            lines.append(f"### Failure #{item.index}")
            lines.append("")
            lines.append(f"- File: `{item.source_file}`")
            if item.prompt:
                lines.append(f"- Prompt: `{item.prompt}`")
            if item.generation_mode:
                lines.append(f"- Generation mode: `{item.generation_mode}`")
            lines.append(f"- Output: `{item.output}`")
            lines.append("- Problemi:")
            for issue in item.issues:
                lines.append(f"  - `{issue.code}`: {issue.message}")
            lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def discover_default_files() -> List[Path]:
    candidates: List[Path] = []
    base = Path("mini_llm/data")
    if base.exists():
        candidates.extend(sorted(base.glob("inference_*/**/*outputs.json")))
        candidates.extend(sorted(base.glob("quality/model_quality_gate_v1/*results.json")))
        candidates.extend(sorted(base.glob("quality/model_quality_gate_v11/*results.json")))

    filtered = []
    for path in candidates:
        raw = str(path)
        if "model_semantic_gate_" in raw:
            continue
        filtered.append(path)

    return sorted(set(filtered), key=lambda p: str(p), reverse=True)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="File JSON da controllare.")
    args = parser.parse_args()

    paths = [Path(p) for p in args.paths] if args.paths else discover_default_files()

    results, summary = evaluate_files(paths)
    write_outputs(results, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
