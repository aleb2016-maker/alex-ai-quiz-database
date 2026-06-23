#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import re

SCRIPT_TAG = '<script src="./pdf-export-browser-v6.js?v=6"></script>'


def patch_html(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"File HTML non trovato: {path}")

    text = path.read_text(encoding="utf-8")
    backup = path.with_suffix(path.suffix + ".backup_pdf_browser_v6_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup.write_text(text, encoding="utf-8")

    text = re.sub(
        r'\s*<script\s+src=["\']\.\/pdf-export-browser(?:-v\d+)?\.js(?:\?[^"\']*)?["\']\s*>\s*</script>',
        "",
        text
    )

    if SCRIPT_TAG not in text:
        if "</body>" in text:
            text = text.replace("</body>", f"  {SCRIPT_TAG}\n</body>")
        else:
            text += "\n" + SCRIPT_TAG + "\n"

    path.write_text(text, encoding="utf-8")
    print(f"Hook V6 installato in: {path}")
    print(f"Backup: {backup}")


def main() -> None:
    patch_html(Path("demo-rag/test-documenti-universale.html"))


if __name__ == "__main__":
    main()
