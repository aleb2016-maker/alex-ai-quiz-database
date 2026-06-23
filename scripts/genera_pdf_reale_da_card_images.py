#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def find_images(images_dir: Path) -> list[Path]:
    if not images_dir.exists():
        raise SystemExit(f"Cartella immagini non trovata: {images_dir}")

    images = [
        p for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    images.sort(key=lambda p: p.name.lower())

    if not images:
        raise SystemExit(f"Nessuna immagine card trovata in: {images_dir}")

    return images


def build_json(images: list[Path], json_path: Path, title: str) -> None:
    cards = []
    for index, image_path in enumerate(images, start=1):
        cards.append({
            "title": f"Card {index}",
            "badge": "CARD",
            "category": "card_renderizzata",
            "body": "Card immagine già generata dal motore.",
            "imagePath": str(image_path.resolve()),
            "points": [],
        })

    data = {
        "title": title,
        "subtitle": "PDF generato da immagini card già renderizzate.",
        "footer": "Alex AI Workspace - PDF image-only",
        "theme": "image-only",
        "cardsPerPage": 1,
        "cards": cards,
    }

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_pdf(project_root: Path, json_path: Path, output_pdf: Path) -> None:
    engine_dir = project_root / "java" / "rag-pdf-engine"
    runner = engine_dir / "scripts" / "run_from_json.sh"

    if not runner.exists():
        raise SystemExit(
            "Motore Java PDF non trovato.\n"
            f"Manca: {runner}\n"
            "Installa prima il pacchetto motore scarica PDF."
        )

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "bash",
        "scripts/run_from_json.sh",
        str(json_path.resolve()),
        str(output_pdf.resolve()),
    ]

    subprocess.run(cmd, cwd=engine_dir, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera un PDF Java image-only partendo da immagini card già renderizzate."
    )
    parser.add_argument("--images-dir", required=True, help="Cartella con card_01.png, card_02.png, ecc.")
    parser.add_argument("--output", required=True, help="PDF finale da creare.")
    parser.add_argument("--json-output", default="", help="Percorso JSON intermedio opzionale.")
    parser.add_argument("--title", default="PDF card generate dalla demo")
    parser.add_argument("--project-root", default=".", help="Root del progetto alex-ai-workspace")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    images_dir = Path(args.images_dir).resolve()
    output_pdf = Path(args.output).resolve()

    if args.json_output:
        json_path = Path(args.json_output).resolve()
    else:
        json_path = output_pdf.with_suffix(".json")

    images = find_images(images_dir)
    build_json(images, json_path, args.title)
    generate_pdf(project_root, json_path, output_pdf)

    print(f"OK immagini trovate: {len(images)}")
    print(f"JSON: {json_path}")
    print(f"PDF: {output_pdf}")


if __name__ == "__main__":
    main()
