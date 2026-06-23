#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path


SCRIPT_TAG = '<script src="./pdf-export-cards.js"></script>'


def patch_html(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"File HTML non trovato: {path}")

    text = path.read_text(encoding="utf-8")

    if "pdf-export-cards.js" in text:
        print(f"Hook già presente in: {path}")
        return

    backup = path.with_suffix(path.suffix + ".backup_pdf_export_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup.write_text(text, encoding="utf-8")

    if "</body>" in text:
        text = text.replace("</body>", f"  {SCRIPT_TAG}\n</body>")
    else:
        text += "\n" + SCRIPT_TAG + "\n"

    path.write_text(text, encoding="utf-8")
    print(f"Hook aggiunto in: {path}")
    print(f"Backup: {backup}")


def main() -> None:
    target = Path("demo-rag/test-documenti-universale.html")
    patch_html(target)


if __name__ == "__main__":
    main()
