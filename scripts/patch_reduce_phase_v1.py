# scripts/patch_reduce_phase_v1.py
# =============================================================================
# PATCH REDUCE PHASE V1
#
# Modifica SOLO backend:
# - target: backend/motori_scrittura.py
# - aggiunge Fase 2 REDUCE gerarchica ad albero
# - nessuna modifica a UI, CSS, pulsanti o grafica
#
# REDUCE V1 è volutamente deterministica:
# - non usa LLM
# - non riscrive in stile elegante
# - non fa Super Quality Gate
# - unisce, deduplica, conserva fonti e struttura
# =============================================================================

from __future__ import annotations

import shutil
import sys
from pathlib import Path


TARGET_FILE = Path("backend/motori_scrittura.py")
PATCH_MARKER = "FASE 2 — REDUCE V1"


REDUCE_CODE = r'''

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
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if PATCH_MARKER in original:
            print("✅ REDUCE V1 già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_reduce_phase_v1")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + REDUCE_CODE + "\n"

        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch REDUCE PHASE V1 applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore patch REDUCE PHASE V1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())