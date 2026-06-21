#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"

THEMES_PATH = CONFIG_DIR / "temi_card_materie.json"
LAYOUT_PATH = CONFIG_DIR / "layout_card_grafiche.json"
CONCEPTS_PATH = CONFIG_DIR / "icone_concetti_materie.json"
SYNONYMS_PATH = CONFIG_DIR / "sinonimi_concetti.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_engine_data() -> dict[str, Any]:
    return {
        "themes": load_json(THEMES_PATH),
        "layout": load_json(LAYOUT_PATH),
        "concepts": load_json(CONCEPTS_PATH),
        "synonyms": load_json(SYNONYMS_PATH),
    }


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text))
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9àèéìòùç%\s]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def safe_html(value: Any) -> str:
    return html.escape(str(value), quote=True)


def detect_subject(text: str, preferred_subject: str | None = None, data: dict[str, Any] | None = None) -> str:
    data = data or load_engine_data()
    themes = data["themes"]
    concepts = data["concepts"]

    if preferred_subject and preferred_subject in themes:
        return preferred_subject

    normalized = normalize_text(text)
    scores: dict[str, int] = {}

    for subject, theme in themes.items():
        if subject == "generico":
            continue

        score = 0

        for keyword in theme.get("parole_chiave", []):
            if normalize_text(keyword) in normalized:
                score += 3

        for concept_name in concepts.get(subject, {}):
            if normalize_text(concept_name) in normalized:
                score += 5

        scores[subject] = score

    best = max(scores, key=scores.get) if scores else "generico"

    if scores.get(best, 0) <= 0:
        return "generico"

    return best


def detect_concept(text: str, subject: str | None = None, data: dict[str, Any] | None = None) -> str:
    data = data or load_engine_data()
    concepts = data["concepts"]
    synonyms = data["synonyms"]
    normalized = normalize_text(text)

    subjects = [subject] if subject and subject in concepts else list(concepts.keys())
    scored: list[tuple[int, str]] = []

    for current_subject in subjects:
        for concept_name in concepts.get(current_subject, {}):
            names = [concept_name] + synonyms.get(concept_name, [])

            score = 0
            for name in names:
                name_norm = normalize_text(name)
                if name_norm and name_norm in normalized:
                    score += 10 + len(name_norm)

            if score:
                scored.append((score, concept_name))

    if scored:
        scored.sort(reverse=True)
        return scored[0][1]

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{4,}", text)
    stopwords = {"questo", "questa", "documento", "viene", "sono", "della", "delle", "come", "anche"}
    for word in words:
        if normalize_text(word) not in stopwords:
            return word.lower()

    return "concetto"


def resolve_profile(materia: str | None, concetto: str | None, testo: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    data = data or load_engine_data()
    themes = data["themes"]
    concepts = data["concepts"]

    subject = detect_subject(f"{concetto or ''} {testo}", materia, data)
    concept = concetto or detect_concept(testo, subject, data)

    theme = themes.get(subject, themes["generico"])
    concept_config = concepts.get(subject, {}).get(concept)

    if not concept_config:
        concept_config = {
            "icona": theme.get("icona_base", "spark"),
            "decorazioni": [theme.get("sfondo", "astratto")],
        }

    return {
        "materia": subject,
        "tema": theme,
        "concetto": concept,
        "icona": concept_config.get("icona", theme.get("icona_base", "spark")),
        "decorazioni": concept_config.get("decorazioni", []),
    }


def svg_icon(icon: str, palette: list[str], concept: str) -> str:
    primary, secondary, accent = palette

    if icon in {"shield", "lock-code", "badge-check"}:
        return f'''
        <path d="M110 26 L168 50 V92 C168 130 143 158 110 176 C77 158 52 130 52 92 V50 Z" fill="{accent}" opacity=".92"/>
        <rect x="86" y="96" width="48" height="42" rx="8" fill="{primary}" opacity=".9"/>
        <path d="M96 96 v-15 c0-19 28-19 28 0v15" fill="none" stroke="{primary}" stroke-width="9" stroke-linecap="round"/>
        '''

    if icon in {"backup"}:
        return f'''
        <path d="M74 126 h86 c20 0 35-14 35-32 0-17-13-30-31-32-7-20-25-32-48-32-28 0-49 18-53 44-20 3-34 17-34 35 0 10 5 17 13 17z" fill="{accent}" opacity=".92"/>
        <path d="M110 118 V78" stroke="{primary}" stroke-width="10" stroke-linecap="round"/>
        <path d="M90 96 l20-20 20 20" fill="none" stroke="{primary}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="72" y="142" width="76" height="24" rx="8" fill="{primary}" opacity=".9"/>
        '''

    if icon in {"key"}:
        return f'''
        <circle cx="82" cy="88" r="30" fill="none" stroke="{accent}" stroke-width="13"/>
        <path d="M106 100 L170 164" stroke="{accent}" stroke-width="15" stroke-linecap="round"/>
        <path d="M148 142 h32 M132 126 h22" stroke="{accent}" stroke-width="10" stroke-linecap="round"/>
        '''

    if icon in {"email-hook"}:
        return f'''
        <rect x="44" y="66" width="128" height="82" rx="14" fill="{accent}" opacity=".92"/>
        <path d="M48 76 l60 42 60-42" fill="none" stroke="{primary}" stroke-width="8" stroke-linejoin="round"/>
        <path d="M150 44 c30 18 28 66-2 76" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>
        '''

    if icon in {"bug"}:
        return f'''
        <circle cx="110" cy="104" r="44" fill="{accent}" opacity=".94"/>
        <circle cx="94" cy="94" r="7" fill="{primary}"/>
        <circle cx="126" cy="94" r="7" fill="{primary}"/>
        <path d="M92 122 c14 10 25 10 38 0" stroke="{primary}" stroke-width="8" stroke-linecap="round"/>
        <path d="M54 104 H28 M192 104 h-26 M72 62 L50 42 M148 62 l22-20" stroke="{accent}" stroke-width="9" stroke-linecap="round"/>
        '''

    if icon in {"database"}:
        return f'''
        <ellipse cx="110" cy="58" rx="62" ry="24" fill="{accent}" opacity=".95"/>
        <path d="M48 58 v88 c0 14 28 25 62 25s62-11 62-25V58" fill="{accent}" opacity=".75"/>
        <ellipse cx="110" cy="146" rx="62" ry="24" fill="{accent}" opacity=".9"/>
        <path d="M48 90 c0 14 28 25 62 25s62-11 62-25 M48 118 c0 14 28 25 62 25s62-11 62-25" fill="none" stroke="{primary}" stroke-width="6" opacity=".65"/>
        '''

    if icon in {"flow", "function", "api", "server", "json", "screen", "box"}:
        return f'''
        <rect x="34" y="52" width="58" height="40" rx="10" fill="{accent}"/>
        <rect x="128" y="52" width="58" height="40" rx="10" fill="{accent}" opacity=".85"/>
        <rect x="81" y="124" width="58" height="40" rx="10" fill="{accent}" opacity=".7"/>
        <path d="M92 72 h36 M110 92 v32" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
        '''

    if icon in {"chip", "network", "vectors", "prompt", "rag", "table", "training", "inference"}:
        return f'''
        <rect x="66" y="54" width="88" height="88" rx="18" fill="{accent}" opacity=".9"/>
        <path d="M46 72 h20 M46 96 h20 M46 120 h20 M154 72 h20 M154 96 h20 M154 120 h20" stroke="{accent}" stroke-width="8" stroke-linecap="round"/>
        <circle cx="90" cy="86" r="7" fill="{primary}"/><circle cx="128" cy="86" r="7" fill="{primary}"/><circle cx="110" cy="118" r="7" fill="{primary}"/>
        <path d="M90 86 L110 118 L128 86" stroke="{primary}" stroke-width="5" fill="none"/>
        '''

    if icon in {"chart", "derivative", "integral", "formula", "percent", "fraction"}:
        return f'''
        <path d="M44 150 H178 M58 164 V44" stroke="#fff" stroke-width="6" opacity=".75"/>
        <path d="M58 136 C84 126 86 72 116 86 C140 98 142 132 174 58" fill="none" stroke="{accent}" stroke-width="11" stroke-linecap="round"/>
        <path d="M86 112 L150 74" stroke="{primary}" stroke-width="7" stroke-linecap="round" opacity=".88"/>
        '''

    if icon in {"atom", "energy", "vector", "speed", "acceleration", "circuit"}:
        return f'''
        <circle cx="110" cy="104" r="13" fill="{accent}"/>
        <ellipse cx="110" cy="104" rx="76" ry="28" fill="none" stroke="{accent}" stroke-width="7"/>
        <ellipse cx="110" cy="104" rx="76" ry="28" fill="none" stroke="{accent}" stroke-width="7" transform="rotate(60 110 104)"/>
        <ellipse cx="110" cy="104" rx="76" ry="28" fill="none" stroke="{accent}" stroke-width="7" transform="rotate(-60 110 104)"/>
        '''

    if icon in {"molecule", "reaction", "bond", "flask", "beaker"}:
        return f'''
        <circle cx="74" cy="92" r="26" fill="{accent}"/><circle cx="146" cy="72" r="22" fill="{accent}" opacity=".8"/><circle cx="142" cy="138" r="28" fill="{accent}" opacity=".65"/>
        <path d="M96 86 L126 78 M94 104 L120 126" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
        '''

    if icon in {"dna", "cell", "protein", "organism", "leaf", "mitosis"}:
        return f'''
        <path d="M76 34 C148 70 148 138 76 174 M144 34 C72 70 72 138 144 174" fill="none" stroke="{accent}" stroke-width="9" stroke-linecap="round"/>
        <path d="M88 60 h44 M78 88 h64 M78 120 h64 M88 148 h44" stroke="#fff" stroke-width="6" opacity=".7"/>
        '''

    return f'''
    <circle cx="110" cy="90" r="46" fill="{accent}" opacity=".9"/>
    <rect x="52" y="142" width="116" height="18" rx="9" fill="{accent}" opacity=".65"/>
    <text x="110" y="104" text-anchor="middle" font-size="24" fill="{primary}" font-family="Arial" font-weight="900">★</text>
    '''


def render_svg(profile: dict[str, Any]) -> str:
    theme = profile["tema"]
    palette = theme.get("palette", ["#0f172a", "#7c3aed", "#e2e8f0"])
    primary, secondary, accent = palette
    icon = profile.get("icona", "spark")
    concept = profile.get("concetto", "concetto")

    return f'''
    <svg class="card-illustration" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 210" role="img" aria-label="Illustrazione {safe_html(concept)}">
      <defs>
        <linearGradient id="bg-{safe_html(concept)}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{primary}"/>
          <stop offset="100%" stop-color="{secondary}"/>
        </linearGradient>
      </defs>
      <rect width="220" height="210" rx="28" fill="url(#bg-{safe_html(concept)})"/>
      <circle cx="48" cy="52" r="34" fill="{accent}" opacity="0.16"/>
      <circle cx="176" cy="176" r="60" fill="#ffffff" opacity="0.08"/>
      {svg_icon(icon, palette, concept)}
    </svg>
    '''


def render_card_html(titolo: str, testo: str, materia: str | None = None, concetto: str | None = None, uso: str | None = None) -> str:
    data = load_engine_data()
    profile = resolve_profile(materia, concetto, f"{titolo} {testo}", data)
    theme = profile["tema"]
    palette = theme.get("palette", ["#0f172a", "#7c3aed", "#e2e8f0"])
    primary, secondary, accent = palette
    badge = theme.get("badge", profile["materia"])
    uso = uso or "Ripassa questo punto e prova a rispiegarlo con parole tue."

    return f'''
    <article class="graphic-card" style="--card-primary:{primary}; --card-secondary:{secondary}; --card-accent:{accent};">
      <div class="graphic-card-badge">{safe_html(badge)}</div>
      <div class="graphic-card-image">{render_svg(profile)}</div>
      <h2>{safe_html(titolo)}</h2>
      <p>{safe_html(testo)}</p>
      <small>{safe_html(uso)}</small>
    </article>
    '''


def render_cards_page(cards: list[dict[str, Any]], titolo_pagina: str = "Card grafiche") -> str:
    card_html = []
    for card in cards:
        card_html.append(
            render_card_html(
                titolo=card.get("titolo") or card.get("fronte") or "Concetto chiave",
                testo=card.get("testo") or card.get("retro") or "",
                materia=card.get("materia"),
                concetto=card.get("concetto"),
                uso=card.get("uso"),
            )
        )

    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_html(titolo_pagina)}</title>
<style>
body {{ margin:0; font-family:Arial,Helvetica,sans-serif; background:#020617; color:#f8fafc; }}
main {{ max-width:1180px; margin:0 auto; padding:42px 20px 70px; }}
h1 {{ font-size:clamp(34px,5vw,58px); margin:0 0 24px; }}
.cards-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(285px,1fr)); gap:18px; }}
.graphic-card {{ position:relative; overflow:hidden; border-radius:28px; padding:20px; background:linear-gradient(145deg,var(--card-primary),var(--card-secondary)); border:1px solid rgba(255,255,255,.16); box-shadow:0 26px 80px rgba(0,0,0,.34); min-height:430px; }}
.graphic-card::after {{ content:""; position:absolute; width:160px; height:160px; right:-60px; bottom:-60px; border-radius:50%; background:var(--card-accent); opacity:.13; }}
.graphic-card-badge {{ position:relative; z-index:2; display:inline-flex; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.16); color:#fff; font-size:12px; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }}
.graphic-card-image {{ position:relative; z-index:2; margin:18px 0 16px; }}
.card-illustration {{ width:100%; height:auto; display:block; }}
.graphic-card h2 {{ position:relative; z-index:2; font-size:22px; line-height:1.16; margin:0 0 12px; }}
.graphic-card p {{ position:relative; z-index:2; color:#f8fafc; line-height:1.55; font-size:15px; }}
.graphic-card small {{ position:relative; z-index:2; display:block; color:#e5e7eb; font-weight:800; line-height:1.45; margin-top:14px; }}
</style>
</head>
<body>
<main>
<h1>{safe_html(titolo_pagina)}</h1>
<section class="cards-grid">
{''.join(card_html)}
</section>
</main>
</body>
</html>'''


def demo_cards() -> list[dict[str, Any]]:
    return [
        {"materia":"cybersecurity","concetto":"backup","titolo":"Concetto chiave: Backup","testo":"Il backup crea copie dei dati per permettere il ripristino in caso di errore, guasto o attacco informatico."},
        {"materia":"cybersecurity","concetto":"password","titolo":"Concetto chiave: Password","testo":"La password protegge l'accesso a un sistema e deve essere forte, unica e gestita con attenzione."},
        {"materia":"informatica","concetto":"database","titolo":"Concetto chiave: Database","testo":"Un database organizza dati strutturati e permette di cercarli, aggiornarli e collegarli in modo controllato."},
        {"materia":"ai","concetto":"rag","titolo":"Concetto chiave: RAG","testo":"Il RAG combina recupero di documenti e generazione AI per produrre risposte più collegate alle fonti."},
        {"materia":"matematica","concetto":"derivata","titolo":"Concetto chiave: Derivata","testo":"La derivata descrive quanto rapidamente cambia una funzione in un punto e può essere vista come pendenza della tangente."},
        {"materia":"chimica","concetto":"molecola","titolo":"Concetto chiave: Molecola","testo":"Una molecola è formata da atomi legati tra loro e rappresenta una struttura fondamentale della chimica."},
        {"materia":"biologia","concetto":"dna","titolo":"Concetto chiave: DNA","testo":"Il DNA contiene informazioni genetiche e guida molti processi fondamentali degli organismi viventi."},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Motore grafico per card formative.")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--materia", default=None)
    parser.add_argument("--concetto", default=None)
    parser.add_argument("--titolo", default="Concetto chiave")
    parser.add_argument("--testo", default="Testo dimostrativo della card grafica.")
    parser.add_argument("--output", default="reports/demo_card_grafiche.html")
    args = parser.parse_args()

    output_path = (ROOT / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.demo:
        page = render_cards_page(demo_cards(), "Demo motore card grafiche")
    else:
        page = render_cards_page([{"materia":args.materia,"concetto":args.concetto,"titolo":args.titolo,"testo":args.testo}], "Card grafica generata")

    output_path.write_text(page, encoding="utf-8")
    print(f"✅ Card grafiche generate in: {output_path}")


if __name__ == "__main__":
    main()
