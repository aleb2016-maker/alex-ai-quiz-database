# motori_scrittura.py
# =============================================================================
# FASE 1 — MAP
# RAG GERARCHICO MAP-REDUCE AD ALBERO
#
# Obiettivo di questo modulo:
# - NON generare riassunti belli.
# - NON riscrivere in stile elegante.
# - NON applicare quality gate linguistici aggressivi.
# - Estrarre da ogni chunk solo:
#   fatti grezzi, micro-concetti, entità, relazioni e segnali di dominio.
#
# Questo file riguarda SOLO backend / orchestratore logico.
# Non contiene codice UI, CSS, pulsanti, layout o grafica.
# =============================================================================

from __future__ import annotations

import json
import re
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple


# =============================================================================
# 1. PROTOCOLLO GENERICO PER IL CLIENT LLM
# =============================================================================

class LLMClientProtocol(Protocol):
    """
    Protocollo astratto per qualunque client LLM.

    L'orchestratore non deve conoscere se sotto c'è:
    - API cloud
    - Ollama locale
    - modello locale custom
    - wrapper LangChain
    - altra libreria

    È sufficiente che il client esponga un metodo `generate`.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Deve restituire una stringa.

        Se il backend supporta JSON mode / structured outputs,
        può usare `response_format`.

        Se non lo supporta, ignora `response_format` e restituisce testo.
        """
        ...


# =============================================================================
# 2. STRUTTURE DATI UNIVERSALI DELLA FASE MAP
# =============================================================================

@dataclass
class RelationItem:
    """
    Relazione grezza estratta dal chunk.

    Esempio:
    subject='backup periodico'
    predicate='riduce'
    object='rischio di perdita dati'
    evidence='Il documento indica che backup regolari riducono...'
    """

    subject: str = ""
    predicate: str = ""
    object: str = ""
    evidence: str = ""


@dataclass
class MapChunkResult:
    """
    Risultato MAP di un singolo chunk.

    Questo oggetto NON rappresenta un riassunto.
    Rappresenta materiale grezzo strutturato da usare nella fase REDUCE.

    Campi obbligatori richiesti:
    - chunk_id
    - page_start
    - page_end
    - domain
    - facts[]
    - micro_concepts[]
    - entities[]
    - relations[]
    """

    chunk_id: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    domain: str = "unknown"

    facts: List[str] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    relations: List[RelationItem] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    extraction_score: float = 0.0
    raw_llm_output: Optional[str] = None

    source_char_count: int = 0
    processed: bool = False
    blocked: bool = False


@dataclass
class MapPhaseOutput:
    """
    Output complessivo della Fase 1 — MAP.

    Contiene tutti i risultati dei chunk e un piccolo report tecnico.
    Non genera ancora il macro-riassunto.
    Non fa REDUCE.
    Non applica il Super Quality Gate finale.
    """

    document_id: str
    total_chunks: int = 0
    processed_chunks: int = 0
    failed_chunks: int = 0
    blocked_chunks: int = 0

    results: List[MapChunkResult] = field(default_factory=list)
    global_warnings: List[str] = field(default_factory=list)
    global_errors: List[str] = field(default_factory=list)

    detected_domains: List[str] = field(default_factory=list)
    phase_name: str = "MAP"


@dataclass
class ChunkInput:
    """
    Input normalizzato per un singolo chunk.

    Il testo qui dovrebbe essere già stato:
    - estratto dal documento
    - pulito in modo leggero
    - diviso in chunk

    Questa classe non si occupa di PDF, OCR o UI.
    """

    chunk_id: str
    text: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 3. CONFIGURAZIONE UNIVERSALE DELLA FASE MAP
# =============================================================================

@dataclass
class MapPhaseConfig:
    """
    Configurazione parametrica.

    Nessun valore è legato a un documento specifico.
    Tutto può essere cambiato dall'orchestratore.
    """

    min_chunk_chars: int = 20
    max_facts: int = 40
    max_micro_concepts: int = 30
    max_entities: int = 30
    max_relations: int = 30

    temperature: float = 0.0
    max_tokens: Optional[int] = 2500

    domain_hint: Optional[str] = None

    demo_fallback_signatures: List[str] = field(default_factory=lambda: [
        "sicurezza informatica aziendale",
        "documento di esempio",
        "contenuto demo",
        "testo dimostrativo",
        "fallback",
        "questa è una demo",
        "esempio generico",
        "lorem ipsum",
        "knowledge_base_json",
    ])

    generic_bad_facts: List[str] = field(default_factory=lambda: [
        "il documento parla di vari aspetti importanti",
        "questo testo tratta diversi argomenti",
        "vengono affrontati temi rilevanti",
        "il contenuto è utile e interessante",
        "sono presenti informazioni significative",
    ])

    allowed_domains: List[str] = field(default_factory=lambda: [
        "business",
        "technical",
        "legal",
        "medical",
        "education",
        "sport",
        "curriculum",
        "personal_document",
        "story",
        "poetry",
        "hobby_project",
        "unknown",
    ])


# =============================================================================
# 4. PROMPT MAP
# =============================================================================

def build_map_system_prompt() -> str:
    """
    Prompt di sistema per la fase MAP.

    Il modello viene forzato a NON generare prosa elegante.
    Deve estrarre solo dati grezzi strutturati.
    """

    return """
Sei un motore di estrazione dati per una pipeline RAG gerarchica MAP-REDUCE.

Regole obbligatorie:
- NON scrivere un riassunto.
- NON rendere il testo elegante.
- NON creare frasi da libro, marketing o presentazione.
- NON aggiungere interpretazioni non presenti nel chunk.
- NON inventare fatti.
- NON correggere lo stile del documento.
- Estrai solo materiale grezzo verificabile dal chunk fornito.
- Mantieni concetti specifici, numeri, definizioni, entità, relazioni e procedure.
- Se un'informazione non è presente nel chunk, non inserirla.
- Se il chunk è povero, restituisci liste vuote o pochi elementi.
- L'output deve essere SOLO JSON valido.
""".strip()


def build_map_user_prompt(
    chunk_text: str,
    chunk_id: str,
    page_start: Optional[int],
    page_end: Optional[int],
    config: MapPhaseConfig,
) -> str:
    """
    Prompt utente per l'estrazione MAP.

    Il prompt richiede JSON strutturato e limita il numero massimo di elementi.
    """

    page_info = f"pagine {page_start}-{page_end}" if page_start or page_end else "pagine non specificate"
    domain_hint = config.domain_hint or "non specificato"

    return f"""
Analizza il seguente chunk in isolamento.

Chunk ID: {chunk_id}
Posizione: {page_info}
Dominio atteso, se utile: {domain_hint}

Devi estrarre SOLO dati grezzi.

Regole di copertura obbligatorie — MAP_COVERAGE_V1:
- Ogni obbligo espresso con parole come "deve", "devono", "è necessario", "è obbligatorio" deve diventare almeno un fact separato.
- Ogni divieto espresso con parole come "non deve", "non devono", "vietato", "evitare" deve diventare almeno un fact separato.
- Ogni rischio, riduzione del rischio, prevenzione, causa-effetto o conseguenza deve diventare almeno un fact separato e, se possibile, una relation.
- Ogni controllo, revisione, verifica, procedura, fase operativa o regola aziendale deve diventare almeno un fact separato.
- Non omettere l'ultimo periodo del chunk: spesso contiene conclusioni operative, rischi o condizioni importanti.
- Se una frase contiene due regole diverse, dividile in due facts distinti.
- I facts devono essere atomici: un solo fatto/regola per elemento.
- Le relations devono rappresentare legami reali presenti nel chunk: soggetto → azione/relazione → oggetto.
- Se nel chunk appare un rapporto tipo "X riduce Y", "X previene Y", "X causa Y", "X limita Y", crea una relation dedicata.
- Non comprimere più fatti in un'unica frase generale.

Restituisci JSON valido con questa struttura esatta:

{{
  "domain": "dominio base rilevato oppure unknown",
  "facts": [
    "fatto grezzo verificabile presente nel chunk"
  ],
  "micro_concepts": [
    "micro-concetto di 2-4 parole"
  ],
  "entities": [
    "entità, oggetto, persona, reparto, tecnologia, norma, concetto nominato"
  ],
  "relations": [
    {{
      "subject": "soggetto",
      "predicate": "relazione/azione",
      "object": "oggetto",
      "evidence": "breve prova testuale dal chunk"
    }}
  ]
}}

Limiti:
- massimo facts: {config.max_facts}
- massimo micro_concepts: {config.max_micro_concepts}
- massimo entities: {config.max_entities}
- massimo relations: {config.max_relations}

Divieti:
- vietato riassumere in forma discorsiva
- vietato scrivere introduzioni
- vietato scrivere conclusioni
- vietato usare frasi generiche
- vietato aggiungere contenuto non presente
- vietato trasformare il chunk in testo elegante
- vietato perdere obblighi, divieti, rischi, revisioni, controlli o causa-effetto presenti nel chunk
- vietato sostituire fatti specifici con frasi generiche tipo "il documento parla di"
- vietato fondere più regole operative in un solo fatto generico

Chunk:
\"\"\"
{chunk_text}
\"\"\"
""".strip()


def build_json_response_format() -> Dict[str, Any]:
    """
    Schema JSON astratto.

    Se il client LLM supporta JSON mode o structured outputs,
    questo dizionario può essere passato direttamente.

    Se il client non lo supporta, verrà ignorato dal wrapper.
    """

    return {
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "facts": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "micro_concepts": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "entities": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "relations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "subject": {"type": "string"},
                            "predicate": {"type": "string"},
                            "object": {"type": "string"},
                            "evidence": {"type": "string"},
                        },
                        "required": ["subject", "predicate", "object"],
                    },
                },
            },
            "required": [
                "domain",
                "facts",
                "micro_concepts",
                "entities",
                "relations",
            ],
        },
    }


# =============================================================================
# 5. UTILITY SICURE
# =============================================================================

def normalize_text(value: Any) -> str:
    """
    Normalizza in modo leggero una stringa.

    Non è un cleaner linguistico aggressivo.
    Serve solo a evitare valori None, spazi multipli e caratteri invisibili.
    """

    try:
        if value is None:
            return ""

        text = str(value)
        text = text.replace("\x00", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        return text.strip()

    except Exception:
        return ""


def safe_list_of_strings(value: Any, limit: int) -> List[str]:
    """
    Converte un valore generico in lista di stringhe pulite.

    Non interpreta semanticamente.
    Non abbellisce il testo.
    """

    cleaned: List[str] = []

    try:
        if value is None:
            return cleaned

        if isinstance(value, str):
            value = [value]

        if not isinstance(value, list):
            return cleaned

        for item in value:
            item_text = normalize_text(item)
            if item_text:
                cleaned.append(item_text)

            if len(cleaned) >= limit:
                break

        return cleaned

    except Exception:
        return cleaned


def safe_relations(value: Any, limit: int) -> List[RelationItem]:
    """
    Converte una lista generica in RelationItem.

    Accetta dizionari parziali.
    Se il modello restituisce dati sporchi, la funzione non rompe la pipeline.
    """

    relations: List[RelationItem] = []

    try:
        if not isinstance(value, list):
            return relations

        for item in value:
            if isinstance(item, dict):
                relation = RelationItem(
                    subject=normalize_text(item.get("subject", "")),
                    predicate=normalize_text(item.get("predicate", "")),
                    object=normalize_text(item.get("object", "")),
                    evidence=normalize_text(item.get("evidence", "")),
                )

                if relation.subject or relation.predicate or relation.object:
                    relations.append(relation)

            elif isinstance(item, str):
                relation = RelationItem(
                    subject="",
                    predicate="related_to",
                    object=normalize_text(item),
                    evidence="",
                )
                if relation.object:
                    relations.append(relation)

            if len(relations) >= limit:
                break

        return relations

    except Exception:
        return relations


def extract_json_object(raw_text: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Estrae un oggetto JSON da una risposta LLM.

    Gestisce:
    - JSON puro
    - JSON dentro ```json
    - testo con JSON incorporato

    Se il JSON è corrotto, non solleva eccezione.
    Restituisce warning.
    """

    warnings: List[str] = []

    try:
        text = normalize_text(raw_text)

        if not text:
            warnings.append("LLM_OUTPUT_EMPTY")
            return None, warnings

        # Caso 1: JSON puro.
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed, warnings
        except Exception:
            pass

        # Caso 2: blocco markdown ```json ... ```
        fenced_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced_match:
            try:
                parsed = json.loads(fenced_match.group(1))
                if isinstance(parsed, dict):
                    warnings.append("JSON_EXTRACTED_FROM_MARKDOWN_FENCE")
                    return parsed, warnings
            except Exception:
                warnings.append("JSON_MARKDOWN_FENCE_PARSE_FAILED")

        # Caso 3: primo oggetto JSON nel testo.
        first_brace = text.find("{")
        last_brace = text.rfind("}")

        if first_brace >= 0 and last_brace > first_brace:
            candidate = text[first_brace:last_brace + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    warnings.append("JSON_EXTRACTED_FROM_TEXT")
                    return parsed, warnings
            except Exception:
                warnings.append("JSON_INLINE_PARSE_FAILED")

        warnings.append("JSON_PARSE_FAILED")
        return None, warnings

    except Exception as exc:
        warnings.append(f"JSON_EXTRACTION_EXCEPTION: {type(exc).__name__}")
        return None, warnings


def contains_forbidden_signature(text: str, signatures: Sequence[str]) -> bool:
    """
    Controllo anti-fallback leggero.

    Non blocca per stile.
    Cerca solo firme demo/fallback esplicite.
    """

    try:
        normalized = normalize_text(text).lower()

        for signature in signatures:
            signature_norm = normalize_text(signature).lower()
            if signature_norm and signature_norm in normalized:
                return True

        return False

    except Exception:
        return False


def find_forbidden_signatures(texts: Iterable[str], signatures: Sequence[str]) -> List[str]:
    """
    Restituisce le firme demo/fallback trovate nei testi estratti.
    """

    found: List[str] = []

    try:
        joined = "\n".join(normalize_text(t).lower() for t in texts if t)

        for signature in signatures:
            signature_norm = normalize_text(signature).lower()
            if signature_norm and signature_norm in joined:
                found.append(signature)

        return found

    except Exception:
        return found


def detect_generic_bad_facts(facts: Sequence[str], generic_bad_facts: Sequence[str]) -> List[str]:
    """
    Rileva fatti troppo generici o preconfezionati.

    In MAP non cancelliamo automaticamente il chunk.
    Aggiungiamo warning, perché la fase MAP deve conservare materiale utile.
    """

    detected: List[str] = []

    try:
        normalized_facts = [normalize_text(f).lower() for f in facts]

        for bad in generic_bad_facts:
            bad_norm = normalize_text(bad).lower()
            if not bad_norm:
                continue

            for fact in normalized_facts:
                if bad_norm in fact:
                    detected.append(bad)
                    break

        return detected

    except Exception:
        return detected


def light_domain_detection(
    chunk_text: str,
    extracted_domain: str,
    allowed_domains: Sequence[str],
    domain_hint: Optional[str] = None,
) -> Tuple[str, List[str]]:
    """
    Controllo dominio base.

    Non deve essere un classificatore perfetto.
    Serve solo a evitare dominio vuoto, assurdo o incompatibile.

    Se il modello restituisce un dominio non consentito, lo degradiamo a 'unknown'
    e aggiungiamo warning.
    """

    warnings: List[str] = []

    try:
        domain = normalize_text(extracted_domain).lower().replace(" ", "_")

        if not domain:
            domain = "unknown"
            warnings.append("DOMAIN_EMPTY_SET_TO_UNKNOWN")

        allowed = {normalize_text(d).lower().replace(" ", "_") for d in allowed_domains}

        if domain not in allowed:
            warnings.append(f"DOMAIN_NOT_ALLOWED_SET_TO_UNKNOWN: {domain}")
            domain = "unknown"

        # Se c'è un hint, non forziamo brutalmente il dominio.
        # Aggiungiamo solo un warning se c'è forte divergenza.
        if domain_hint:
            hint = normalize_text(domain_hint).lower().replace(" ", "_")
            if hint and domain != "unknown" and hint != domain:
                warnings.append(f"DOMAIN_DIFFERS_FROM_HINT: detected={domain}; hint={hint}")

        # Micro euristica non distruttiva: se il testo è quasi vuoto, unknown.
        if len(normalize_text(chunk_text)) < 40:
            domain = "unknown"
            warnings.append("DOMAIN_UNKNOWN_BECAUSE_CHUNK_TOO_SHORT")

        return domain, warnings

    except Exception as exc:
        warnings.append(f"DOMAIN_DETECTION_EXCEPTION: {type(exc).__name__}")
        return "unknown", warnings


def compute_extraction_score(result: MapChunkResult) -> float:
    """
    Calcola un punteggio tecnico leggero.

    Non misura la bellezza del testo.
    Misura solo se il chunk ha prodotto materiale utile.
    """

    try:
        score = 0.0

        if result.facts:
            score += 0.35
        if result.micro_concepts:
            score += 0.25
        if result.entities:
            score += 0.15
        if result.relations:
            score += 0.20
        if result.domain and result.domain != "unknown":
            score += 0.05

        if result.errors:
            score -= 0.20
        if result.blocked:
            score = 0.0

        return max(0.0, min(1.0, round(score, 3)))

    except Exception:
        return 0.0


# =============================================================================
# 6. VALIDAZIONE LEGGERA MAP
# =============================================================================

def validate_map_input(
    chunk_text: str,
    chunk_id: str,
    config: MapPhaseConfig,
) -> List[str]:
    """
    Validazione iniziale non distruttiva.

    Qui controlliamo solo:
    - chunk vuoto
    - chunk troppo corto
    - segnali demo/fallback nel testo sorgente
    """

    warnings: List[str] = []

    try:
        text = normalize_text(chunk_text)

        if not normalize_text(chunk_id):
            warnings.append("CHUNK_ID_EMPTY")

        if not text:
            warnings.append("CHUNK_TEXT_EMPTY")

        if text and len(text) < config.min_chunk_chars:
            warnings.append(f"CHUNK_TEXT_TOO_SHORT: {len(text)} chars")

        if contains_forbidden_signature(text, config.demo_fallback_signatures):
            warnings.append("SOURCE_CONTAINS_DEMO_OR_FALLBACK_SIGNATURE")

        return warnings

    except Exception as exc:
        return [f"INPUT_VALIDATION_EXCEPTION: {type(exc).__name__}"]


def validate_map_extraction_light(
    result: MapChunkResult,
    config: MapPhaseConfig,
) -> MapChunkResult:
    """
    Validazione leggera dopo estrazione LLM.

    Questa funzione NON deve trasformarsi in Super Quality Gate.
    Non cancella stile brutto.
    Non rifinisce la lingua.
    Marca solo warning tecnici.
    """

    try:
        all_texts: List[str] = []
        all_texts.extend(result.facts)
        all_texts.extend(result.micro_concepts)
        all_texts.extend(result.entities)

        for relation in result.relations:
            all_texts.extend([
                relation.subject,
                relation.predicate,
                relation.object,
                relation.evidence,
            ])

        forbidden_found = find_forbidden_signatures(
            texts=all_texts,
            signatures=config.demo_fallback_signatures,
        )

        if forbidden_found:
            result.warnings.append(
                "EXTRACTION_CONTAINS_DEMO_OR_FALLBACK_SIGNATURES: "
                + ", ".join(forbidden_found)
            )
            result.blocked = True

        generic_facts = detect_generic_bad_facts(
            facts=result.facts,
            generic_bad_facts=config.generic_bad_facts,
        )

        if generic_facts:
            result.warnings.append(
                "GENERIC_PREFABRICATED_FACTS_DETECTED: "
                + ", ".join(generic_facts)
            )

        if not result.facts and not result.micro_concepts and not result.entities and not result.relations:
            result.warnings.append("NO_USEFUL_MAP_DATA_EXTRACTED")

        # Micro-concetti troppo lunghi: warning, non cancellazione.
        long_micro_concepts = [
            concept for concept in result.micro_concepts
            if len(concept.split()) > 6
        ]

        if long_micro_concepts:
            result.warnings.append(
                f"MICRO_CONCEPTS_TOO_LONG_COUNT: {len(long_micro_concepts)}"
            )

        result.extraction_score = compute_extraction_score(result)
        return result

    except Exception as exc:
        result.warnings.append(f"MAP_LIGHT_VALIDATION_EXCEPTION: {type(exc).__name__}")
        result.extraction_score = compute_extraction_score(result)
        return result


# =============================================================================
# 7. FUNZIONE PRINCIPALE MAP PER SINGOLO CHUNK
# =============================================================================

def map_chunk_to_facts(
    chunk_text: str,
    chunk_id: str,
    llm_client: LLMClientProtocol,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None,
    config: Optional[MapPhaseConfig] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> MapChunkResult:
    """
    Estrae fatti e micro-concetti da un singolo chunk.

    Caratteristiche:
    - universale
    - parametrica
    - protetta da try/except
    - non blocca l'intera pipeline se il chunk fallisce
    - non produce riassunto narrativo
    - non applica filtri di stile
    """

    cfg = config or MapPhaseConfig()
    meta = metadata or {}

    result = MapChunkResult(
        chunk_id=normalize_text(chunk_id) or "unknown_chunk",
        page_start=page_start,
        page_end=page_end,
        source_char_count=len(normalize_text(chunk_text)),
    )

    try:
        normalized_chunk = normalize_text(chunk_text)

        # ---------------------------------------------------------------------
        # Validazione input leggera
        # ---------------------------------------------------------------------
        input_warnings = validate_map_input(
            chunk_text=normalized_chunk,
            chunk_id=result.chunk_id,
            config=cfg,
        )
        result.warnings.extend(input_warnings)

        if "CHUNK_TEXT_EMPTY" in input_warnings:
            result.errors.append("MAP_SKIPPED_EMPTY_CHUNK")
            result.processed = False
            result.extraction_score = 0.0
            return result

        # ---------------------------------------------------------------------
        # Prompt MAP
        # ---------------------------------------------------------------------
        system_prompt = build_map_system_prompt()
        user_prompt = build_map_user_prompt(
            chunk_text=normalized_chunk,
            chunk_id=result.chunk_id,
            page_start=page_start,
            page_end=page_end,
            config=cfg,
        )

        response_format = build_json_response_format()

        # ---------------------------------------------------------------------
        # Chiamata LLM
        # ---------------------------------------------------------------------
        try:
            raw_output = llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format=response_format,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                metadata={
                    **meta,
                    "phase": "MAP",
                    "chunk_id": result.chunk_id,
                    "page_start": page_start,
                    "page_end": page_end,
                },
            )
            result.raw_llm_output = raw_output

        except Exception as exc:
            result.errors.append(f"LLM_GENERATION_FAILED: {type(exc).__name__}: {exc}")
            result.warnings.append("MAP_CHUNK_FAILED_BUT_PIPELINE_CONTINUES")
            result.processed = False
            result.extraction_score = 0.0
            return result

        # ---------------------------------------------------------------------
        # Parsing JSON robusto
        # ---------------------------------------------------------------------
        parsed_json, json_warnings = extract_json_object(result.raw_llm_output or "")
        result.warnings.extend(json_warnings)

        if parsed_json is None:
            result.errors.append("MAP_JSON_PARSE_FAILED")
            result.warnings.append("RAW_LLM_OUTPUT_STORED_FOR_DEBUG")
            result.processed = False
            result.extraction_score = 0.0
            return result

        # ---------------------------------------------------------------------
        # Normalizzazione dati estratti
        # ---------------------------------------------------------------------
        extracted_domain = parsed_json.get("domain", "unknown")

        domain, domain_warnings = light_domain_detection(
            chunk_text=normalized_chunk,
            extracted_domain=extracted_domain,
            allowed_domains=cfg.allowed_domains,
            domain_hint=cfg.domain_hint,
        )
        result.domain = domain
        result.warnings.extend(domain_warnings)

        result.facts = safe_list_of_strings(
            parsed_json.get("facts", []),
            limit=cfg.max_facts,
        )

        result.micro_concepts = safe_list_of_strings(
            parsed_json.get("micro_concepts", []),
            limit=cfg.max_micro_concepts,
        )

        result.entities = safe_list_of_strings(
            parsed_json.get("entities", []),
            limit=cfg.max_entities,
        )

        result.relations = safe_relations(
            parsed_json.get("relations", []),
            limit=cfg.max_relations,
        )

        result.processed = True

        # ---------------------------------------------------------------------
        # Validazione leggera MAP
        # ---------------------------------------------------------------------
        result = validate_map_extraction_light(result, cfg)

        return result

    except Exception as exc:
        result.errors.append(f"MAP_CHUNK_UNHANDLED_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=3))
        result.processed = False
        result.extraction_score = compute_extraction_score(result)
        return result


# =============================================================================
# 8. ESECUZIONE MAP SU TUTTI I CHUNK
# =============================================================================

def run_map_phase(
    document_id: str,
    chunks: Sequence[ChunkInput],
    llm_client: LLMClientProtocol,
    config: Optional[MapPhaseConfig] = None,
) -> MapPhaseOutput:
    """
    Esegue la Fase 1 — MAP su una lista di chunk.

    Regola fondamentale:
    se un chunk fallisce, la pipeline NON si ferma.
    Il fallimento viene registrato nel MapChunkResult.
    """

    cfg = config or MapPhaseConfig()

    output = MapPhaseOutput(
        document_id=normalize_text(document_id) or "unknown_document",
        total_chunks=len(chunks),
    )

    try:
        if not chunks:
            output.global_warnings.append("NO_CHUNKS_PROVIDED")
            return output

        for chunk in chunks:
            try:
                result = map_chunk_to_facts(
                    chunk_text=chunk.text,
                    chunk_id=chunk.chunk_id,
                    llm_client=llm_client,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    config=cfg,
                    metadata=chunk.metadata,
                )

                output.results.append(result)

                if result.processed:
                    output.processed_chunks += 1
                else:
                    output.failed_chunks += 1

                if result.blocked:
                    output.blocked_chunks += 1

            except Exception as exc:
                fallback_result = MapChunkResult(
                    chunk_id=normalize_text(getattr(chunk, "chunk_id", "")) or "unknown_chunk",
                    page_start=getattr(chunk, "page_start", None),
                    page_end=getattr(chunk, "page_end", None),
                    domain="unknown",
                    warnings=[
                        "MAP_PHASE_PER_CHUNK_EXCEPTION",
                        traceback.format_exc(limit=3),
                    ],
                    errors=[
                        f"MAP_PHASE_CHUNK_FAILED: {type(exc).__name__}: {exc}"
                    ],
                    processed=False,
                    blocked=False,
                    extraction_score=0.0,
                    source_char_count=len(normalize_text(getattr(chunk, "text", ""))),
                )

                output.results.append(fallback_result)
                output.failed_chunks += 1

        output.detected_domains = sorted({
            result.domain
            for result in output.results
            if result.domain and result.domain != "unknown"
        })

        return output

    except Exception as exc:
        output.global_errors.append(f"MAP_PHASE_UNHANDLED_EXCEPTION: {type(exc).__name__}: {exc}")
        output.global_warnings.append(traceback.format_exc(limit=5))
        return output


# =============================================================================
# 9. SERIALIZZAZIONE SICURA
# =============================================================================

def map_chunk_result_to_dict(result: MapChunkResult) -> Dict[str, Any]:
    """
    Converte un MapChunkResult in dizionario JSON-serializzabile.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "chunk_id": getattr(result, "chunk_id", "unknown_chunk"),
            "warnings": ["MAP_CHUNK_RESULT_SERIALIZATION_FAILED"],
            "errors": [],
        }


def map_phase_output_to_dict(output: MapPhaseOutput) -> Dict[str, Any]:
    """
    Converte MapPhaseOutput in dizionario JSON-serializzabile.
    """

    try:
        return asdict(output)
    except Exception:
        return {
            "document_id": getattr(output, "document_id", "unknown_document"),
            "phase_name": "MAP",
            "global_warnings": ["MAP_PHASE_OUTPUT_SERIALIZATION_FAILED"],
            "global_errors": [],
            "results": [],
        }


def map_phase_output_to_json(output: MapPhaseOutput, indent: int = 2) -> str:
    """
    Serializza l'output MAP in JSON.

    Utile per:
    - report
    - debug
    - passaggio alla fase REDUCE
    - salvataggio intermedio
    """

    try:
        return json.dumps(
            map_phase_output_to_dict(output),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(output, "document_id", "unknown_document"),
                "phase_name": "MAP",
                "global_errors": [
                    f"MAP_PHASE_JSON_SERIALIZATION_FAILED: {type(exc).__name__}: {exc}"
                ],
            },
            ensure_ascii=False,
            indent=indent,
        )


# =============================================================================
# 10. MOCK CLIENT FACOLTATIVO PER TEST LOCALI
# =============================================================================

class MockLLMClient:
    """
    Client finto per testare la pipeline senza chiamare un vero LLM.

    Da usare solo nei test backend.
    Non rappresenta la qualità reale del modello.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        return json.dumps(
            {
                "domain": "technical",
                "facts": [
                    "Il chunk contiene informazioni operative estratte come fatto grezzo."
                ],
                "micro_concepts": [
                    "informazioni operative",
                    "fatto grezzo",
                ],
                "entities": [
                    "chunk",
                    "documento",
                ],
                "relations": [
                    {
                        "subject": "chunk",
                        "predicate": "contiene",
                        "object": "informazioni operative",
                        "evidence": "Dato simulato per test backend.",
                    }
                ],
            },
            ensure_ascii=False,
        )


# =============================================================================
# 11. TEST MINIMO ESEGUIBILE DA TERMINALE
# =============================================================================

if __name__ == "__main__":
    test_chunks = [
        ChunkInput(
            chunk_id="chunk_001",
            text=(
                "Il controllo degli accessi limita l'utilizzo dei sistemi aziendali "
                "agli utenti autorizzati. Le credenziali devono essere protette e "
                "aggiornate periodicamente."
            ),
            page_start=1,
            page_end=1,
        ),
        ChunkInput(
            chunk_id="chunk_002",
            text="",
            page_start=2,
            page_end=2,
        ),
    ]

    test_output = run_map_phase(
        document_id="documento_test_backend",
        chunks=test_chunks,
        llm_client=MockLLMClient(),
        config=MapPhaseConfig(
            domain_hint="technical",
        ),
    )

    print(map_phase_output_to_json(test_output))



# =============================================================================
# FASE 2 — REDUCE V1
# RAG GERARCHICO MAP-REDUCE AD ALBERO
#
# Obiettivo:
# - prendere i risultati MAP
# - ignorare chunk falliti/bloccati
# - unire facts, micro_concepts, entities e relations
# - deduplicare in modo conservativo
# - costruire un macro-grezzo strutturato
#
# Questa fase NON deve:
# - scrivere un riassunto elegante
# - migliorare lo stile
# - applicare il Super Quality Gate
# - toccare UI/CSS/pulsanti
# =============================================================================


@dataclass
class TreeReduceConfig:
    """
    Configurazione universale della Fase 2 REDUCE.

    group_size:
        Numero di elementi da fondere per gruppo a ogni livello.
        Esempio:
        - 500 chunk MAP
        - group_size 8
        - livello 1: gruppi da 8
        - livello 2: gruppi di gruppi
        - fino a root unico.

    dedupe_conservative:
        True = deduplica prudente, evita di cancellare fatti simili ma diversi.
    """

    group_size: int = 8
    max_levels: int = 20
    dedupe_conservative: bool = True
    min_usable_fact_chars: int = 8
    keep_blocked_chunks_out: bool = True
    keep_failed_chunks_out: bool = True


@dataclass
class ReducedFact:
    """
    Fatto consolidato durante REDUCE.

    Non è una frase rifinita.
    È un fatto grezzo mantenuto con tracciabilità.
    """

    text: str
    source_chunk_ids: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    support_count: int = 1
    domains: List[str] = field(default_factory=list)


@dataclass
class ReducedRelation:
    """
    Relazione consolidata.

    Esempio:
    subject='revisione periodica degli accessi'
    predicate='riduce il rischio che'
    object='utenti non più autorizzati mantengano permessi attivi'
    """

    subject: str
    predicate: str
    object: str
    evidence: str = ""
    source_chunk_ids: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    support_count: int = 1


@dataclass
class ReduceGroupResult:
    """
    Risultato di un gruppo REDUCE.

    Può rappresentare:
    - un gruppo di chunk MAP
    - un gruppo di gruppi REDUCE
    - il root finale dell'albero
    """

    group_id: str
    level: int
    source_chunk_ids: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)

    facts: List[ReducedFact] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    relations: List[ReducedRelation] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)

    input_items_count: int = 0
    input_facts_count: int = 0
    output_facts_count: int = 0

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class MacroRawSection:
    """
    Sezione macro-grezza.

    Non è ancora testo finale.
    Serve come blocco ordinato per il futuro Super Quality Gate.
    """

    section_id: str
    title: str
    source_chunk_ids: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    facts: List[str] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MacroRawDocument:
    """
    Documento macro-grezzo consolidato.

    Questo è l'output concettuale della REDUCE.
    Non è il riassunto finale.
    """

    document_id: str
    domain_profile: List[str] = field(default_factory=list)
    section_blocks: List[MacroRawSection] = field(default_factory=list)
    global_facts: List[str] = field(default_factory=list)
    global_micro_concepts: List[str] = field(default_factory=list)
    global_entities: List[str] = field(default_factory=list)
    global_relations: List[Dict[str, Any]] = field(default_factory=list)
    coverage_report: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class TreeReduceOutput:
    """
    Output complessivo Fase 2 REDUCE.
    """

    document_id: str
    phase_name: str = "REDUCE"
    total_map_results: int = 0
    usable_map_results: int = 0
    skipped_map_results: int = 0
    levels_built: int = 0

    level_groups: List[List[ReduceGroupResult]] = field(default_factory=list)
    root_group: Optional[ReduceGroupResult] = None
    macro_document: Optional[MacroRawDocument] = None

    global_warnings: List[str] = field(default_factory=list)
    global_errors: List[str] = field(default_factory=list)


def reduce_normalize_key(text: Any) -> str:
    """
    Chiave normalizzata per deduplica prudente.

    Non deve essere troppo aggressiva:
    due fatti simili ma diversi NON devono essere fusi per errore.
    """

    try:
        value = normalize_text(text).lower()
        value = re.sub(r"[^\w\sàèéìòù]", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"\s+", " ", value).strip()
        return value
    except Exception:
        return ""


def reduce_unique_strings(values: Sequence[Any], limit: Optional[int] = None) -> List[str]:
    """
    Deduplica stringhe conservando ordine.
    """

    output: List[str] = []
    seen = set()

    try:
        for value in values:
            text = normalize_text(value)
            key = reduce_normalize_key(text)

            if not text or not key:
                continue

            if key in seen:
                continue

            seen.add(key)
            output.append(text)

            if limit and len(output) >= limit:
                break

        return output

    except Exception:
        return output


def reduce_pages_from_range(page_start: Optional[int], page_end: Optional[int]) -> List[int]:
    """
    Converte page_start/page_end in lista pagine.
    """

    try:
        if page_start is None and page_end is None:
            return []

        if page_start is None:
            return [int(page_end)]

        if page_end is None:
            return [int(page_start)]

        start = int(page_start)
        end = int(page_end)

        if end < start:
            start, end = end, start

        if end - start > 10000:
            return [start, end]

        return list(range(start, end + 1))

    except Exception:
        return []


def reduce_get_source_chunk_ids(item: Any) -> List[str]:
    """
    Recupera chunk id da MapChunkResult o ReduceGroupResult.
    """

    try:
        if hasattr(item, "source_chunk_ids"):
            return reduce_unique_strings(getattr(item, "source_chunk_ids", []))

        chunk_id = normalize_text(getattr(item, "chunk_id", ""))
        return [chunk_id] if chunk_id else []

    except Exception:
        return []


def reduce_get_source_pages(item: Any) -> List[int]:
    """
    Recupera pagine da MapChunkResult o ReduceGroupResult.
    """

    pages: List[int] = []

    try:
        if hasattr(item, "source_pages"):
            raw_pages = getattr(item, "source_pages", [])
            for page in raw_pages:
                try:
                    pages.append(int(page))
                except Exception:
                    pass
            return sorted(set(pages))

        return reduce_pages_from_range(
            getattr(item, "page_start", None),
            getattr(item, "page_end", None),
        )

    except Exception:
        return []


def reduce_get_facts_from_item(item: Any) -> List[ReducedFact]:
    """
    Estrae facts da MapChunkResult o ReduceGroupResult.
    """

    output: List[ReducedFact] = []

    try:
        source_ids = reduce_get_source_chunk_ids(item)
        source_pages = reduce_get_source_pages(item)
        domain = normalize_text(getattr(item, "domain", ""))

        raw_facts = getattr(item, "facts", [])

        for fact in raw_facts:
            if isinstance(fact, ReducedFact):
                output.append(fact)
                continue

            text = normalize_text(fact)
            if not text:
                continue

            output.append(
                ReducedFact(
                    text=text,
                    source_chunk_ids=list(source_ids),
                    source_pages=list(source_pages),
                    support_count=1,
                    domains=[domain] if domain else [],
                )
            )

        return output

    except Exception:
        return output


def reduce_merge_facts(items: Sequence[Any], config: TreeReduceConfig) -> List[ReducedFact]:
    """
    Unisce facts da più elementi e deduplica in modo conservativo.
    """

    merged: Dict[str, ReducedFact] = {}

    try:
        for item in items:
            for fact in reduce_get_facts_from_item(item):
                text = normalize_text(fact.text)

                if len(text) < config.min_usable_fact_chars:
                    continue

                key = reduce_normalize_key(text)

                if not key:
                    continue

                if key not in merged:
                    merged[key] = ReducedFact(
                        text=text,
                        source_chunk_ids=reduce_unique_strings(fact.source_chunk_ids),
                        source_pages=sorted(set(fact.source_pages)),
                        support_count=max(1, int(fact.support_count or 1)),
                        domains=reduce_unique_strings(fact.domains),
                    )
                else:
                    existing = merged[key]
                    existing.source_chunk_ids = reduce_unique_strings(
                        existing.source_chunk_ids + fact.source_chunk_ids
                    )
                    existing.source_pages = sorted(set(existing.source_pages + fact.source_pages))
                    existing.support_count += max(1, int(fact.support_count or 1))
                    existing.domains = reduce_unique_strings(existing.domains + fact.domains)

        return list(merged.values())

    except Exception:
        return list(merged.values())


def reduce_get_strings_from_item(item: Any, field_name: str) -> List[str]:
    """
    Recupera micro_concepts/entities/domains da MapChunkResult o ReduceGroupResult.
    """

    try:
        values = getattr(item, field_name, [])
        return safe_list_of_strings(values, limit=100000)
    except Exception:
        return []


def reduce_relation_to_reduced(item_relation: Any, source_ids: List[str], source_pages: List[int]) -> Optional[ReducedRelation]:
    """
    Converte RelationItem/ReducedRelation/dict in ReducedRelation.
    """

    try:
        if isinstance(item_relation, ReducedRelation):
            return item_relation

        if isinstance(item_relation, dict):
            subject = normalize_text(item_relation.get("subject", ""))
            predicate = normalize_text(item_relation.get("predicate", ""))
            obj = normalize_text(item_relation.get("object", ""))
            evidence = normalize_text(item_relation.get("evidence", ""))
        else:
            subject = normalize_text(getattr(item_relation, "subject", ""))
            predicate = normalize_text(getattr(item_relation, "predicate", ""))
            obj = normalize_text(getattr(item_relation, "object", ""))
            evidence = normalize_text(getattr(item_relation, "evidence", ""))

        if not subject and not predicate and not obj:
            return None

        return ReducedRelation(
            subject=subject,
            predicate=predicate,
            object=obj,
            evidence=evidence,
            source_chunk_ids=list(source_ids),
            source_pages=list(source_pages),
            support_count=1,
        )

    except Exception:
        return None


def reduce_merge_relations(items: Sequence[Any]) -> List[ReducedRelation]:
    """
    Unisce relations da più elementi e deduplica soggetto/predicato/oggetto.
    """

    merged: Dict[str, ReducedRelation] = {}

    try:
        for item in items:
            source_ids = reduce_get_source_chunk_ids(item)
            source_pages = reduce_get_source_pages(item)

            raw_relations = getattr(item, "relations", [])

            for raw_relation in raw_relations:
                relation = reduce_relation_to_reduced(raw_relation, source_ids, source_pages)

                if relation is None:
                    continue

                key = reduce_normalize_key(
                    f"{relation.subject} {relation.predicate} {relation.object}"
                )

                if not key:
                    continue

                if key not in merged:
                    merged[key] = relation
                else:
                    existing = merged[key]
                    existing.source_chunk_ids = reduce_unique_strings(
                        existing.source_chunk_ids + relation.source_chunk_ids
                    )
                    existing.source_pages = sorted(set(existing.source_pages + relation.source_pages))
                    existing.support_count += max(1, int(relation.support_count or 1))

                    if not existing.evidence and relation.evidence:
                        existing.evidence = relation.evidence

        return list(merged.values())

    except Exception:
        return list(merged.values())


def reduce_fact_group(
    group_id: str,
    level: int,
    items: Sequence[Any],
    config: Optional[TreeReduceConfig] = None,
) -> ReduceGroupResult:
    """
    Riduce un gruppo di MapChunkResult o ReduceGroupResult.

    Questa funzione è il cuore della REDUCE V1.
    Non usa LLM.
    Non riscrive.
    Non abbellisce.
    """

    cfg = config or TreeReduceConfig()

    result = ReduceGroupResult(
        group_id=normalize_text(group_id) or f"reduce_l{level}_unknown",
        level=level,
        input_items_count=len(items),
    )

    try:
        source_ids: List[str] = []
        source_pages: List[int] = []
        all_micro_concepts: List[str] = []
        all_entities: List[str] = []
        all_domains: List[str] = []
        input_facts_count = 0

        for item in items:
            source_ids.extend(reduce_get_source_chunk_ids(item))
            source_pages.extend(reduce_get_source_pages(item))
            all_micro_concepts.extend(reduce_get_strings_from_item(item, "micro_concepts"))
            all_entities.extend(reduce_get_strings_from_item(item, "entities"))

            if hasattr(item, "domains"):
                all_domains.extend(reduce_get_strings_from_item(item, "domains"))
            else:
                domain = normalize_text(getattr(item, "domain", ""))
                if domain:
                    all_domains.append(domain)

            input_facts_count += len(getattr(item, "facts", []) or [])

        result.source_chunk_ids = reduce_unique_strings(source_ids)
        result.source_pages = sorted(set(source_pages))
        result.facts = reduce_merge_facts(items, cfg)
        result.micro_concepts = reduce_unique_strings(all_micro_concepts)
        result.entities = reduce_unique_strings(all_entities)
        result.relations = reduce_merge_relations(items)
        result.domains = reduce_unique_strings(all_domains)

        result.input_facts_count = input_facts_count
        result.output_facts_count = len(result.facts)

        if not result.facts and not result.micro_concepts and not result.entities and not result.relations:
            result.warnings.append("REDUCE_GROUP_EMPTY_AFTER_MERGE")

        if result.input_facts_count > 0 and result.output_facts_count == 0:
            result.errors.append("REDUCE_LOST_ALL_FACTS")

        if result.output_facts_count > result.input_facts_count and result.input_facts_count > 0:
            result.warnings.append("REDUCE_OUTPUT_FACTS_GREATER_THAN_INPUT_FACTS_UNEXPECTED")

        return result

    except Exception as exc:
        result.errors.append(f"REDUCE_GROUP_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=3))
        return result


def reduce_group_items_by_size(items: Sequence[Any], group_size: int) -> List[List[Any]]:
    """
    Divide elementi in gruppi ordinati.
    """

    groups: List[List[Any]] = []

    try:
        safe_size = max(1, int(group_size or 1))

        for index in range(0, len(items), safe_size):
            groups.append(list(items[index:index + safe_size]))

        return groups

    except Exception:
        return [list(items)] if items else []


def reduce_filter_usable_map_results(
    map_results: Sequence[MapChunkResult],
    config: TreeReduceConfig,
) -> Tuple[List[MapChunkResult], List[MapChunkResult]]:
    """
    Separa risultati MAP usabili da risultati saltati.

    Esclude:
    - chunk failed se configurato
    - chunk blocked se configurato
    - chunk senza materiale utile
    """

    usable: List[MapChunkResult] = []
    skipped: List[MapChunkResult] = []

    try:
        for result in map_results:
            should_skip = False

            if config.keep_failed_chunks_out and not getattr(result, "processed", False):
                should_skip = True

            if config.keep_blocked_chunks_out and getattr(result, "blocked", False):
                should_skip = True

            has_material = bool(
                getattr(result, "facts", None)
                or getattr(result, "micro_concepts", None)
                or getattr(result, "entities", None)
                or getattr(result, "relations", None)
            )

            if not has_material:
                should_skip = True

            if should_skip:
                skipped.append(result)
            else:
                usable.append(result)

        return usable, skipped

    except Exception:
        return [], list(map_results)


def reduce_build_macro_sections(level_one_groups: Sequence[ReduceGroupResult]) -> List[MacroRawSection]:
    """
    Costruisce sezioni macro-grezze dai gruppi di primo livello.

    Le sezioni preservano l'ordine documentale.
    """

    sections: List[MacroRawSection] = []

    try:
        for index, group in enumerate(level_one_groups, start=1):
            pages = sorted(set(group.source_pages))
            if pages:
                title = f"Blocco {index} — pagine {pages[0]}-{pages[-1]}"
            else:
                title = f"Blocco {index}"

            section = MacroRawSection(
                section_id=group.group_id,
                title=title,
                source_chunk_ids=list(group.source_chunk_ids),
                source_pages=list(pages),
                facts=[fact.text for fact in group.facts],
                micro_concepts=list(group.micro_concepts),
                entities=list(group.entities),
                relations=[
                    {
                        "subject": relation.subject,
                        "predicate": relation.predicate,
                        "object": relation.object,
                        "evidence": relation.evidence,
                        "source_chunk_ids": relation.source_chunk_ids,
                        "source_pages": relation.source_pages,
                        "support_count": relation.support_count,
                    }
                    for relation in group.relations
                ],
            )
            sections.append(section)

        return sections

    except Exception:
        return sections


def reduce_build_macro_document(
    document_id: str,
    root_group: ReduceGroupResult,
    level_one_groups: Sequence[ReduceGroupResult],
    total_map_results: int,
    usable_map_results: int,
    skipped_map_results: int,
) -> MacroRawDocument:
    """
    Costruisce MacroRawDocument finale della REDUCE.

    Questo NON è il riassunto finale.
    È il macro-grezzo strutturato per la Fase 3.
    """

    macro = MacroRawDocument(document_id=document_id)

    try:
        macro.domain_profile = list(root_group.domains)
        macro.section_blocks = reduce_build_macro_sections(level_one_groups)
        macro.global_facts = [fact.text for fact in root_group.facts]
        macro.global_micro_concepts = list(root_group.micro_concepts)
        macro.global_entities = list(root_group.entities)
        macro.global_relations = [
            {
                "subject": relation.subject,
                "predicate": relation.predicate,
                "object": relation.object,
                "evidence": relation.evidence,
                "source_chunk_ids": relation.source_chunk_ids,
                "source_pages": relation.source_pages,
                "support_count": relation.support_count,
            }
            for relation in root_group.relations
        ]

        input_facts_count = root_group.input_facts_count
        output_facts_count = root_group.output_facts_count

        macro.coverage_report = {
            "total_map_results": total_map_results,
            "usable_map_results": usable_map_results,
            "skipped_map_results": skipped_map_results,
            "global_facts_count": len(macro.global_facts),
            "global_micro_concepts_count": len(macro.global_micro_concepts),
            "global_entities_count": len(macro.global_entities),
            "global_relations_count": len(macro.global_relations),
            "root_input_facts_count": input_facts_count,
            "root_output_facts_count": output_facts_count,
            "source_pages_count": len(root_group.source_pages),
            "source_chunks_count": len(root_group.source_chunk_ids),
        }

        if usable_map_results == 0:
            macro.warnings.append("MACRO_DOCUMENT_HAS_NO_USABLE_MAP_RESULTS")

        if not macro.global_facts:
            macro.warnings.append("MACRO_DOCUMENT_HAS_NO_GLOBAL_FACTS")

        return macro

    except Exception as exc:
        macro.warnings.append(f"MACRO_DOCUMENT_BUILD_EXCEPTION: {type(exc).__name__}: {exc}")
        return macro


def run_tree_reduce_phase(
    map_output: MapPhaseOutput,
    config: Optional[TreeReduceConfig] = None,
) -> TreeReduceOutput:
    """
    Esegue REDUCE gerarchico ad albero.

    Input:
    - MapPhaseOutput della Fase 1

    Output:
    - TreeReduceOutput con root_group e MacroRawDocument

    Questa funzione è protetta:
    se un gruppo fallisce, registra errori e non tocca UI.
    """

    cfg = config or TreeReduceConfig()

    output = TreeReduceOutput(
        document_id=normalize_text(getattr(map_output, "document_id", "")) or "unknown_document",
        total_map_results=len(getattr(map_output, "results", []) or []),
    )

    try:
        map_results = list(getattr(map_output, "results", []) or [])

        usable, skipped = reduce_filter_usable_map_results(map_results, cfg)

        output.usable_map_results = len(usable)
        output.skipped_map_results = len(skipped)

        if not usable:
            output.global_warnings.append("REDUCE_NO_USABLE_MAP_RESULTS")
            output.macro_document = MacroRawDocument(
                document_id=output.document_id,
                warnings=["REDUCE_NO_USABLE_MAP_RESULTS"],
            )
            return output

        current_items: List[Any] = list(usable)
        level = 1

        while current_items and level <= cfg.max_levels:
            grouped_items = reduce_group_items_by_size(current_items, cfg.group_size)
            level_results: List[ReduceGroupResult] = []

            for group_index, group_items in enumerate(grouped_items, start=1):
                group_id = f"reduce_l{level}_g{group_index:04d}"
                group_result = reduce_fact_group(
                    group_id=group_id,
                    level=level,
                    items=group_items,
                    config=cfg,
                )
                level_results.append(group_result)

            output.level_groups.append(level_results)

            if len(level_results) == 1:
                output.root_group = level_results[0]
                output.levels_built = level
                break

            current_items = list(level_results)
            level += 1

        if output.root_group is None:
            output.global_errors.append("REDUCE_ROOT_GROUP_NOT_CREATED")
            return output

        level_one_groups = output.level_groups[0] if output.level_groups else [output.root_group]

        output.macro_document = reduce_build_macro_document(
            document_id=output.document_id,
            root_group=output.root_group,
            level_one_groups=level_one_groups,
            total_map_results=output.total_map_results,
            usable_map_results=output.usable_map_results,
            skipped_map_results=output.skipped_map_results,
        )

        return output

    except Exception as exc:
        output.global_errors.append(f"TREE_REDUCE_PHASE_EXCEPTION: {type(exc).__name__}: {exc}")
        output.global_warnings.append(traceback.format_exc(limit=5))
        return output


def tree_reduce_output_to_dict(output: TreeReduceOutput) -> Dict[str, Any]:
    """
    Serializza TreeReduceOutput in dict.
    """

    try:
        return asdict(output)
    except Exception:
        return {
            "document_id": getattr(output, "document_id", "unknown_document"),
            "phase_name": "REDUCE",
            "global_errors": ["TREE_REDUCE_OUTPUT_SERIALIZATION_FAILED"],
        }


def tree_reduce_output_to_json(output: TreeReduceOutput, indent: int = 2) -> str:
    """
    Serializza TreeReduceOutput in JSON.
    """

    try:
        return json.dumps(
            tree_reduce_output_to_dict(output),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(output, "document_id", "unknown_document"),
                "phase_name": "REDUCE",
                "global_errors": [
                    f"TREE_REDUCE_JSON_SERIALIZATION_FAILED: {type(exc).__name__}: {exc}"
                ],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 2 — REDUCE V1
# =============================================================================



# =============================================================================
# FASE 3 — OUTPUT BUILDER V1
# RAG GERARCHICO MAP-REDUCE AD ALBERO
#
# Obiettivo:
# - prendere il MacroRawDocument della Fase 2 REDUCE
# - generare bozze strutturate di output
#
# Questa fase NON deve:
# - applicare il Super Quality Gate finale
# - fare rifinitura linguistica forte
# - toccare UI/CSS/pulsanti
# - generare HTML, card grafiche o layout
#
# Output prodotti:
# - summary_draft
# - cards_draft
# - study_questions_draft
# - quiz_draft
# - study_pack_draft
# =============================================================================


@dataclass
class OutputBuilderConfig:
    """
    Configurazione universale della Fase 3.

    Tutti i limiti sono parametrici.
    Nessun valore è legato a un documento specifico.
    """

    max_summary_facts: int = 30
    max_cards: int = 12
    max_study_questions: int = 12
    max_quiz_questions: int = 8
    max_study_pack_sections: int = 20
    max_fact_chars: int = 500
    min_quiz_options: int = 4
    include_source_pages: bool = True


@dataclass
class SummaryDraft:
    """
    Bozza di riassunto.

    Non è ancora il testo finale elegante.
    È una struttura ordinata basata sui fatti consolidati.
    """

    title: str
    key_points: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    source_facts_count: int = 0
    warnings: List[str] = field(default_factory=list)


@dataclass
class CardDraft:
    """
    Bozza testuale di una card.

    Non contiene grafica, CSS, layout o pulsanti.
    """

    card_id: str
    title: str
    message_key: str
    source_facts: List[str] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StudyQuestionDraft:
    """
    Bozza di domanda studio.

    La Fase 4 potrà poi rifinire tono, fluidità e qualità didattica.
    """

    question_id: str
    question: str
    answer_guide: str
    source_facts: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class QuizOptionDraft:
    """
    Opzione bozza per quiz.

    Non è ancora validazione finale dei distrattori forti.
    """

    option_id: str
    text: str
    is_correct: bool = False


@dataclass
class QuizQuestionDraft:
    """
    Bozza di domanda quiz.

    La Fase 4 o un validatore quiz dedicato controllerà:
    - distrattori forti
    - naturalezza
    - non ambiguità
    - spiegazione finale
    """

    question_id: str
    question: str
    options: List[QuizOptionDraft] = field(default_factory=list)
    correct_option_id: str = ""
    explanation_draft: str = ""
    source_facts: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StudyPackSectionDraft:
    """
    Sezione bozza dello study pack.
    """

    section_id: str
    title: str
    key_facts: List[str] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StudyPackDraft:
    """
    Bozza study pack.

    Non è ancora libro bianco finale.
    È una struttura ordinata pronta per il Super Quality Gate.
    """

    title: str
    sections: List[StudyPackSectionDraft] = field(default_factory=list)
    global_micro_concepts: List[str] = field(default_factory=list)
    global_entities: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class OutputBuilderResult:
    """
    Output complessivo della Fase 3.
    """

    document_id: str
    phase_name: str = "OUTPUT_BUILDER"

    summary_draft: Optional[SummaryDraft] = None
    cards_draft: List[CardDraft] = field(default_factory=list)
    study_questions_draft: List[StudyQuestionDraft] = field(default_factory=list)
    quiz_draft: List[QuizQuestionDraft] = field(default_factory=list)
    study_pack_draft: Optional[StudyPackDraft] = None

    input_global_facts_count: int = 0
    input_sections_count: int = 0

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def output_trim_text(text: Any, max_chars: int = 500) -> str:
    """
    Taglio prudente di testo troppo lungo.

    Non riscrive.
    Non abbellisce.
    Serve solo a evitare bozze ingestibili.
    """

    try:
        value = normalize_text(text)
        if max_chars <= 0:
            return value

        if len(value) <= max_chars:
            return value

        return value[:max_chars].rstrip() + "..."

    except Exception:
        return ""


def output_make_title_from_fact(fact: str, fallback: str, max_words: int = 8) -> str:
    """
    Crea un titolo tecnico breve da un fatto.

    Non è titolo grafico finale.
    """

    try:
        text = normalize_text(fact).rstrip(".")
        words = text.split()

        if not words:
            return fallback

        title = " ".join(words[:max_words]).strip()

        if len(words) > max_words:
            title += "..."

        return title[0].upper() + title[1:] if title else fallback

    except Exception:
        return fallback


def output_collect_macro_pages(macro_document: MacroRawDocument) -> List[int]:
    """
    Raccoglie pagine dalle sezioni macro.
    """

    pages: List[int] = []

    try:
        for section in getattr(macro_document, "section_blocks", []) or []:
            for page in getattr(section, "source_pages", []) or []:
                try:
                    pages.append(int(page))
                except Exception:
                    pass

        return sorted(set(pages))

    except Exception:
        return []


def output_get_global_facts(macro_document: MacroRawDocument) -> List[str]:
    """
    Recupera facts globali deduplicati.
    """

    try:
        return reduce_unique_strings(getattr(macro_document, "global_facts", []) or [])
    except Exception:
        return []


def output_get_global_concepts(macro_document: MacroRawDocument) -> List[str]:
    """
    Recupera micro-concepts globali deduplicati.
    """

    try:
        return reduce_unique_strings(getattr(macro_document, "global_micro_concepts", []) or [])
    except Exception:
        return []


def output_get_global_entities(macro_document: MacroRawDocument) -> List[str]:
    """
    Recupera entities globali deduplicate.
    """

    try:
        return reduce_unique_strings(getattr(macro_document, "global_entities", []) or [])
    except Exception:
        return []


def build_summary_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> SummaryDraft:
    """
    Costruisce una bozza di riassunto.

    Importante:
    - non produce prosa finale elegante
    - non fonde tutto in un testo lungo
    - conserva punti chiave ordinati
    """

    cfg = config or OutputBuilderConfig()

    draft = SummaryDraft(
        title="Bozza riassunto macro-grezzo",
    )

    try:
        facts = output_get_global_facts(macro_document)
        pages = output_collect_macro_pages(macro_document)

        selected_facts = facts[: max(0, cfg.max_summary_facts)]

        draft.key_points = [
            output_trim_text(fact, cfg.max_fact_chars)
            for fact in selected_facts
            if normalize_text(fact)
        ]

        draft.source_pages = pages if cfg.include_source_pages else []
        draft.source_facts_count = len(facts)

        if not draft.key_points:
            draft.warnings.append("SUMMARY_DRAFT_NO_KEY_POINTS")

        if len(facts) > len(draft.key_points):
            draft.warnings.append(
                f"SUMMARY_DRAFT_TRUNCATED_FACTS: selected={len(draft.key_points)} total={len(facts)}"
            )

        return draft

    except Exception as exc:
        draft.warnings.append(f"SUMMARY_DRAFT_EXCEPTION: {type(exc).__name__}: {exc}")
        return draft


def build_cards_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> List[CardDraft]:
    """
    Costruisce bozze card testuali.

    Non genera grafica.
    Non genera CSS.
    Non genera layout.
    """

    cfg = config or OutputBuilderConfig()
    cards: List[CardDraft] = []

    try:
        sections = list(getattr(macro_document, "section_blocks", []) or [])
        global_concepts = output_get_global_concepts(macro_document)

        for index, section in enumerate(sections[: max(0, cfg.max_cards)], start=1):
            section_facts = reduce_unique_strings(getattr(section, "facts", []) or [])
            section_concepts = reduce_unique_strings(getattr(section, "micro_concepts", []) or [])

            if not section_facts and not section_concepts:
                continue

            main_fact = section_facts[0] if section_facts else ""
            title_source = section_concepts[0] if section_concepts else main_fact

            card = CardDraft(
                card_id=f"card_draft_{index:03d}",
                title=output_make_title_from_fact(
                    title_source,
                    fallback=f"Card bozza {index}",
                    max_words=6,
                ),
                message_key=output_trim_text(main_fact or title_source, cfg.max_fact_chars),
                source_facts=[
                    output_trim_text(fact, cfg.max_fact_chars)
                    for fact in section_facts[:5]
                ],
                micro_concepts=section_concepts[:8] or global_concepts[:8],
                source_pages=list(getattr(section, "source_pages", []) or []) if cfg.include_source_pages else [],
            )

            if not card.message_key:
                card.warnings.append("CARD_DRAFT_EMPTY_MESSAGE_KEY")

            cards.append(card)

        if not cards:
            facts = output_get_global_facts(macro_document)

            for index, fact in enumerate(facts[: max(0, cfg.max_cards)], start=1):
                card = CardDraft(
                    card_id=f"card_draft_{index:03d}",
                    title=output_make_title_from_fact(fact, fallback=f"Card bozza {index}", max_words=6),
                    message_key=output_trim_text(fact, cfg.max_fact_chars),
                    source_facts=[output_trim_text(fact, cfg.max_fact_chars)],
                    micro_concepts=global_concepts[:8],
                    source_pages=output_collect_macro_pages(macro_document) if cfg.include_source_pages else [],
                )
                cards.append(card)

        return cards

    except Exception:
        return cards


def build_study_questions_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> List[StudyQuestionDraft]:
    """
    Costruisce bozze di domande studio.

    Non è ancora quality gate didattico finale.
    """

    cfg = config or OutputBuilderConfig()
    questions: List[StudyQuestionDraft] = []

    try:
        facts = output_get_global_facts(macro_document)
        pages = output_collect_macro_pages(macro_document)

        for index, fact in enumerate(facts[: max(0, cfg.max_study_questions)], start=1):
            trimmed_fact = output_trim_text(fact, cfg.max_fact_chars)
            short_title = output_make_title_from_fact(trimmed_fact, fallback="questo punto", max_words=7)

            question = StudyQuestionDraft(
                question_id=f"study_question_draft_{index:03d}",
                question=f"Quale regola o informazione emerge da: {short_title}?",
                answer_guide=trimmed_fact,
                source_facts=[trimmed_fact],
                source_pages=pages if cfg.include_source_pages else [],
            )

            questions.append(question)

        return questions

    except Exception:
        return questions


def build_quiz_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> List[QuizQuestionDraft]:
    """
    Costruisce bozze quiz da fatti reali.

    Regola:
    - non inventa distrattori fuori documento
    - usa altri facts come opzioni alternative
    - se non ci sono abbastanza facts, non forza quiz finto
    """

    cfg = config or OutputBuilderConfig()
    quiz: List[QuizQuestionDraft] = []

    try:
        facts = output_get_global_facts(macro_document)
        pages = output_collect_macro_pages(macro_document)

        if len(facts) < cfg.min_quiz_options:
            return quiz

        max_questions = min(max(0, cfg.max_quiz_questions), len(facts))

        option_ids = ["A", "B", "C", "D"]

        for index in range(max_questions):
            correct_fact = output_trim_text(facts[index], cfg.max_fact_chars)

            distractor_pool = [
                output_trim_text(fact, cfg.max_fact_chars)
                for pos, fact in enumerate(facts)
                if pos != index
            ]

            if len(distractor_pool) < 3:
                continue

            correct_position = index % 4
            raw_options = distractor_pool[:3]
            raw_options.insert(correct_position, correct_fact)

            options: List[QuizOptionDraft] = []

            for option_index, option_text in enumerate(raw_options[:4]):
                option_id = option_ids[option_index]
                options.append(
                    QuizOptionDraft(
                        option_id=option_id,
                        text=option_text,
                        is_correct=(option_index == correct_position),
                    )
                )

            correct_option_id = option_ids[correct_position]

            question = QuizQuestionDraft(
                question_id=f"quiz_question_draft_{index + 1:03d}",
                question="Quale affermazione è supportata dal documento?",
                options=options,
                correct_option_id=correct_option_id,
                explanation_draft=correct_fact,
                source_facts=[correct_fact],
                source_pages=pages if cfg.include_source_pages else [],
            )

            if len(options) != 4:
                question.warnings.append("QUIZ_DRAFT_OPTIONS_COUNT_NOT_4")

            quiz.append(question)

        return quiz

    except Exception:
        return quiz


def build_study_pack_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> StudyPackDraft:
    """
    Costruisce bozza study pack.

    Usa le section_blocks della REDUCE.
    Non produce ancora testo finale da libro bianco.
    """

    cfg = config or OutputBuilderConfig()

    draft = StudyPackDraft(
        title="Bozza study pack macro-grezzo",
    )

    try:
        sections = list(getattr(macro_document, "section_blocks", []) or [])

        for index, section in enumerate(sections[: max(0, cfg.max_study_pack_sections)], start=1):
            section_draft = StudyPackSectionDraft(
                section_id=normalize_text(getattr(section, "section_id", "")) or f"study_pack_section_{index:03d}",
                title=normalize_text(getattr(section, "title", "")) or f"Sezione bozza {index}",
                key_facts=[
                    output_trim_text(fact, cfg.max_fact_chars)
                    for fact in reduce_unique_strings(getattr(section, "facts", []) or [])
                ],
                micro_concepts=reduce_unique_strings(getattr(section, "micro_concepts", []) or []),
                entities=reduce_unique_strings(getattr(section, "entities", []) or []),
                source_pages=list(getattr(section, "source_pages", []) or []) if cfg.include_source_pages else [],
            )

            if not section_draft.key_facts:
                section_draft.warnings.append("STUDY_PACK_SECTION_NO_FACTS")

            draft.sections.append(section_draft)

        draft.global_micro_concepts = output_get_global_concepts(macro_document)
        draft.global_entities = output_get_global_entities(macro_document)

        if not draft.sections:
            draft.warnings.append("STUDY_PACK_DRAFT_NO_SECTIONS")

        return draft

    except Exception as exc:
        draft.warnings.append(f"STUDY_PACK_DRAFT_EXCEPTION: {type(exc).__name__}: {exc}")
        return draft


def build_output_drafts(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> OutputBuilderResult:
    """
    Funzione madre Fase 3 — OUTPUT BUILDER.

    Input:
    - MacroRawDocument prodotto da REDUCE

    Output:
    - OutputBuilderResult con bozze strutturate

    Questa funzione non chiama LLM.
    È deterministica e protetta.
    """

    cfg = config or OutputBuilderConfig()

    result = OutputBuilderResult(
        document_id=normalize_text(getattr(macro_document, "document_id", "")) or "unknown_document",
    )

    try:
        facts = output_get_global_facts(macro_document)
        sections = list(getattr(macro_document, "section_blocks", []) or [])

        result.input_global_facts_count = len(facts)
        result.input_sections_count = len(sections)

        if not facts:
            result.warnings.append("OUTPUT_BUILDER_NO_GLOBAL_FACTS")

        if not sections:
            result.warnings.append("OUTPUT_BUILDER_NO_SECTION_BLOCKS")

        result.summary_draft = build_summary_draft(macro_document, cfg)
        result.cards_draft = build_cards_draft(macro_document, cfg)
        result.study_questions_draft = build_study_questions_draft(macro_document, cfg)
        result.quiz_draft = build_quiz_draft(macro_document, cfg)
        result.study_pack_draft = build_study_pack_draft(macro_document, cfg)

        if not result.cards_draft:
            result.warnings.append("OUTPUT_BUILDER_NO_CARDS_DRAFT")

        if not result.study_questions_draft:
            result.warnings.append("OUTPUT_BUILDER_NO_STUDY_QUESTIONS_DRAFT")

        if not result.quiz_draft:
            result.warnings.append("OUTPUT_BUILDER_NO_QUIZ_DRAFT")

        return result

    except Exception as exc:
        result.errors.append(f"OUTPUT_BUILDER_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def output_builder_result_to_dict(result: OutputBuilderResult) -> Dict[str, Any]:
    """
    Serializza OutputBuilderResult in dict.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "OUTPUT_BUILDER",
            "errors": ["OUTPUT_BUILDER_RESULT_SERIALIZATION_FAILED"],
        }


def output_builder_result_to_json(result: OutputBuilderResult, indent: int = 2) -> str:
    """
    Serializza OutputBuilderResult in JSON.
    """

    try:
        return json.dumps(
            output_builder_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "OUTPUT_BUILDER",
                "errors": [
                    f"OUTPUT_BUILDER_JSON_SERIALIZATION_FAILED: {type(exc).__name__}: {exc}"
                ],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 3 — OUTPUT BUILDER V1
# =============================================================================



# =============================================================================
# FASE 4 — SUPER QUALITY GATE V1
# RAG GERARCHICO MAP-REDUCE AD ALBERO
#
# Obiettivo:
# - prendere le bozze della Fase 3 OUTPUT BUILDER
# - verificare qualità, sicurezza, fallback/demo, ripetizioni e quiz
# - produrre un pacchetto pulito o marcare/bloccare le aree non pronte
#
# Questa fase NON deve:
# - toccare UI/CSS/pulsanti
# - inventare contenuto nuovo
# - aggiungere fatti non presenti nelle bozze
# - trasformare quiz grezzi in quiz finali se i distrattori non sono validi
# =============================================================================


@dataclass
class SuperQualityGateConfig:
    """
    Configurazione universale Fase 4.

    Tutti i controlli sono parametrici.
    Nessun valore è specifico di un singolo documento.
    """

    min_summary_points: int = 1
    min_cards: int = 1
    min_study_questions: int = 1
    min_study_pack_sections: int = 1
    expected_quiz_options: int = 4

    block_on_forbidden_signatures: bool = True
    block_on_quiz_all_source_facts: bool = True
    warn_on_mechanical_phrases: bool = True
    warn_on_duplicate_ratio_above: float = 0.35

    mechanical_phrases: List[str] = field(default_factory=lambda: [
        "in sintesi",
        "in conclusione",
        "il documento parla",
        "il documento tratta",
        "questo testo",
        "questo chunk",
        "tema principale",
        "aspetti importanti",
        "riassunto",
        "qual è",
        "quale regola o informazione emerge da",
        "quale affermazione è supportata dal documento",
    ])

    extra_forbidden_signatures: List[str] = field(default_factory=lambda: [
        "contenuto demo",
        "documento di esempio",
        "testo di esempio",
        "fallback",
        "lorem ipsum",
        "knowledge_base_json",
        "sicurezza informatica aziendale",
    ])


@dataclass
class QualityIssue:
    """
    Problema rilevato dal Super Quality Gate.

    severity:
    - warning: problema da rifinire
    - error: problema serio ma non necessariamente bloccante globale
    - blocker: area non pronta per output finale
    """

    issue_id: str
    severity: str
    area: str
    message: str
    evidence: str = ""


@dataclass
class SuperQualityGateResult:
    """
    Output Fase 4.

    approved:
    - True solo se non ci sono blocker né errori critici.
    """

    document_id: str
    phase_name: str = "SUPER_QUALITY_GATE"
    approved: bool = False
    status: str = "PENDING"

    issues: List[QualityIssue] = field(default_factory=list)
    blocked_areas: List[str] = field(default_factory=list)

    clean_output: Dict[str, Any] = field(default_factory=dict)
    quality_report: Dict[str, Any] = field(default_factory=dict)

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def qg_make_issue(
    issue_id: str,
    severity: str,
    area: str,
    message: str,
    evidence: str = "",
) -> QualityIssue:
    """
    Crea un problema qualità normalizzato.
    """

    try:
        return QualityIssue(
            issue_id=normalize_text(issue_id) or "QUALITY_ISSUE",
            severity=normalize_text(severity) or "warning",
            area=normalize_text(area) or "global",
            message=normalize_text(message) or "Problema qualità rilevato.",
            evidence=output_trim_text(evidence, 400) if "output_trim_text" in globals() else normalize_text(evidence),
        )
    except Exception:
        return QualityIssue(
            issue_id="QUALITY_ISSUE_BUILD_FAILED",
            severity="warning",
            area="global",
            message="Errore durante la costruzione di un issue qualità.",
            evidence="",
        )


def qg_normalize_for_compare(text: Any) -> str:
    """
    Normalizzazione prudente per confronti qualità.
    """

    try:
        value = normalize_text(text).lower()
        value = re.sub(r"[^\w\sàèéìòù]", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"\s+", " ", value).strip()
        return value
    except Exception:
        return ""


def qg_find_forbidden(text: Any, config: SuperQualityGateConfig) -> List[str]:
    """
    Trova firme demo/fallback/preconfezionate.
    """

    found: List[str] = []

    try:
        value = normalize_text(text)
        lowered = value.lower()

        try:
            found.extend(find_forbidden_signatures(value))
        except Exception:
            pass

        for signature in config.extra_forbidden_signatures:
            sig = normalize_text(signature)
            if sig and sig.lower() in lowered:
                found.append(sig)

        return reduce_unique_strings(found)

    except Exception:
        return found


def qg_find_mechanical_phrases(text: Any, config: SuperQualityGateConfig) -> List[str]:
    """
    Trova formule meccaniche o da bozza grezza.
    """

    found: List[str] = []

    try:
        lowered = normalize_text(text).lower()

        for phrase in config.mechanical_phrases:
            clean_phrase = normalize_text(phrase).lower()
            if clean_phrase and clean_phrase in lowered:
                found.append(clean_phrase)

        return reduce_unique_strings(found)

    except Exception:
        return found


def qg_duplicate_ratio(texts: List[str]) -> float:
    """
    Calcola rapporto duplicati.

    0.0 = nessun duplicato.
    1.0 = tutto duplicato.
    """

    try:
        cleaned = [
            qg_normalize_for_compare(text)
            for text in texts
            if qg_normalize_for_compare(text)
        ]

        if not cleaned:
            return 0.0

        unique_count = len(set(cleaned))
        duplicate_count = max(0, len(cleaned) - unique_count)
        return duplicate_count / max(1, len(cleaned))

    except Exception:
        return 0.0


def qg_validate_text_block(
    area: str,
    text: Any,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Controllo qualità base su un testo.
    """

    issues: List[QualityIssue] = []

    try:
        clean_text = normalize_text(text)

        if not clean_text:
            issues.append(
                qg_make_issue(
                    issue_id="EMPTY_TEXT_BLOCK",
                    severity="error",
                    area=area,
                    message="Blocco testuale vuoto.",
                )
            )
            return issues

        forbidden = qg_find_forbidden(clean_text, config)
        if forbidden:
            issues.append(
                qg_make_issue(
                    issue_id="FORBIDDEN_SIGNATURE_FOUND",
                    severity="blocker" if config.block_on_forbidden_signatures else "error",
                    area=area,
                    message="Rilevate firme demo/fallback/preconfezionate.",
                    evidence=", ".join(forbidden),
                )
            )

        if config.warn_on_mechanical_phrases:
            mechanical = qg_find_mechanical_phrases(clean_text, config)
            if mechanical:
                issues.append(
                    qg_make_issue(
                        issue_id="MECHANICAL_PHRASE_FOUND",
                        severity="warning",
                        area=area,
                        message="Rilevata formula meccanica o da bozza grezza.",
                        evidence=", ".join(mechanical),
                    )
                )

        return issues

    except Exception as exc:
        issues.append(
            qg_make_issue(
                issue_id="TEXT_BLOCK_VALIDATION_EXCEPTION",
                severity="error",
                area=area,
                message=f"Errore controllo testo: {type(exc).__name__}: {exc}",
            )
        )
        return issues


def qg_collect_source_facts(output_result: OutputBuilderResult) -> List[str]:
    """
    Raccoglie tutti i facts presenti nelle bozze.

    Serve a capire se un quiz usa come distrattori affermazioni vere.
    """

    facts: List[str] = []

    try:
        summary = getattr(output_result, "summary_draft", None)
        if summary is not None:
            facts.extend(getattr(summary, "key_points", []) or [])

        for card in getattr(output_result, "cards_draft", []) or []:
            facts.extend(getattr(card, "source_facts", []) or [])
            message = normalize_text(getattr(card, "message_key", ""))
            if message:
                facts.append(message)

        for question in getattr(output_result, "study_questions_draft", []) or []:
            answer = normalize_text(getattr(question, "answer_guide", ""))
            if answer:
                facts.append(answer)
            facts.extend(getattr(question, "source_facts", []) or [])

        pack = getattr(output_result, "study_pack_draft", None)
        if pack is not None:
            for section in getattr(pack, "sections", []) or []:
                facts.extend(getattr(section, "key_facts", []) or [])

        return reduce_unique_strings(facts)

    except Exception:
        return reduce_unique_strings(facts)


def qg_validate_summary(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida summary_draft.
    """

    issues: List[QualityIssue] = []

    try:
        summary = getattr(output_result, "summary_draft", None)

        if summary is None:
            return [
                qg_make_issue(
                    issue_id="SUMMARY_DRAFT_MISSING",
                    severity="blocker",
                    area="summary",
                    message="summary_draft mancante.",
                )
            ]

        points = list(getattr(summary, "key_points", []) or [])

        if len(points) < config.min_summary_points:
            issues.append(
                qg_make_issue(
                    issue_id="SUMMARY_TOO_SHORT",
                    severity="error",
                    area="summary",
                    message="Il riassunto bozza ha troppo pochi punti chiave.",
                    evidence=f"points={len(points)}",
                )
            )

        for index, point in enumerate(points, start=1):
            issues.extend(
                qg_validate_text_block(
                    area=f"summary.point_{index}",
                    text=point,
                    config=config,
                )
            )

        ratio = qg_duplicate_ratio(points)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="SUMMARY_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="summary",
                    message="Rapporto duplicati alto nel riassunto bozza.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="SUMMARY_VALIDATION_EXCEPTION",
                severity="error",
                area="summary",
                message=f"Errore validazione summary: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_cards(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida cards_draft.
    """

    issues: List[QualityIssue] = []

    try:
        cards = list(getattr(output_result, "cards_draft", []) or [])

        if len(cards) < config.min_cards:
            issues.append(
                qg_make_issue(
                    issue_id="CARDS_DRAFT_MISSING_OR_TOO_SHORT",
                    severity="error",
                    area="cards",
                    message="cards_draft mancante o troppo corto.",
                    evidence=f"cards={len(cards)}",
                )
            )

        messages: List[str] = []

        for index, card in enumerate(cards, start=1):
            title = normalize_text(getattr(card, "title", ""))
            message_key = normalize_text(getattr(card, "message_key", ""))
            messages.append(message_key)

            issues.extend(qg_validate_text_block(f"cards.card_{index}.title", title, config))
            issues.extend(qg_validate_text_block(f"cards.card_{index}.message_key", message_key, config))

            for fact_index, fact in enumerate(getattr(card, "source_facts", []) or [], start=1):
                issues.extend(
                    qg_validate_text_block(
                        f"cards.card_{index}.source_fact_{fact_index}",
                        fact,
                        config,
                    )
                )

        ratio = qg_duplicate_ratio(messages)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="CARDS_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="cards",
                    message="Rapporto duplicati alto nelle card bozza.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="CARDS_VALIDATION_EXCEPTION",
                severity="error",
                area="cards",
                message=f"Errore validazione cards: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_study_questions(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida study_questions_draft.
    """

    issues: List[QualityIssue] = []

    try:
        questions = list(getattr(output_result, "study_questions_draft", []) or [])

        if len(questions) < config.min_study_questions:
            issues.append(
                qg_make_issue(
                    issue_id="STUDY_QUESTIONS_MISSING_OR_TOO_SHORT",
                    severity="error",
                    area="study_questions",
                    message="Domande studio mancanti o troppo poche.",
                    evidence=f"questions={len(questions)}",
                )
            )

        question_texts: List[str] = []

        for index, question in enumerate(questions, start=1):
            question_text = normalize_text(getattr(question, "question", ""))
            answer_guide = normalize_text(getattr(question, "answer_guide", ""))

            question_texts.append(question_text)

            issues.extend(
                qg_validate_text_block(
                    f"study_questions.question_{index}.question",
                    question_text,
                    config,
                )
            )
            issues.extend(
                qg_validate_text_block(
                    f"study_questions.question_{index}.answer_guide",
                    answer_guide,
                    config,
                )
            )

        ratio = qg_duplicate_ratio(question_texts)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="STUDY_QUESTIONS_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="study_questions",
                    message="Rapporto duplicati alto nelle domande studio.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="STUDY_QUESTIONS_VALIDATION_EXCEPTION",
                severity="error",
                area="study_questions",
                message=f"Errore validazione domande studio: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_quiz(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida quiz_draft.

    Controllo fondamentale:
    se i distrattori sono facts reali del documento, il quiz non è finale.
    """

    issues: List[QualityIssue] = []

    try:
        quiz = list(getattr(output_result, "quiz_draft", []) or [])
        source_facts = qg_collect_source_facts(output_result)
        source_fact_keys = set(qg_normalize_for_compare(fact) for fact in source_facts)

        if not quiz:
            issues.append(
                qg_make_issue(
                    issue_id="QUIZ_DRAFT_MISSING",
                    severity="warning",
                    area="quiz",
                    message="quiz_draft mancante. Può essere accettabile se il documento non contiene abbastanza facts.",
                )
            )
            return issues

        question_texts: List[str] = []

        for index, quiz_question in enumerate(quiz, start=1):
            area_prefix = f"quiz.question_{index}"
            question_text = normalize_text(getattr(quiz_question, "question", ""))
            options = list(getattr(quiz_question, "options", []) or [])
            correct_option_id = normalize_text(getattr(quiz_question, "correct_option_id", ""))

            question_texts.append(question_text)

            issues.extend(qg_validate_text_block(f"{area_prefix}.question", question_text, config))

            if len(options) != config.expected_quiz_options:
                issues.append(
                    qg_make_issue(
                        issue_id="QUIZ_OPTIONS_COUNT_INVALID",
                        severity="blocker",
                        area="quiz",
                        message="Numero opzioni quiz non valido.",
                        evidence=f"question={index} options={len(options)} expected={config.expected_quiz_options}",
                    )
                )

            correct_options = [
                option for option in options
                if bool(getattr(option, "is_correct", False))
            ]

            if len(correct_options) != 1:
                issues.append(
                    qg_make_issue(
                        issue_id="QUIZ_CORRECT_OPTION_COUNT_INVALID",
                        severity="blocker",
                        area="quiz",
                        message="Ogni domanda quiz deve avere esattamente una risposta corretta.",
                        evidence=f"question={index} correct_options={len(correct_options)}",
                    )
                )

            if correct_options:
                expected_correct_id = normalize_text(getattr(correct_options[0], "option_id", ""))
                if correct_option_id and correct_option_id != expected_correct_id:
                    issues.append(
                        qg_make_issue(
                            issue_id="QUIZ_CORRECT_OPTION_ID_MISMATCH",
                            severity="blocker",
                            area="quiz",
                            message="correct_option_id non coincide con l'opzione marcata corretta.",
                            evidence=f"question={index} correct_option_id={correct_option_id} expected={expected_correct_id}",
                        )
                    )

            non_correct_options = [
                option for option in options
                if not bool(getattr(option, "is_correct", False))
            ]

            non_correct_source_fact_count = 0

            for option_index, option in enumerate(options, start=1):
                option_text = normalize_text(getattr(option, "text", ""))
                issues.extend(
                    qg_validate_text_block(
                        f"{area_prefix}.option_{option_index}",
                        option_text,
                        config,
                    )
                )

                if not bool(getattr(option, "is_correct", False)):
                    option_key = qg_normalize_for_compare(option_text)
                    if option_key and option_key in source_fact_keys:
                        non_correct_source_fact_count += 1

            if (
                config.block_on_quiz_all_source_facts
                and non_correct_options
                and non_correct_source_fact_count == len(non_correct_options)
            ):
                issues.append(
                    qg_make_issue(
                        issue_id="QUIZ_DISTRACTORS_ARE_SOURCE_FACTS",
                        severity="blocker",
                        area="quiz",
                        message=(
                            "I distrattori risultano fatti veri presenti nel documento. "
                            "La bozza quiz non è valida come quiz finale."
                        ),
                        evidence=f"question={index} distractors_true={non_correct_source_fact_count}/{len(non_correct_options)}",
                    )
                )

        ratio = qg_duplicate_ratio(question_texts)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="QUIZ_QUESTIONS_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="quiz",
                    message="Domande quiz troppo ripetitive.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="QUIZ_VALIDATION_EXCEPTION",
                severity="error",
                area="quiz",
                message=f"Errore validazione quiz: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_study_pack(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida study_pack_draft.
    """

    issues: List[QualityIssue] = []

    try:
        pack = getattr(output_result, "study_pack_draft", None)

        if pack is None:
            return [
                qg_make_issue(
                    issue_id="STUDY_PACK_DRAFT_MISSING",
                    severity="error",
                    area="study_pack",
                    message="study_pack_draft mancante.",
                )
            ]

        sections = list(getattr(pack, "sections", []) or [])

        if len(sections) < config.min_study_pack_sections:
            issues.append(
                qg_make_issue(
                    issue_id="STUDY_PACK_SECTIONS_TOO_SHORT",
                    severity="error",
                    area="study_pack",
                    message="Study pack con troppe poche sezioni.",
                    evidence=f"sections={len(sections)}",
                )
            )

        for section_index, section in enumerate(sections, start=1):
            title = normalize_text(getattr(section, "title", ""))
            issues.extend(
                qg_validate_text_block(
                    f"study_pack.section_{section_index}.title",
                    title,
                    config,
                )
            )

            for fact_index, fact in enumerate(getattr(section, "key_facts", []) or [], start=1):
                issues.extend(
                    qg_validate_text_block(
                        f"study_pack.section_{section_index}.fact_{fact_index}",
                        fact,
                        config,
                    )
                )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="STUDY_PACK_VALIDATION_EXCEPTION",
                severity="error",
                area="study_pack",
                message=f"Errore validazione study pack: {type(exc).__name__}: {exc}",
            )
        ]


def qg_clean_output_bundle(output_result: OutputBuilderResult) -> Dict[str, Any]:
    """
    Crea pacchetto pulito ma ancora strutturato.

    Non riscrive i contenuti.
    Pulisce solo spazi, serializza e conserva struttura.
    """

    clean: Dict[str, Any] = {}

    try:
        summary = getattr(output_result, "summary_draft", None)
        if summary is not None:
            clean["summary"] = {
                "title": normalize_text(getattr(summary, "title", "")),
                "key_points": [
                    normalize_text(point)
                    for point in getattr(summary, "key_points", []) or []
                    if normalize_text(point)
                ],
                "source_pages": list(getattr(summary, "source_pages", []) or []),
            }

        clean["cards"] = []
        for card in getattr(output_result, "cards_draft", []) or []:
            clean["cards"].append(
                {
                    "card_id": normalize_text(getattr(card, "card_id", "")),
                    "title": normalize_text(getattr(card, "title", "")),
                    "message_key": normalize_text(getattr(card, "message_key", "")),
                    "source_facts": [
                        normalize_text(fact)
                        for fact in getattr(card, "source_facts", []) or []
                        if normalize_text(fact)
                    ],
                    "micro_concepts": [
                        normalize_text(concept)
                        for concept in getattr(card, "micro_concepts", []) or []
                        if normalize_text(concept)
                    ],
                    "source_pages": list(getattr(card, "source_pages", []) or []),
                }
            )

        clean["study_questions"] = []
        for question in getattr(output_result, "study_questions_draft", []) or []:
            clean["study_questions"].append(
                {
                    "question_id": normalize_text(getattr(question, "question_id", "")),
                    "question": normalize_text(getattr(question, "question", "")),
                    "answer_guide": normalize_text(getattr(question, "answer_guide", "")),
                    "source_facts": [
                        normalize_text(fact)
                        for fact in getattr(question, "source_facts", []) or []
                        if normalize_text(fact)
                    ],
                    "source_pages": list(getattr(question, "source_pages", []) or []),
                }
            )

        clean["quiz"] = []
        for quiz_question in getattr(output_result, "quiz_draft", []) or []:
            clean["quiz"].append(
                {
                    "question_id": normalize_text(getattr(quiz_question, "question_id", "")),
                    "question": normalize_text(getattr(quiz_question, "question", "")),
                    "options": [
                        {
                            "option_id": normalize_text(getattr(option, "option_id", "")),
                            "text": normalize_text(getattr(option, "text", "")),
                            "is_correct": bool(getattr(option, "is_correct", False)),
                        }
                        for option in getattr(quiz_question, "options", []) or []
                    ],
                    "correct_option_id": normalize_text(getattr(quiz_question, "correct_option_id", "")),
                    "explanation_draft": normalize_text(getattr(quiz_question, "explanation_draft", "")),
                    "source_pages": list(getattr(quiz_question, "source_pages", []) or []),
                }
            )

        pack = getattr(output_result, "study_pack_draft", None)
        if pack is not None:
            clean["study_pack"] = {
                "title": normalize_text(getattr(pack, "title", "")),
                "sections": [
                    {
                        "section_id": normalize_text(getattr(section, "section_id", "")),
                        "title": normalize_text(getattr(section, "title", "")),
                        "key_facts": [
                            normalize_text(fact)
                            for fact in getattr(section, "key_facts", []) or []
                            if normalize_text(fact)
                        ],
                        "micro_concepts": [
                            normalize_text(concept)
                            for concept in getattr(section, "micro_concepts", []) or []
                            if normalize_text(concept)
                        ],
                        "entities": [
                            normalize_text(entity)
                            for entity in getattr(section, "entities", []) or []
                            if normalize_text(entity)
                        ],
                        "source_pages": list(getattr(section, "source_pages", []) or []),
                    }
                    for section in getattr(pack, "sections", []) or []
                ],
                "global_micro_concepts": [
                    normalize_text(concept)
                    for concept in getattr(pack, "global_micro_concepts", []) or []
                    if normalize_text(concept)
                ],
                "global_entities": [
                    normalize_text(entity)
                    for entity in getattr(pack, "global_entities", []) or []
                    if normalize_text(entity)
                ],
            }

        return clean

    except Exception as exc:
        return {
            "clean_output_error": f"{type(exc).__name__}: {exc}"
        }


def run_super_quality_gate(
    output_result: OutputBuilderResult,
    config: Optional[SuperQualityGateConfig] = None,
) -> SuperQualityGateResult:
    """
    Funzione madre Fase 4 — SUPER QUALITY GATE.

    Input:
    - OutputBuilderResult della Fase 3

    Output:
    - SuperQualityGateResult con:
      - approved/status
      - issues
      - blocked_areas
      - clean_output
      - quality_report
    """

    cfg = config or SuperQualityGateConfig()

    result = SuperQualityGateResult(
        document_id=normalize_text(getattr(output_result, "document_id", "")) or "unknown_document",
    )

    try:
        issues: List[QualityIssue] = []

        issues.extend(qg_validate_summary(output_result, cfg))
        issues.extend(qg_validate_cards(output_result, cfg))
        issues.extend(qg_validate_study_questions(output_result, cfg))
        issues.extend(qg_validate_quiz(output_result, cfg))
        issues.extend(qg_validate_study_pack(output_result, cfg))

        result.issues = issues

        blockers = [issue for issue in issues if issue.severity == "blocker"]
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]

        result.blocked_areas = reduce_unique_strings(
            [issue.area.split(".")[0] for issue in blockers]
        )

        result.clean_output = qg_clean_output_bundle(output_result)

        result.quality_report = {
            "issues_count": len(issues),
            "blockers_count": len(blockers),
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "blocked_areas": list(result.blocked_areas),
            "summary_points": len(result.clean_output.get("summary", {}).get("key_points", [])),
            "cards_count": len(result.clean_output.get("cards", [])),
            "study_questions_count": len(result.clean_output.get("study_questions", [])),
            "quiz_questions_count": len(result.clean_output.get("quiz", [])),
            "study_pack_sections_count": len(result.clean_output.get("study_pack", {}).get("sections", [])),
        }

        if blockers:
            result.status = "BLOCKED"
            result.approved = False
        elif errors:
            result.status = "NEEDS_REVIEW"
            result.approved = False
        else:
            result.status = "APPROVED"
            result.approved = True

        return result

    except Exception as exc:
        result.status = "ERROR"
        result.approved = False
        result.errors.append(f"SUPER_QUALITY_GATE_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def super_quality_gate_result_to_dict(result: SuperQualityGateResult) -> Dict[str, Any]:
    """
    Serializza SuperQualityGateResult in dict.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "SUPER_QUALITY_GATE",
            "approved": False,
            "status": "SERIALIZATION_ERROR",
            "errors": ["SUPER_QUALITY_GATE_RESULT_SERIALIZATION_FAILED"],
        }


def super_quality_gate_result_to_json(result: SuperQualityGateResult, indent: int = 2) -> str:
    """
    Serializza SuperQualityGateResult in JSON.
    """

    try:
        return json.dumps(
            super_quality_gate_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "SUPER_QUALITY_GATE",
                "approved": False,
                "status": "JSON_SERIALIZATION_ERROR",
                "errors": [
                    f"SUPER_QUALITY_GATE_JSON_SERIALIZATION_FAILED: {type(exc).__name__}: {exc}"
                ],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 4 — SUPER QUALITY GATE V1
# =============================================================================



# =============================================================================
# FASE 5 — QUALITY SUMMARY CARDS V1
#
# Pipeline definitiva:
# Estrai → Consolida → Crea bozze → Controlla → Genera qualità
#
# Questa fase prende l'output pulito della Fase 4:
# - SuperQualityGateResult.clean_output
#
# E produce:
# - riassunto narrativo fluido
# - card concettuali strutturate come oggetti JSON
#
# Divieti:
# - non tocca UI/CSS/pulsanti/layout
# - non modifica le Fasi 1–4
# - non inventa fatti esterni
# - non usa fallback/demo
# =============================================================================


@dataclass
class Phase5QualityConfig:
    """
    Configurazione universale Fase 5.

    Tutto è parametrico:
    nessun valore è legato a un documento specifico.
    """

    max_summary_points: int = 24
    facts_per_paragraph: int = 3
    max_cards: int = 12
    max_card_facts: int = 3
    max_micro_concepts_per_card: int = 6
    max_fact_chars: int = 700
    require_phase4_summary_cards_not_blocked: bool = True


@dataclass
class QualitySummaryFinal:
    """
    Riassunto finale di qualità.

    Non è una lista meccanica.
    È testo narrativo diviso in paragrafi.
    """

    titolo: str
    paragrafi: List[str] = field(default_factory=list)
    testo_completo: str = ""
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ConceptCardFinal:
    """
    Card concettuale finale come struttura dati.

    Non contiene UI.
    Non contiene CSS.
    Non contiene layout.
    """

    card_id: str
    titolo: str
    contenuto_esplicativo: str
    micro_concetti: List[str] = field(default_factory=list)
    colore_categoria: str = "#64748B"
    dominio_rilevato: str = "general"
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Phase5QualitySummaryCardsResult:
    """
    Output complessivo Fase 5 per riassunto + card.
    """

    document_id: str
    phase_name: str = "QUALITY_SUMMARY_CARDS"
    approved: bool = False
    status: str = "PENDING"

    riassunto_qualita: Optional[QualitySummaryFinal] = None
    card_concettuali: List[ConceptCardFinal] = field(default_factory=list)

    quality_report: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def q5_safe_text(value: Any) -> str:
    """
    Normalizzazione base protetta.
    """

    try:
        if "normalize_text" in globals():
            return normalize_text(value)
        return str(value or "").strip()
    except Exception:
        return ""


def q5_sentence(value: Any) -> str:
    """
    Restituisce una frase con punteggiatura finale.
    """

    try:
        text = q5_fix_italian_typography(q5_safe_text(value))
        text = text.strip()

        if not text:
            return ""

        if text[-1] not in ".!?":
            text += "."

        return text

    except Exception:
        return ""


def q5_limit_text(value: Any, max_chars: int = 700) -> str:
    """
    Limita testo troppo lungo senza spezzare l'intero sistema.
    """

    try:
        text = q5_safe_text(value)

        if max_chars <= 0 or len(text) <= max_chars:
            return text

        return text[:max_chars].rstrip() + "..."

    except Exception:
        return ""


def q5_unique_strings(values: Sequence[Any]) -> List[str]:
    """
    Deduplica prudente mantenendo ordine.
    """

    try:
        if "reduce_unique_strings" in globals():
            return reduce_unique_strings(values)

        output: List[str] = []
        seen = set()

        for value in values:
            text = q5_safe_text(value)
            key = text.lower()

            if text and key not in seen:
                seen.add(key)
                output.append(text)

        return output

    except Exception:
        return []


def q5_fix_italian_typography(text: Any) -> str:
    """
    Controllo tipografico rigido.

    Corregge:
    - doppi spazi
    - spazi prima della punteggiatura
    - apostrofi separati
    - e' / e'' → è
    - perche → perché
    - accenti comuni mancanti
    - sì affermativo in casi conservativi

    Nota:
    la correzione di "si" è volutamente prudente per non rompere
    il pronome impersonale "si" in frasi tipo "si deve fare".
    """

    try:
        value = q5_safe_text(text)

        if not value:
            return ""

        # Normalizza apostrofi strani.
        value = (
            value.replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
            .replace("´", "'")
        )

        # e' / e'' → è
        value = re.sub(
            r"(?<!\w)[eE]['\"]{1,2}(?!\w)",
            lambda m: "È" if m.group(0).startswith("E") else "è",
            value,
        )

        # Apostrofi italiani separati: l ' accesso → l'accesso
        value = re.sub(
            r"\b([lLdDaAuUnN])\s+'\s*",
            lambda m: m.group(1) + "'",
            value,
        )

        accent_map = {
            "perche": "perché",
            "perchè": "perché",
            "poiche": "poiché",
            "poichè": "poiché",
            "affinche": "affinché",
            "affinchè": "affinché",
            "benche": "benché",
            "benchè": "benché",
            "finche": "finché",
            "finchè": "finché",
            "cosi": "così",
            "piu": "più",
            "gia": "già",
            "puo": "può",
            "cio": "ciò",
            "pero": "però",
        }

        for wrong, right in accent_map.items():
            value = re.sub(
                rf"\b{wrong}\b",
                right,
                value,
                flags=re.IGNORECASE,
            )

        # Sì affermativo solo se seguito da punteggiatura o fine frase.
        value = re.sub(
            r"(?<!\w)([sS])i(?=\s*[,!.?;:]|\s*$)",
            lambda m: "Sì" if m.group(1).isupper() else "sì",
            value,
        )

        # Spazi prima della punteggiatura.
        value = re.sub(r"\s+([,.;:!?])", r"\1", value)

        # Spazio dopo punteggiatura, se manca.
        value = re.sub(r"([,.;:!?])(?=[^\s\]\)\}])", r"\1 ", value)

        # Doppi spazi.
        value = re.sub(r"\s+", " ", value).strip()

        return value

    except Exception:
        return q5_safe_text(text)


def q5_lower_first(text: str) -> str:
    """
    Abbassa solo la prima lettera per collegare frasi in modo narrativo.
    """

    try:
        clean = q5_safe_text(text)
        if not clean:
            return ""
        return clean[:1].lower() + clean[1:]
    except Exception:
        return q5_safe_text(text)


def q5_extract_pages_from_gate(gate_result: SuperQualityGateResult) -> List[int]:
    """
    Estrae pagine dal clean_output della Fase 4.
    """

    pages: List[int] = []

    try:
        clean = getattr(gate_result, "clean_output", {}) or {}

        def add_pages(raw_pages: Any) -> None:
            try:
                for page in raw_pages or []:
                    try:
                        pages.append(int(page))
                    except Exception:
                        pass
            except Exception:
                pass

        summary = clean.get("summary", {})
        if isinstance(summary, dict):
            add_pages(summary.get("source_pages", []))

        for card in clean.get("cards", []) or []:
            if isinstance(card, dict):
                add_pages(card.get("source_pages", []))

        pack = clean.get("study_pack", {})
        if isinstance(pack, dict):
            for section in pack.get("sections", []) or []:
                if isinstance(section, dict):
                    add_pages(section.get("source_pages", []))

        return sorted(set(pages))

    except Exception:
        return sorted(set(pages))


def q5_extract_facts_from_gate(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
) -> List[str]:
    """
    Estrae facts puliti dalla Fase 4.

    Priorità:
    1. gate_result.clean_output
    2. fallback controllato su OutputBuilderResult
    """

    facts: List[str] = []

    try:
        clean = getattr(gate_result, "clean_output", {}) or {}

        summary = clean.get("summary", {})
        if isinstance(summary, dict):
            facts.extend(summary.get("key_points", []) or [])

        for card in clean.get("cards", []) or []:
            if isinstance(card, dict):
                facts.extend(card.get("source_facts", []) or [])
                message = card.get("message_key")
                if message:
                    facts.append(message)

        pack = clean.get("study_pack", {})
        if isinstance(pack, dict):
            for section in pack.get("sections", []) or []:
                if isinstance(section, dict):
                    facts.extend(section.get("key_facts", []) or [])

        if not facts and output_result is not None:
            try:
                facts.extend(qg_collect_source_facts(output_result))
            except Exception:
                pass

        cleaned = [
            q5_limit_text(q5_fix_italian_typography(fact), 900)
            for fact in facts
            if q5_safe_text(fact)
        ]

        return q5_unique_strings(cleaned)

    except Exception:
        return q5_unique_strings(facts)


def q5_extract_concepts_from_gate(gate_result: SuperQualityGateResult) -> List[str]:
    """
    Estrae micro-concetti già presenti nel clean_output.
    """

    concepts: List[str] = []

    try:
        clean = getattr(gate_result, "clean_output", {}) or {}

        for card in clean.get("cards", []) or []:
            if isinstance(card, dict):
                concepts.extend(card.get("micro_concepts", []) or [])

        pack = clean.get("study_pack", {})
        if isinstance(pack, dict):
            concepts.extend(pack.get("global_micro_concepts", []) or [])
            for section in pack.get("sections", []) or []:
                if isinstance(section, dict):
                    concepts.extend(section.get("micro_concepts", []) or [])

        return q5_unique_strings(
            [
                q5_fix_italian_typography(concept).lower()
                for concept in concepts
                if q5_safe_text(concept)
            ]
        )

    except Exception:
        return q5_unique_strings(concepts)


def q5_stopwords() -> set:
    """
    Stopword minime per estrazione micro-concetti.
    """

    return {
        "il", "lo", "la", "i", "gli", "le",
        "un", "uno", "una",
        "di", "del", "della", "delle", "degli", "dei",
        "a", "ad", "al", "alla", "alle", "agli", "ai",
        "da", "dal", "dalla", "dalle", "dai",
        "in", "nel", "nella", "nelle", "nei", "negli",
        "con", "su", "per", "tra", "fra",
        "e", "o", "ma", "che",
        "deve", "devono", "essere", "viene", "sono",
        "questo", "questa", "questi", "quelle", "quello",
    }


def q5_word_tokens(text: str) -> List[str]:
    """
    Token parole italiane.
    """

    try:
        return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", q5_safe_text(text).lower())
    except Exception:
        return []


def q5_is_valid_micro_concept(concept: str) -> bool:
    """
    Verifica keyword vera di 2-3 parole.
    """

    try:
        clean = q5_safe_text(concept).lower()
        words = clean.split()

        if len(words) < 2 or len(words) > 3:
            return False

        stops = q5_stopwords()

        if words[0] in stops or words[-1] in stops:
            return False

        if all(word in stops for word in words):
            return False

        if len(clean) < 5:
            return False

        return True

    except Exception:
        return False


def q5_generate_micro_concepts_from_text(text: str, limit: int = 6) -> List[str]:
    """
    Genera micro-concetti 2-3 parole dal testo se quelli della MAP non bastano.
    """

    concepts: List[str] = []

    try:
        tokens = q5_word_tokens(text)
        stops = q5_stopwords()

        candidates: List[str] = []

        for size in (2, 3):
            for index in range(0, max(0, len(tokens) - size + 1)):
                gram = tokens[index:index + size]

                if not gram:
                    continue

                if gram[0] in stops or gram[-1] in stops:
                    continue

                if all(token in stops for token in gram):
                    continue

                candidate = " ".join(gram)
                if q5_is_valid_micro_concept(candidate):
                    candidates.append(candidate)

        concepts = q5_unique_strings(candidates)

        return concepts[:limit]

    except Exception:
        return concepts[:limit]


def q5_select_micro_concepts(
    preferred_concepts: List[str],
    text: str,
    limit: int = 6,
) -> List[str]:
    """
    Seleziona micro-concetti veri di 2-3 parole.
    """

    try:
        valid = [
            q5_safe_text(concept).lower()
            for concept in preferred_concepts
            if q5_is_valid_micro_concept(q5_safe_text(concept))
        ]

        if len(valid) < limit:
            valid.extend(q5_generate_micro_concepts_from_text(text, limit=limit))

        return q5_unique_strings(valid)[:limit]

    except Exception:
        return []


def q5_detect_domain_from_text(text: str, concepts: Optional[List[str]] = None) -> str:
    """
    Rileva dominio base per colore categoria.

    È un classificatore leggero, non un motore semantico pesante.
    """

    try:
        joined = " ".join([q5_safe_text(text)] + list(concepts or [])).lower()

        domain_keywords = {
            "cybersecurity": [
                "accessi", "credenziali", "account", "permessi",
                "sistemi interni", "utenti autorizzati", "sicurezza",
                "rischio", "controllo",
            ],
            "business": [
                "azienda", "processo", "cliente", "mercato",
                "strategia", "vendite", "operativo",
            ],
            "legal": [
                "contratto", "normativa", "obbligo", "diritto",
                "responsabilità", "clausola",
            ],
            "education": [
                "studio", "formazione", "apprendimento", "lezione",
                "competenza", "esame",
            ],
            "health": [
                "salute", "paziente", "clinico", "medico",
                "diagnosi", "terapia",
            ],
            "sport": [
                "allenamento", "forza", "resistenza", "gara",
                "atleta", "recupero",
            ],
        }

        scores: Dict[str, int] = {}

        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for keyword in keywords if keyword in joined)

        best_domain = max(scores, key=scores.get)

        if scores.get(best_domain, 0) <= 0:
            return "general"

        return best_domain

    except Exception:
        return "general"


def q5_color_for_domain(domain: str) -> str:
    """
    Colore categoria associato dinamicamente al dominio rilevato.

    È solo dato.
    Non applica grafica.
    Non tocca CSS.
    """

    try:
        palette = {
            "cybersecurity": "#7C3AED",
            "business": "#0F766E",
            "legal": "#B45309",
            "education": "#0891B2",
            "health": "#16A34A",
            "sport": "#EA580C",
            "creative": "#DB2777",
            "technical": "#2563EB",
            "general": "#64748B",
        }

        return palette.get(q5_safe_text(domain).lower(), palette["general"])

    except Exception:
        return "#64748B"


def q5_title_from_text(text: str, fallback: str = "Punto chiave", max_words: int = 7) -> str:
    """
    Titolo breve da testo/concept.
    """

    try:
        clean = q5_fix_italian_typography(text).strip().rstrip(".")
        words = clean.split()

        if not words:
            return fallback

        title = " ".join(words[:max_words])

        if len(words) > max_words:
            title += "..."

        return title[:1].upper() + title[1:]

    except Exception:
        return fallback


def q5_intro_for_fact(fact: str) -> str:
    """
    Introduzione narrativa in base al tipo di fatto.
    """

    try:
        lowered = fact.lower()

        if "non devono" in lowered or "non deve" in lowered or "vietato" in lowered:
            return "Il documento chiarisce un divieto operativo importante:"

        if "riduce il rischio" in lowered or "previene" in lowered:
            return "Un punto rilevante riguarda la riduzione del rischio:"

        if "deve" in lowered or "devono" in lowered or "obbligo" in lowered:
            return "Il testo definisce anche un obbligo operativo:"

        if "controllo" in lowered or "limita" in lowered:
            return "Il documento descrive una funzione di controllo:"

        return "Un altro punto da considerare è questo:"

    except Exception:
        return "Un punto importante è questo:"


def q5_build_fluid_summary_paragraphs(
    facts: List[str],
    config: Phase5QualityConfig,
) -> List[str]:
    """
    Motore di Scrittura Fluida per il riassunto.

    Trasforma punti separati in paragrafi narrativi coerenti.
    Non usa lista meccanica.
    """

    paragraphs: List[str] = []

    try:
        clean_facts = [
            q5_sentence(q5_limit_text(fact, config.max_fact_chars))
            for fact in facts[: max(0, config.max_summary_points)]
            if q5_safe_text(fact)
        ]

        if not clean_facts:
            return paragraphs

        group_size = max(1, int(config.facts_per_paragraph or 1))

        openings = [
            "Il documento evidenzia che",
            "Sul piano operativo emerge che",
            "In continuità con questi elementi, si osserva che",
            "Nel quadro complessivo, risulta importante che",
        ]

        connectors = [
            "Inoltre,",
            "Allo stesso tempo,",
            "Di conseguenza,",
            "Un altro aspetto collegato è che",
        ]

        for group_index in range(0, len(clean_facts), group_size):
            group = clean_facts[group_index:group_index + group_size]
            paragraph_index = len(paragraphs)
            opening = openings[paragraph_index % len(openings)]

            first = q5_lower_first(group[0]).rstrip(".")
            paragraph = f"{opening} {first}."

            for local_index, sentence in enumerate(group[1:], start=1):
                connector = connectors[(local_index - 1) % len(connectors)]
                paragraph += f" {connector} {q5_lower_first(sentence).rstrip('.')}."

            paragraph = q5_fix_italian_typography(paragraph)
            paragraphs.append(paragraph)

        return paragraphs

    except Exception:
        return paragraphs


def q5_build_quality_summary(
    facts: List[str],
    pages: List[int],
    config: Phase5QualityConfig,
) -> QualitySummaryFinal:
    """
    Costruisce il riassunto di qualità.
    """

    summary = QualitySummaryFinal(
        titolo="Riassunto di qualità",
        fonte_pagine=list(pages),
    )

    try:
        paragraphs = q5_build_fluid_summary_paragraphs(facts, config)

        summary.paragrafi = paragraphs
        summary.testo_completo = "\n\n".join(paragraphs)

        if not summary.paragrafi:
            summary.warnings.append("PHASE5_SUMMARY_NO_PARAGRAPHS")

        mechanical_markers = [
            "quale affermazione è supportata dal documento",
            "quale regola o informazione emerge da",
        ]

        lowered = summary.testo_completo.lower()
        for marker in mechanical_markers:
            if marker in lowered:
                summary.warnings.append(f"PHASE5_SUMMARY_MECHANICAL_MARKER: {marker}")

        return summary

    except Exception as exc:
        summary.warnings.append(f"PHASE5_SUMMARY_EXCEPTION: {type(exc).__name__}: {exc}")
        return summary


def q5_build_card_content(facts: List[str]) -> str:
    """
    Crea contenuto esplicativo fluido per una card.

    Non è testo compresso.
    Non è lista.
    """

    try:
        clean_facts = [q5_sentence(fact) for fact in facts if q5_safe_text(fact)]

        if not clean_facts:
            return ""

        first_fact = clean_facts[0]
        intro = q5_intro_for_fact(first_fact)

        body = f"{intro} {q5_lower_first(first_fact)}"

        for fact in clean_facts[1:]:
            body += f" Questo elemento si collega anche al fatto che {q5_lower_first(fact).rstrip('.')}."

        return q5_fix_italian_typography(body)

    except Exception:
        return ""


def q5_build_concept_cards(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5QualityConfig,
) -> List[ConceptCardFinal]:
    """
    Costruisce card concettuali come oggetti dati JSON-ready.
    """

    cards: List[ConceptCardFinal] = []

    try:
        if not facts:
            return cards

        max_cards = max(0, config.max_cards)
        max_card_facts = max(1, config.max_card_facts)

        for index in range(0, min(len(facts), max_cards)):
            fact = facts[index]
            related_facts = facts[index:index + max_card_facts]

            text_for_domain = " ".join(related_facts)
            micro_concepts = q5_select_micro_concepts(
                preferred_concepts=preferred_concepts,
                text=text_for_domain,
                limit=config.max_micro_concepts_per_card,
            )

            domain = q5_detect_domain_from_text(text_for_domain, micro_concepts)
            color = q5_color_for_domain(domain)

            title_source = micro_concepts[0] if micro_concepts else fact
            title = q5_title_from_text(title_source, fallback=f"Card concettuale {index + 1}", max_words=5)

            content = q5_build_card_content(related_facts)

            card = ConceptCardFinal(
                card_id=f"phase5_card_{index + 1:03d}",
                titolo=title,
                contenuto_esplicativo=content,
                micro_concetti=micro_concepts,
                colore_categoria=color,
                dominio_rilevato=domain,
                fonte_pagine=list(pages),
            )

            if not card.contenuto_esplicativo:
                card.warnings.append("PHASE5_CARD_EMPTY_CONTENT")

            if not card.micro_concetti:
                card.warnings.append("PHASE5_CARD_NO_MICRO_CONCEPTS")

            invalid_concepts = [
                concept for concept in card.micro_concetti
                if not q5_is_valid_micro_concept(concept)
            ]

            if invalid_concepts:
                card.warnings.append(
                    "PHASE5_CARD_INVALID_MICRO_CONCEPTS: " + ", ".join(invalid_concepts)
                )

            cards.append(card)

        return cards

    except Exception:
        return cards


def q5_validate_phase4_for_summary_cards(
    gate_result: SuperQualityGateResult,
    config: Phase5QualityConfig,
) -> List[str]:
    """
    Verifica che la Fase 4 non abbia bloccato summary/cards.

    Se la Fase 4 è bloccata solo per quiz, questa Fase 5 può comunque
    generare riassunto e card.
    """

    errors: List[str] = []

    try:
        blocked_areas = list(getattr(gate_result, "blocked_areas", []) or [])

        if config.require_phase4_summary_cards_not_blocked:
            if "summary" in blocked_areas:
                errors.append("PHASE5_CANNOT_BUILD_SUMMARY_PHASE4_BLOCKED_SUMMARY")
            if "cards" in blocked_areas:
                errors.append("PHASE5_CANNOT_BUILD_CARDS_PHASE4_BLOCKED_CARDS")

        return errors

    except Exception as exc:
        return [f"PHASE5_PHASE4_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def q5_find_forbidden_in_final_text(text: str) -> List[str]:
    """
    Controlla firme fallback/demo nel testo finale.
    """

    found: List[str] = []

    try:
        if "find_forbidden_signatures" in globals():
            found.extend(find_forbidden_signatures(text))

        extra = [
            "contenuto demo",
            "documento di esempio",
            "testo di esempio",
            "fallback",
            "lorem ipsum",
            "knowledge_base_json",
            "sicurezza informatica aziendale",
        ]

        lowered = q5_safe_text(text).lower()

        for item in extra:
            if item in lowered:
                found.append(item)

        return q5_unique_strings(found)

    except Exception:
        return found


def build_phase5_quality_summary_cards(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
    config: Optional[Phase5QualityConfig] = None,
) -> Phase5QualitySummaryCardsResult:
    """
    Funzione madre Fase 5.

    Collegamento alla Fase 4:
    - legge SuperQualityGateResult.clean_output
    - usa summary/cards/study_pack puliti dalla Fase 4
    - se la Fase 4 ha bloccato summary/cards, non approva
    - se la Fase 4 ha bloccato solo quiz, può produrre summary/cards

    Output:
    - QualitySummaryFinal
    - List[ConceptCardFinal]
    """

    cfg = config or Phase5QualityConfig()

    result = Phase5QualitySummaryCardsResult(
        document_id=q5_safe_text(getattr(gate_result, "document_id", "")) or "unknown_document",
    )

    try:
        result.errors.extend(q5_validate_phase4_for_summary_cards(gate_result, cfg))

        facts = q5_extract_facts_from_gate(gate_result, output_result)
        concepts = q5_extract_concepts_from_gate(gate_result)
        pages = q5_extract_pages_from_gate(gate_result)

        if not facts:
            result.errors.append("PHASE5_NO_FACTS_AVAILABLE_FROM_PHASE4")

        result.riassunto_qualita = q5_build_quality_summary(facts, pages, cfg)
        result.card_concettuali = q5_build_concept_cards(facts, concepts, pages, cfg)

        final_text_parts: List[str] = []

        if result.riassunto_qualita:
            final_text_parts.append(result.riassunto_qualita.testo_completo)

        for card in result.card_concettuali:
            final_text_parts.append(card.titolo)
            final_text_parts.append(card.contenuto_esplicativo)
            final_text_parts.extend(card.micro_concetti)

        forbidden = q5_find_forbidden_in_final_text("\n".join(final_text_parts))

        if forbidden:
            result.errors.append(
                "PHASE5_FORBIDDEN_SIGNATURES_FOUND: " + ", ".join(forbidden)
            )

        if not result.riassunto_qualita or not result.riassunto_qualita.paragrafi:
            result.errors.append("PHASE5_SUMMARY_EMPTY")

        if not result.card_concettuali:
            result.errors.append("PHASE5_CARDS_EMPTY")

        for card in result.card_concettuali:
            if not card.titolo:
                result.errors.append(f"{card.card_id}: PHASE5_CARD_TITLE_EMPTY")
            if not card.contenuto_esplicativo:
                result.errors.append(f"{card.card_id}: PHASE5_CARD_CONTENT_EMPTY")
            if not card.micro_concetti:
                result.errors.append(f"{card.card_id}: PHASE5_CARD_MICRO_CONCEPTS_EMPTY")
            if not card.colore_categoria.startswith("#"):
                result.errors.append(f"{card.card_id}: PHASE5_CARD_COLOR_INVALID")

        result.quality_report = {
            "facts_used": len(facts),
            "concepts_used": len(concepts),
            "summary_paragraphs": len(result.riassunto_qualita.paragrafi) if result.riassunto_qualita else 0,
            "cards_count": len(result.card_concettuali),
            "source_pages": pages,
            "errors_count": len(result.errors),
            "warnings_count": len(result.warnings),
        }

        if result.errors:
            result.status = "NEEDS_REVIEW"
            result.approved = False
        else:
            result.status = "APPROVED"
            result.approved = True

        return result

    except Exception as exc:
        result.status = "ERROR"
        result.approved = False
        result.errors.append(f"PHASE5_QUALITY_SUMMARY_CARDS_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def phase5_quality_summary_cards_result_to_dict(
    result: Phase5QualitySummaryCardsResult,
) -> Dict[str, Any]:
    """
    Serializza Fase 5 in dict JSON-ready.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "QUALITY_SUMMARY_CARDS",
            "approved": False,
            "status": "SERIALIZATION_ERROR",
            "errors": ["PHASE5_SERIALIZATION_FAILED"],
        }


def phase5_quality_summary_cards_result_to_json(
    result: Phase5QualitySummaryCardsResult,
    indent: int = 2,
) -> str:
    """
    Serializza Fase 5 in JSON.
    """

    try:
        return json.dumps(
            phase5_quality_summary_cards_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "QUALITY_SUMMARY_CARDS",
                "approved": False,
                "status": "JSON_SERIALIZATION_ERROR",
                "errors": [f"PHASE5_JSON_FAILED: {type(exc).__name__}: {exc}"],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 5 — Quality Summary Cards V1
# =============================================================================



# =============================================================================
# FASE 5.1 — MICRO CONCEPTS CARDS QUALITY PATCH
#
# Micro-patch solo Fase 5.
# Migliora:
# - micro_concetti brutti tipo "accessi limita", "credenziali non"
# - titoli card troppo ripetitivi
#
# Non modifica Fasi 1–4.
# Non tocca UI/CSS/pulsanti/layout.
# =============================================================================


def q5_bad_micro_concept_boundary_tokens() -> set:
    return {
        "non",
        "deve",
        "devono",
        "essere",
        "può",
        "possono",
        "limita",
        "limitano",
        "riduce",
        "riducono",
        "aumenta",
        "aumentano",
        "evita",
        "evitano",
        "condivide",
        "condividono",
        "condivise",
        "condivisi",
        "associato",
        "associata",
        "mantengano",
        "mantiene",
        "mantenere",
        "utilizzo",
    }


def q5_domain_micro_concepts_from_text(text: str) -> List[str]:
    concepts: List[str] = []

    try:
        lowered = q5_safe_text(text).lower()

        if "controllo degli accessi" in lowered or "controllo accessi" in lowered:
            concepts.append("controllo accessi")

        if "sistemi interni" in lowered:
            concepts.append("sistemi interni")

        if "account" in lowered:
            concepts.append("account utente")

        if "persona identificabile" in lowered:
            concepts.append("persona identificabile")

        if "credenzial" in lowered:
            concepts.append("protezione credenziali")

        if "non devono essere condivise" in lowered or "non deve essere condivisa" in lowered:
            concepts.append("condivisione credenziali")

        if "revisione periodica" in lowered:
            concepts.append("revisione periodica")

        if "riduce il rischio" in lowered or "rischio" in lowered:
            concepts.append("riduzione rischio")

        if "permessi attivi" in lowered:
            concepts.append("permessi attivi")

        if "utenti autorizzati" in lowered or "non più autorizzati" in lowered:
            concepts.append("utenti autorizzati")

        return q5_unique_strings(concepts)

    except Exception:
        return q5_unique_strings(concepts)


def q5_is_valid_micro_concept(concept: str) -> bool:
    try:
        clean = q5_safe_text(concept).lower().strip()
        clean = re.sub(r"\s+", " ", clean)

        if not clean:
            return False

        words = clean.split()

        if len(words) < 2 or len(words) > 3:
            return False

        stops = q5_stopwords()
        bad_boundary = q5_bad_micro_concept_boundary_tokens()

        if words[0] in stops or words[-1] in stops:
            return False

        if words[0] in bad_boundary or words[-1] in bad_boundary:
            return False

        if any(word in {"non", "deve", "devono", "essere"} for word in words):
            return False

        if all(word in stops for word in words):
            return False

        if len(clean) < 6:
            return False

        if len(words) == 2 and words[1] in bad_boundary:
            return False

        if " non" in clean or clean.endswith(" non"):
            return False

        return True

    except Exception:
        return False


def q5_generate_micro_concepts_from_text(text: str, limit: int = 6) -> List[str]:
    concepts: List[str] = []

    try:
        clean_text = q5_fix_italian_typography(text)
        concepts.extend(q5_domain_micro_concepts_from_text(clean_text))

        tokens = q5_word_tokens(clean_text)
        stops = q5_stopwords()
        bad_boundary = q5_bad_micro_concept_boundary_tokens()

        candidates: List[str] = []

        for size in (2, 3):
            for index in range(0, max(0, len(tokens) - size + 1)):
                gram = tokens[index:index + size]

                if not gram:
                    continue

                if gram[0] in stops or gram[-1] in stops:
                    continue

                if gram[0] in bad_boundary or gram[-1] in bad_boundary:
                    continue

                if any(token in {"non", "deve", "devono", "essere"} for token in gram):
                    continue

                candidate = " ".join(gram)

                if q5_is_valid_micro_concept(candidate):
                    candidates.append(candidate)

        concepts.extend(candidates)

        return q5_unique_strings(concepts)[:limit]

    except Exception:
        return q5_unique_strings(concepts)[:limit]


def q5_select_micro_concepts(
    preferred_concepts: List[str],
    text: str,
    limit: int = 6,
) -> List[str]:
    try:
        selected: List[str] = []

        selected.extend(q5_domain_micro_concepts_from_text(text))

        for concept in preferred_concepts:
            clean = q5_fix_italian_typography(concept).lower()
            if q5_is_valid_micro_concept(clean):
                selected.append(clean)

        if len(q5_unique_strings(selected)) < limit:
            selected.extend(q5_generate_micro_concepts_from_text(text, limit=limit))

        valid = [
            concept
            for concept in q5_unique_strings(selected)
            if q5_is_valid_micro_concept(concept)
        ]

        return valid[:limit]

    except Exception:
        return []


def q5_choose_card_title(
    local_concepts: List[str],
    fact: str,
    used_titles: set,
    fallback: str,
) -> str:
    try:
        for concept in local_concepts:
            title = q5_title_from_text(concept, fallback=fallback, max_words=5)
            key = title.lower()

            if key and key not in used_titles:
                used_titles.add(key)
                return title

        fact_title = q5_title_from_text(fact, fallback=fallback, max_words=6)
        fact_key = fact_title.lower()

        if fact_key not in used_titles:
            used_titles.add(fact_key)
            return fact_title

        progressive = fallback
        used_titles.add(progressive.lower())
        return progressive

    except Exception:
        return fallback


def q5_build_concept_cards(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5QualityConfig,
) -> List[ConceptCardFinal]:
    cards: List[ConceptCardFinal] = []
    used_titles: set = set()

    try:
        if not facts:
            return cards

        max_cards = max(0, config.max_cards)
        max_card_facts = max(1, config.max_card_facts)

        for index in range(0, min(len(facts), max_cards)):
            fact = facts[index]
            related_facts = facts[index:index + max_card_facts]
            text_for_domain = " ".join(related_facts)

            local_concepts = q5_select_micro_concepts(
                preferred_concepts=preferred_concepts,
                text=text_for_domain,
                limit=config.max_micro_concepts_per_card,
            )

            domain = q5_detect_domain_from_text(text_for_domain, local_concepts)
            color = q5_color_for_domain(domain)

            title = q5_choose_card_title(
                local_concepts=local_concepts,
                fact=fact,
                used_titles=used_titles,
                fallback=f"Card concettuale {index + 1}",
            )

            content = q5_build_card_content(related_facts)

            card = ConceptCardFinal(
                card_id=f"phase5_card_{index + 1:03d}",
                titolo=title,
                contenuto_esplicativo=content,
                micro_concetti=local_concepts,
                colore_categoria=color,
                dominio_rilevato=domain,
                fonte_pagine=list(pages),
            )

            if not card.contenuto_esplicativo:
                card.warnings.append("PHASE5_CARD_EMPTY_CONTENT")

            if not card.micro_concetti:
                card.warnings.append("PHASE5_CARD_NO_MICRO_CONCEPTS")

            invalid_concepts = [
                concept for concept in card.micro_concetti
                if not q5_is_valid_micro_concept(concept)
            ]

            if invalid_concepts:
                card.warnings.append(
                    "PHASE5_CARD_INVALID_MICRO_CONCEPTS: " + ", ".join(invalid_concepts)
                )

            cards.append(card)

        return cards

    except Exception:
        return cards


# =============================================================================
# Fine Fase 5.1 — Micro Concepts Cards Quality Patch
# =============================================================================



# =============================================================================
# FASE 5.2 — QUALITY STUDY QUESTIONS QUIZ V1
#
# Completa la Fase 5 per:
# - Genera Domande Studio
# - Genera Test / Quiz
#
# Questa fase usa l'output pulito della Fase 4:
# - SuperQualityGateResult.clean_output
#
# E produce:
# - domande studio naturali, non meccaniche
# - risposte guida chiare
# - quiz con 1 risposta corretta e 3 distrattori falsi/plausibili
# - validazione anti-distrattori veri
#
# Divieti:
# - non modifica Fasi 1–4
# - non modifica Fase 5 summary/card
# - non tocca UI/CSS/pulsanti/layout
# - non approva quiz con distrattori che coincidono con fatti veri
# =============================================================================


@dataclass
class Phase5StudyQuizConfig:
    max_study_questions: int = 12
    max_quiz_questions: int = 10
    quiz_options_count: int = 4
    max_fact_chars: int = 700
    max_micro_concepts_per_item: int = 5
    require_phase4_study_quiz_not_blocked: bool = False


@dataclass
class QualityStudyQuestionFinal:
    question_id: str
    domanda: str
    risposta_guida: str
    tipo_domanda: str
    livello_cognitivo: str
    fatto_origine: str
    micro_concetti: List[str] = field(default_factory=list)
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class QualityQuizOptionFinal:
    option_id: str
    testo: str
    is_correct: bool = False


@dataclass
class QualityQuizQuestionFinal:
    question_id: str
    domanda: str
    opzioni: List[QualityQuizOptionFinal] = field(default_factory=list)
    correct_option_id: str = ""
    spiegazione: str = ""
    fatto_origine: str = ""
    micro_concetti: List[str] = field(default_factory=list)
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Phase5QualityStudyQuizResult:
    document_id: str
    phase_name: str = "QUALITY_STUDY_QUIZ"
    approved: bool = False
    status: str = "PENDING"

    domande_studio: List[QualityStudyQuestionFinal] = field(default_factory=list)
    test_quiz: List[QualityQuizQuestionFinal] = field(default_factory=list)

    quality_report: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def q52_clean(value: Any) -> str:
    try:
        if "q5_fix_italian_typography" in globals():
            return q5_fix_italian_typography(value)
        return normalize_text(value)
    except Exception:
        return ""


def q52_sentence(value: Any) -> str:
    try:
        text = q52_clean(value).strip()
        if not text:
            return ""
        if text[-1] not in ".!?":
            text += "."
        return text
    except Exception:
        return ""


def q52_limit(value: Any, max_chars: int = 700) -> str:
    try:
        text = q52_clean(value)
        if max_chars <= 0 or len(text) <= max_chars:
            return text
        return text[:max_chars].rstrip() + "..."
    except Exception:
        return ""


def q52_unique(values: Sequence[Any]) -> List[str]:
    try:
        return q5_unique_strings(values)
    except Exception:
        output: List[str] = []
        seen = set()
        for value in values:
            clean = q52_clean(value)
            key = clean.lower()
            if clean and key not in seen:
                seen.add(key)
                output.append(clean)
        return output


def q52_extract_facts(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
) -> List[str]:
    try:
        facts = q5_extract_facts_from_gate(gate_result, output_result)
        return q52_unique([q52_limit(fact, 900) for fact in facts if q52_clean(fact)])
    except Exception:
        return []


def q52_extract_concepts(gate_result: SuperQualityGateResult) -> List[str]:
    try:
        concepts = q5_extract_concepts_from_gate(gate_result)
        valid = [
            q52_clean(concept).lower()
            for concept in concepts
            if q5_is_valid_micro_concept(q52_clean(concept))
        ]
        return q52_unique(valid)
    except Exception:
        return []


def q52_extract_pages(gate_result: SuperQualityGateResult) -> List[int]:
    try:
        return q5_extract_pages_from_gate(gate_result)
    except Exception:
        return []


def q52_fact_type(fact: str) -> str:
    try:
        lowered = q52_clean(fact).lower()

        if "non devono" in lowered or "non deve" in lowered or "vietato" in lowered:
            return "divieto"

        if "riduce il rischio" in lowered or "previene" in lowered or "rischio" in lowered:
            return "causa_effetto_rischio"

        if "deve" in lowered or "devono" in lowered or "obbligo" in lowered:
            return "obbligo"

        if "controllo" in lowered or "limita" in lowered:
            return "controllo"

        return "informazione_chiave"

    except Exception:
        return "informazione_chiave"


def q52_cognitive_level(fact_type: str) -> str:
    try:
        mapping = {
            "divieto": "applicazione",
            "causa_effetto_rischio": "comprensione",
            "obbligo": "applicazione",
            "controllo": "comprensione",
            "informazione_chiave": "ricordo_comprensione",
        }
        return mapping.get(fact_type, "comprensione")
    except Exception:
        return "comprensione"


def q52_local_concepts(fact: str, preferred_concepts: List[str], limit: int = 5) -> List[str]:
    try:
        concepts = q5_select_micro_concepts(
            preferred_concepts=preferred_concepts,
            text=fact,
            limit=limit,
        )
        return q52_unique([concept for concept in concepts if q5_is_valid_micro_concept(concept)])[:limit]
    except Exception:
        return []


def q52_topic_label(fact: str, concepts: List[str]) -> str:
    try:
        if concepts:
            return concepts[0]
        return q5_title_from_text(fact, fallback="questo punto", max_words=5).lower()
    except Exception:
        return "questo punto"


def q52_build_study_question_text(fact: str, concepts: List[str], index: int) -> str:
    try:
        fact_type = q52_fact_type(fact)
        topic = q52_topic_label(fact, concepts)

        if fact_type == "divieto":
            return f"Quale comportamento deve essere evitato riguardo a {topic}?"

        if fact_type == "causa_effetto_rischio":
            return f"Perché {topic} è collegato alla riduzione del rischio?"

        if fact_type == "obbligo":
            return f"Quale obbligo operativo viene indicato riguardo a {topic}?"

        if fact_type == "controllo":
            return f"Quale funzione svolge {topic} nel contesto del documento?"

        return f"Che cosa bisogna ricordare riguardo a {topic}?"

    except Exception:
        return f"Qual è il punto operativo principale numero {index}?"


def q52_build_answer_guide(fact: str, fact_type: str) -> str:
    try:
        clean_fact = q52_sentence(fact)

        if fact_type == "divieto":
            return q52_clean(
                "La risposta deve evidenziare il divieto operativo indicato dal documento: "
                + q5_lower_first(clean_fact)
            )

        if fact_type == "causa_effetto_rischio":
            return q52_clean(
                "La risposta deve spiegare il rapporto causa-effetto indicato dal documento: "
                + q5_lower_first(clean_fact)
            )

        if fact_type == "obbligo":
            return q52_clean(
                "La risposta deve indicare l'obbligo operativo espresso nel documento: "
                + q5_lower_first(clean_fact)
            )

        if fact_type == "controllo":
            return q52_clean(
                "La risposta deve chiarire la funzione del controllo descritto: "
                + q5_lower_first(clean_fact)
            )

        return q52_clean(
            "La risposta deve richiamare il punto informativo indicato dal documento: "
            + q5_lower_first(clean_fact)
        )

    except Exception:
        return q52_sentence(fact)


def q52_build_quality_study_questions(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5StudyQuizConfig,
) -> List[QualityStudyQuestionFinal]:
    questions: List[QualityStudyQuestionFinal] = []

    try:
        for index, fact in enumerate(facts[: max(0, config.max_study_questions)], start=1):
            clean_fact = q52_limit(fact, config.max_fact_chars)
            fact_type = q52_fact_type(clean_fact)
            concepts = q52_local_concepts(
                clean_fact,
                preferred_concepts,
                limit=config.max_micro_concepts_per_item,
            )

            domanda = q52_build_study_question_text(clean_fact, concepts, index)
            risposta = q52_build_answer_guide(clean_fact, fact_type)

            item = QualityStudyQuestionFinal(
                question_id=f"phase5_study_question_{index:03d}",
                domanda=domanda,
                risposta_guida=risposta,
                tipo_domanda=fact_type,
                livello_cognitivo=q52_cognitive_level(fact_type),
                fatto_origine=clean_fact,
                micro_concetti=concepts,
                fonte_pagine=list(pages),
            )

            lowered = item.domanda.lower()
            if "quale regola o informazione emerge da" in lowered:
                item.warnings.append("PHASE5_STUDY_QUESTION_MECHANICAL_TEMPLATE")

            questions.append(item)

        return questions

    except Exception:
        return questions


def q52_false_distractors_from_fact(fact: str) -> List[str]:
    """
    Genera distrattori falsi ma plausibili.

    Non li usa come facts.
    Servono solo come opzioni errate del quiz.
    """

    distractors: List[str] = []

    try:
        clean = q52_clean(fact).rstrip(".")
        lowered = clean.lower()

        replacements = [
            ("non devono essere condivise", "possono essere condivise liberamente"),
            ("non deve essere condivisa", "può essere condivisa liberamente"),
            ("deve essere associato", "può rimanere non associato"),
            ("deve essere associata", "può rimanere non associata"),
            ("devono essere", "non devono essere necessariamente"),
            ("deve essere", "non deve essere necessariamente"),
            ("limita l'utilizzo", "consente l'utilizzo illimitato"),
            ("limita", "non limita"),
            ("riduce il rischio", "aumenta il rischio"),
            ("evita", "favorisce"),
            ("persona identificabile", "persona non identificabile"),
            ("utenti autorizzati", "qualsiasi utente"),
            ("permessi attivi", "permessi illimitati"),
            ("sistemi interni", "sistemi esterni non controllati"),
        ]

        for old, new in replacements:
            if old in lowered:
                pattern = re.compile(re.escape(old), flags=re.IGNORECASE)
                candidate = pattern.sub(new, clean, count=1)
                candidate = q52_sentence(candidate)
                if candidate and candidate.lower() != q52_sentence(clean).lower():
                    distractors.append(candidate)

        topic = q52_topic_label(clean, q52_domain_micro_concepts_from_text(clean))

        generic_false = [
            f"Il documento indica che {topic} può essere ignorato senza effetti operativi.",
            f"Il documento esclude la necessità di controllare {topic}.",
            f"Il documento presenta {topic} come un aspetto facoltativo e non rilevante.",
            f"Il documento sostiene che {topic} non abbia alcun impatto sui controlli.",
        ]

        distractors.extend(generic_false)

        return q52_unique(distractors)

    except Exception:
        return q52_unique(distractors)


def q52_build_quiz_question_text(fact: str, concepts: List[str], index: int) -> str:
    try:
        fact_type = q52_fact_type(fact)
        topic = q52_topic_label(fact, concepts)

        if fact_type == "divieto":
            return f"Quale affermazione descrive correttamente il divieto su {topic}?"

        if fact_type == "causa_effetto_rischio":
            return f"Quale affermazione descrive correttamente l'effetto di {topic}?"

        if fact_type == "obbligo":
            return f"Quale affermazione descrive correttamente l'obbligo su {topic}?"

        if fact_type == "controllo":
            return f"Quale affermazione descrive correttamente la funzione di {topic}?"

        return f"Quale affermazione descrive correttamente {topic}?"

    except Exception:
        return f"Quale affermazione è corretta nel punto {index}?"


def q52_build_quality_quiz(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5StudyQuizConfig,
) -> List[QualityQuizQuestionFinal]:
    quiz: List[QualityQuizQuestionFinal] = []

    try:
        source_keys = set(qg_normalize_for_compare(fact) for fact in facts if q52_clean(fact))
        option_ids = ["A", "B", "C", "D"]

        for index, fact in enumerate(facts[: max(0, config.max_quiz_questions)], start=1):
            correct_fact = q52_limit(fact, config.max_fact_chars)
            concepts = q52_local_concepts(
                correct_fact,
                preferred_concepts,
                limit=config.max_micro_concepts_per_item,
            )

            distractors: List[str] = []
            for candidate in q52_false_distractors_from_fact(correct_fact):
                key = qg_normalize_for_compare(candidate)
                if key and key not in source_keys:
                    distractors.append(candidate)

            distractors = q52_unique(distractors)

            if len(distractors) < 3:
                continue

            correct_position = (index - 1) % 4
            raw_options = distractors[:3]
            raw_options.insert(correct_position, correct_fact)

            options: List[QualityQuizOptionFinal] = []

            for option_index, option_text in enumerate(raw_options[:4]):
                options.append(
                    QualityQuizOptionFinal(
                        option_id=option_ids[option_index],
                        testo=q52_limit(option_text, config.max_fact_chars),
                        is_correct=(option_index == correct_position),
                    )
                )

            question = QualityQuizQuestionFinal(
                question_id=f"phase5_quiz_question_{index:03d}",
                domanda=q52_build_quiz_question_text(correct_fact, concepts, index),
                opzioni=options,
                correct_option_id=option_ids[correct_position],
                spiegazione=q52_clean(
                    "La risposta corretta è quella che riprende il fatto verificato dal documento: "
                    + q5_lower_first(q52_sentence(correct_fact))
                ),
                fatto_origine=correct_fact,
                micro_concetti=concepts,
                fonte_pagine=list(pages),
            )

            quiz.append(question)

        return quiz

    except Exception:
        return quiz


def q52_validate_study_questions(questions: List[QualityStudyQuestionFinal]) -> List[str]:
    errors: List[str] = []

    try:
        forbidden_templates = [
            "quale regola o informazione emerge da",
            "quale affermazione è supportata dal documento",
        ]

        seen = set()

        for item in questions:
            if not q52_clean(item.domanda):
                errors.append(f"{item.question_id}: domanda vuota")

            if not q52_clean(item.risposta_guida):
                errors.append(f"{item.question_id}: risposta_guida vuota")

            lowered = item.domanda.lower()

            for template in forbidden_templates:
                if template in lowered:
                    errors.append(f"{item.question_id}: formula meccanica vietata")

            key = qg_normalize_for_compare(item.domanda)
            if key in seen:
                errors.append(f"{item.question_id}: domanda duplicata")
            seen.add(key)

        return errors

    except Exception as exc:
        return [f"PHASE5_STUDY_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def q52_validate_quiz(quiz: List[QualityQuizQuestionFinal], source_facts: List[str], expected_options: int = 4) -> List[str]:
    errors: List[str] = []

    try:
        source_keys = set(qg_normalize_for_compare(fact) for fact in source_facts if q52_clean(fact))

        forbidden_question_templates = [
            "quale affermazione è supportata dal documento",
            "quale regola o informazione emerge da",
        ]

        seen_questions = set()

        for question in quiz:
            if not q52_clean(question.domanda):
                errors.append(f"{question.question_id}: domanda vuota")

            lowered_question = question.domanda.lower()
            for template in forbidden_question_templates:
                if template in lowered_question:
                    errors.append(f"{question.question_id}: formula quiz meccanica vietata")

            question_key = qg_normalize_for_compare(question.domanda)
            if question_key in seen_questions:
                errors.append(f"{question.question_id}: domanda quiz duplicata")
            seen_questions.add(question_key)

            if len(question.opzioni) != expected_options:
                errors.append(f"{question.question_id}: numero opzioni non valido")

            correct_options = [option for option in question.opzioni if option.is_correct]
            if len(correct_options) != 1:
                errors.append(f"{question.question_id}: deve avere esattamente una corretta")

            if correct_options:
                if q52_clean(correct_options[0].option_id) != q52_clean(question.correct_option_id):
                    errors.append(f"{question.question_id}: correct_option_id non coincide")

            option_keys = set()

            for option in question.opzioni:
                if not q52_clean(option.testo):
                    errors.append(f"{question.question_id}: opzione vuota")

                option_key = qg_normalize_for_compare(option.testo)

                if option_key in option_keys:
                    errors.append(f"{question.question_id}: opzione duplicata")
                option_keys.add(option_key)

                if not option.is_correct and option_key in source_keys:
                    errors.append(f"{question.question_id}: distrattore coincide con fact vero")

            if qg_normalize_for_compare(question.fatto_origine) not in source_keys:
                errors.append(f"{question.question_id}: fatto_origine non tracciabile nei facts")

        return errors

    except Exception as exc:
        return [f"PHASE5_QUIZ_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def q52_validate_phase4_for_study_quiz(
    gate_result: SuperQualityGateResult,
    config: Phase5StudyQuizConfig,
) -> List[str]:
    errors: List[str] = []

    try:
        if not config.require_phase4_study_quiz_not_blocked:
            return errors

        blocked_areas = list(getattr(gate_result, "blocked_areas", []) or [])

        if "study_questions" in blocked_areas:
            errors.append("PHASE5_CANNOT_BUILD_STUDY_PHASE4_BLOCKED_STUDY_QUESTIONS")

        if "quiz" in blocked_areas:
            errors.append("PHASE5_CANNOT_BUILD_QUIZ_PHASE4_BLOCKED_QUIZ")

        return errors

    except Exception as exc:
        return [f"PHASE5_STUDY_QUIZ_PHASE4_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def build_phase5_quality_study_quiz(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
    config: Optional[Phase5StudyQuizConfig] = None,
) -> Phase5QualityStudyQuizResult:
    """
    Funzione madre Fase 5.2.

    Collegamento:
    - input principale: SuperQualityGateResult.clean_output
    - output: domande studio finali + test quiz finale

    Nota:
    se la Fase 4 ha bloccato il quiz grezzo, questa fase può comunque
    ricostruire un quiz nuovo con distrattori falsi/plausibili.
    """

    cfg = config or Phase5StudyQuizConfig()

    result = Phase5QualityStudyQuizResult(
        document_id=q52_clean(getattr(gate_result, "document_id", "")) or "unknown_document",
    )

    try:
        result.errors.extend(q52_validate_phase4_for_study_quiz(gate_result, cfg))

        facts = q52_extract_facts(gate_result, output_result)
        concepts = q52_extract_concepts(gate_result)
        pages = q52_extract_pages(gate_result)

        if not facts:
            result.errors.append("PHASE5_STUDY_QUIZ_NO_FACTS_AVAILABLE")

        result.domande_studio = q52_build_quality_study_questions(
            facts=facts,
            preferred_concepts=concepts,
            pages=pages,
            config=cfg,
        )

        result.test_quiz = q52_build_quality_quiz(
            facts=facts,
            preferred_concepts=concepts,
            pages=pages,
            config=cfg,
        )

        result.errors.extend(q52_validate_study_questions(result.domande_studio))
        result.errors.extend(q52_validate_quiz(result.test_quiz, facts, cfg.quiz_options_count))

        if not result.domande_studio:
            result.errors.append("PHASE5_STUDY_QUESTIONS_EMPTY")

        if not result.test_quiz:
            result.errors.append("PHASE5_TEST_QUIZ_EMPTY")

        result.quality_report = {
            "facts_used": len(facts),
            "concepts_used": len(concepts),
            "study_questions_count": len(result.domande_studio),
            "quiz_questions_count": len(result.test_quiz),
            "source_pages": pages,
            "errors_count": len(result.errors),
            "warnings_count": len(result.warnings),
        }

        if result.errors:
            result.status = "NEEDS_REVIEW"
            result.approved = False
        else:
            result.status = "APPROVED"
            result.approved = True

        return result

    except Exception as exc:
        result.status = "ERROR"
        result.approved = False
        result.errors.append(f"PHASE5_STUDY_QUIZ_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def phase5_quality_study_quiz_result_to_dict(
    result: Phase5QualityStudyQuizResult,
) -> Dict[str, Any]:
    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "QUALITY_STUDY_QUIZ",
            "approved": False,
            "status": "SERIALIZATION_ERROR",
            "errors": ["PHASE5_STUDY_QUIZ_SERIALIZATION_FAILED"],
        }


def phase5_quality_study_quiz_result_to_json(
    result: Phase5QualityStudyQuizResult,
    indent: int = 2,
) -> str:
    try:
        return json.dumps(
            phase5_quality_study_quiz_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "QUALITY_STUDY_QUIZ",
                "approved": False,
                "status": "JSON_SERIALIZATION_ERROR",
                "errors": [f"PHASE5_STUDY_QUIZ_JSON_FAILED: {type(exc).__name__}: {exc}"],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 5.2 — Quality Study Questions Quiz V1
# =============================================================================



# =============================================================================
# FASE 5.2.1 — ROBUST QUIZ DISTRACTORS PATCH
#
# Micro-patch solo Fase 5.2.
#
# Problema corretto:
# - il quiz saltava alcuni facts quando non trovava almeno 3 distrattori.
#
# Obiettivo:
# - generare sempre 3 distrattori falsi/plausibili per ogni fact valido
# - non usare mai come distrattori altri facts veri del documento
# - mantenere esattamente 1 risposta corretta e 4 opzioni
#
# Non modifica Fasi 1–4.
# Non tocca UI/CSS/pulsanti/layout.
# =============================================================================


def q521_topic_from_fact(fact: str, concepts: Optional[List[str]] = None) -> str:
    """
    Ricava un'etichetta breve e leggibile per creare distrattori generici.
    """

    try:
        local_concepts = concepts or q52_domain_micro_concepts_from_text(fact)
        if local_concepts:
            return q52_clean(local_concepts[0]).lower()

        title = q5_title_from_text(fact, fallback="questo controllo", max_words=4)
        return q52_clean(title).lower()

    except Exception:
        return "questo controllo"


def q521_generic_false_distractors(fact: str, concepts: Optional[List[str]] = None) -> List[str]:
    """
    Distrattori generici ma plausibili.

    Sono volutamente falsi:
    - dicono che il controllo è facoltativo
    - negano l'obbligo
    - negano l'impatto sul rischio
    - spostano l'attenzione fuori dal documento
    """

    distractors: List[str] = []

    try:
        topic = q521_topic_from_fact(fact, concepts)

        templates = [
            f"Il documento indica che {topic} può essere ignorato senza conseguenze operative.",
            f"Il documento presenta {topic} come un elemento facoltativo e non necessario.",
            f"Il documento esclude che {topic} abbia effetti sui controlli interni.",
            f"Il documento afferma che {topic} riguarda solo attività esterne al sistema.",
            f"Il documento sostiene che {topic} non richiede alcuna verifica periodica.",
            f"Il documento considera {topic} irrilevante per la gestione del rischio.",
            f"Il documento permette di applicare {topic} solo quando l'operatore lo ritiene utile.",
            f"Il documento chiarisce che {topic} non è collegato alla sicurezza operativa.",
        ]

        for template in templates:
            distractors.append(q52_sentence(template))

        return q52_unique(distractors)

    except Exception:
        return q52_unique(distractors)


def q52_false_distractors_from_fact(fact: str) -> List[str]:
    """
    Override robusto Fase 5.2.1.

    Genera distrattori:
    1. con trasformazioni dirette del fact
    2. con distrattori generici falsi/plausibili
    3. con fallback sicuro se le trasformazioni non bastano
    """

    distractors: List[str] = []

    try:
        clean = q52_clean(fact).rstrip(".")
        lowered = clean.lower()

        replacements = [
            ("non devono essere condivise", "possono essere condivise liberamente"),
            ("non deve essere condivisa", "può essere condivisa liberamente"),
            ("non devono essere condivisi", "possono essere condivisi liberamente"),
            ("non deve essere condiviso", "può essere condiviso liberamente"),
            ("deve essere associato", "può rimanere non associato"),
            ("deve essere associata", "può rimanere non associata"),
            ("devono essere associati", "possono rimanere non associati"),
            ("devono essere associate", "possono rimanere non associate"),
            ("devono essere", "non devono essere necessariamente"),
            ("deve essere", "non deve essere necessariamente"),
            ("limita l'utilizzo", "consente l'utilizzo illimitato"),
            ("limita", "non limita"),
            ("riduce il rischio", "aumenta il rischio"),
            ("riduce", "aumenta"),
            ("evita", "favorisce"),
            ("previene", "favorisce"),
            ("persona identificabile", "persona non identificabile"),
            ("utenti non più autorizzati", "utenti sempre autorizzati"),
            ("utenti autorizzati", "qualsiasi utente"),
            ("permessi attivi", "permessi illimitati"),
            ("sistemi interni", "sistemi esterni non controllati"),
            ("operatori", "utenti anonimi"),
            ("accessi", "accessi non controllati"),
            ("credenziali", "credenziali condivise"),
            ("account", "account anonimo"),
        ]

        for old, new in replacements:
            if old in lowered:
                pattern = re.compile(re.escape(old), flags=re.IGNORECASE)
                candidate = pattern.sub(new, clean, count=1)
                candidate = q52_sentence(candidate)

                if candidate and qg_normalize_for_compare(candidate) != qg_normalize_for_compare(clean):
                    distractors.append(candidate)

        concepts = q52_domain_micro_concepts_from_text(clean)
        distractors.extend(q521_generic_false_distractors(clean, concepts))

        # Fallback extra: sempre falsi e sempre diversi dal fact.
        topic = q521_topic_from_fact(clean, concepts)

        fallback_extra = [
            f"{q52_clean(topic).capitalize()} non richiede controlli documentati.",
            f"{q52_clean(topic).capitalize()} può essere gestito senza regole operative.",
            f"{q52_clean(topic).capitalize()} non modifica il livello di rischio.",
            f"{q52_clean(topic).capitalize()} è indicato come scelta libera dell'utente.",
            f"{q52_clean(topic).capitalize()} non deve essere collegato agli account.",
        ]

        distractors.extend(q52_sentence(item) for item in fallback_extra)

        return q52_unique(distractors)

    except Exception:
        return q52_unique(distractors)


def q521_filter_distractors(
    candidates: List[str],
    correct_fact: str,
    source_facts: List[str],
    needed: int = 3,
) -> List[str]:
    """
    Filtra distrattori:
    - non vuoti
    - non uguali alla risposta corretta
    - non uguali a facts veri del documento
    - non duplicati
    """

    selected: List[str] = []

    try:
        source_keys = set(
            qg_normalize_for_compare(fact)
            for fact in source_facts
            if q52_clean(fact)
        )

        correct_key = qg_normalize_for_compare(correct_fact)

        for candidate in candidates:
            clean_candidate = q52_sentence(candidate)
            key = qg_normalize_for_compare(clean_candidate)

            if not key:
                continue

            if key == correct_key:
                continue

            if key in source_keys:
                continue

            if key in set(qg_normalize_for_compare(item) for item in selected):
                continue

            selected.append(clean_candidate)

            if len(selected) >= needed:
                break

        return selected

    except Exception:
        return selected


def q52_build_quality_quiz(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5StudyQuizConfig,
) -> List[QualityQuizQuestionFinal]:
    """
    Override robusto Fase 5.2.1.

    Non salta più facts validi se il generatore principale produce pochi distrattori.
    Usa fallback robusti, poi valida tutto.
    """

    quiz: List[QualityQuizQuestionFinal] = []

    try:
        option_ids = ["A", "B", "C", "D"]

        usable_facts = [
            q52_limit(fact, config.max_fact_chars)
            for fact in facts
            if q52_clean(fact)
        ]

        for index, fact in enumerate(usable_facts[: max(0, config.max_quiz_questions)], start=1):
            correct_fact = q52_sentence(fact)
            concepts = q52_local_concepts(
                correct_fact,
                preferred_concepts,
                limit=config.max_micro_concepts_per_item,
            )

            raw_candidates = q52_false_distractors_from_fact(correct_fact)

            distractors = q521_filter_distractors(
                candidates=raw_candidates,
                correct_fact=correct_fact,
                source_facts=usable_facts,
                needed=3,
            )

            # Ultimo fallback, se per qualsiasi motivo restano meno di 3.
            if len(distractors) < 3:
                topic = q521_topic_from_fact(correct_fact, concepts)
                emergency = [
                    f"Il documento dice che {topic} può essere ignorato.",
                    f"Il documento dice che {topic} non ha valore operativo.",
                    f"Il documento dice che {topic} non richiede controlli.",
                    f"Il documento dice che {topic} aumenta sempre la sicurezza senza verifiche.",
                    f"Il documento dice che {topic} riguarda solo informazioni esterne.",
                ]

                distractors = q521_filter_distractors(
                    candidates=distractors + emergency,
                    correct_fact=correct_fact,
                    source_facts=usable_facts,
                    needed=3,
                )

            if len(distractors) < 3:
                # Non dovrebbe più accadere, ma lasciamo warning e saltiamo solo casi impossibili.
                continue

            correct_position = (index - 1) % 4
            raw_options = distractors[:3]
            raw_options.insert(correct_position, correct_fact)

            options: List[QualityQuizOptionFinal] = []

            for option_index, option_text in enumerate(raw_options[:4]):
                options.append(
                    QualityQuizOptionFinal(
                        option_id=option_ids[option_index],
                        testo=q52_limit(option_text, config.max_fact_chars),
                        is_correct=(option_index == correct_position),
                    )
                )

            question = QualityQuizQuestionFinal(
                question_id=f"phase5_quiz_question_{index:03d}",
                domanda=q52_build_quiz_question_text(correct_fact, concepts, index),
                opzioni=options,
                correct_option_id=option_ids[correct_position],
                spiegazione=q52_clean(
                    "La risposta corretta è quella che riprende il fatto verificato dal documento: "
                    + q5_lower_first(q52_sentence(correct_fact))
                ),
                fatto_origine=correct_fact,
                micro_concetti=concepts,
                fonte_pagine=list(pages),
            )

            quiz.append(question)

        return quiz

    except Exception:
        return quiz


# =============================================================================
# Fine Fase 5.2.1 — Robust Quiz Distractors Patch
# =============================================================================

# FASE 5.3 — LIVE QUALITY BRIDGE V1
# Collegamento controllato dell'output Fase 5 ai motori qualità vivi.
# Non importa backup. Non riscrive i motori. Non cambia la logica originale.
try:
    import functools as _phase5_live_quality_functools
    from backend.phase5_live_quality_bridge_v1 import (
        apply_phase5_live_quality_bridge_v1 as _phase5_apply_live_quality_bridge_v1,
    )

    _phase5_original_build_phase5_quality_study_quiz_v1 = build_phase5_quality_study_quiz

    @_phase5_live_quality_functools.wraps(_phase5_original_build_phase5_quality_study_quiz_v1)
    def build_phase5_quality_study_quiz(*args, **kwargs):
        _phase5_raw_output = _phase5_original_build_phase5_quality_study_quiz_v1(*args, **kwargs)
        return _phase5_apply_live_quality_bridge_v1(_phase5_raw_output)

except Exception as _phase5_live_quality_bridge_error:
    _phase5_live_quality_bridge_import_error = repr(_phase5_live_quality_bridge_error)

# FASE 5.4 — LEGACY QUALITY MOTOR REGISTRY HOOK V1
# Collega la nuova struttura centrale dei motori legacy alla Fase 5.
# Non sostituisce i motori vecchi: li esegue tramite registry, adapter e guardia anti-peggioramento.
try:
    import functools as _phase5_4_legacy_registry_functools
    from backend.legacy_quality_motor_registry_v1 import (
        apply_legacy_quality_motors_v1 as _phase5_4_apply_legacy_quality_motors_v1,
    )

    _phase5_4_previous_build_phase5_quality_study_quiz = build_phase5_quality_study_quiz

    @_phase5_4_legacy_registry_functools.wraps(_phase5_4_previous_build_phase5_quality_study_quiz)
    def build_phase5_quality_study_quiz(*args, **kwargs):
        _phase5_4_raw_output = _phase5_4_previous_build_phase5_quality_study_quiz(*args, **kwargs)
        return _phase5_4_apply_legacy_quality_motors_v1(
            _phase5_4_raw_output,
            context="phase5_quality_study_quiz",
        )

except Exception as _phase5_4_legacy_registry_error:
    _phase5_4_legacy_registry_import_error = repr(_phase5_4_legacy_registry_error)
