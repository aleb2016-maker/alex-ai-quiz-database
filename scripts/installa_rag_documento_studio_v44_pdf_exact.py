#!/usr/bin/env python3
from pathlib import Path
import argparse

HTML_REL = Path("demo-rag/test-rag-documento-studio-v44.html")

def patch_html(root: Path) -> None:
    html = root / HTML_REL
    if not html.exists():
        raise SystemExit(f"ERRORE: manca {html}. Installa prima V4.4 Auto Flow.")

    text = html.read_text(encoding="utf-8")

    css_tag = '<link rel="stylesheet" href="rag-documento-studio-v44-pdf-exact.css">'
    js_tag = '<script src="rag-documento-studio-v44-pdf-exact.js"></script>'

    if "rag-documento-studio-v44-pdf-exact.css" not in text:
        if "</head>" in text:
            text = text.replace("</head>", f"  {css_tag}\n</head>")
        else:
            text = css_tag + "\n" + text

    if "rag-documento-studio-v44-pdf-exact.js" not in text:
        if "</body>" in text:
            text = text.replace("</body>", f"  {js_tag}\n</body>")
        else:
            text += "\n" + js_tag + "\n"

    html.write_text(text, encoding="utf-8")
    print(f"OK patch HTML: {html}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    patch_html(root)
    print()
    print("✅ PDF exact capture installato")
    print("📌 Avvio:")
    print("   python3 -m http.server 8000")
    print("🌐 URL:")
    print("   http://localhost:8000/demo-rag/test-rag-documento-studio-v44.html")
    print("🔄 Hard refresh: Cmd + Shift + R")
    print("🧪 Verifica:")
    print("   python3 scripts/verifica_rag_documento_studio_v44_pdf_exact.py")

if __name__ == "__main__":
    main()
