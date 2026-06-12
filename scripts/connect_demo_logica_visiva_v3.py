from pathlib import Path
import re


APP_FILE = Path("demo/app.js")
STYLE_FILE = Path("demo/style.css")


def sostituisci_regex(testo, pattern, nuovo, descrizione):
    nuovo_testo, numero_sostituzioni = re.subn(
        pattern,
        nuovo,
        testo,
        count=1,
        flags=re.DOTALL,
    )

    if numero_sostituzioni == 0:
        raise RuntimeError(f"Blocco non trovato: {descrizione}")

    print("Aggiornato:", descrizione)
    return nuovo_testo


def aggiorna_app_js():
    testo = APP_FILE.read_text(encoding="utf-8")

    testo = sostituisci_regex(
        testo,
        r'const\s+categorieOrdinate\s*=\s*\[[\s\S]*?\];',
        '''const categorieOrdinate = [
        "ai",
        "informatica",
        "matematica",
        "inglese",
        "logica",
        "logica_visiva",
    ];''',
        "lista categorie con Logica Visiva",
    )

    testo = testo.replace(
        "return domanda.categoria === categoria;",
        "return domandaCorrispondeCategoria(domanda, categoria);",
    )

    testo = sostituisci_regex(
        testo,
        r'aggiungiOpzione\(\s*elementi\.categorySelect,\s*categoria,\s*formattaTesto\(categoria\)\s*\);',
        'aggiungiOpzione( elementi.categorySelect, categoria, formattaCategoriaFiltro(categoria) );',
        "nome visibile categoria nel menu",
    )

    testo = sostituisci_regex(
        testo,
        r'const\s+categoriaOk\s*=\s*categoriaScelta\s*===\s*"tutte"\s*\|\|\s*domanda\.categoria\s*===\s*categoriaScelta\s*;',
        'const categoriaOk = domandaCorrispondeCategoria(domanda, categoriaScelta);',
        "filtro categoria speciale",
    )

    if "function domandaCorrispondeCategoria" not in testo:
        funzioni_categoria = '''function domandaCorrispondeCategoria(domanda, categoriaScelta) {
    if (categoriaScelta === "tutte") {
        return true;
    }

    if (categoriaScelta === "logica_visiva") {
        return domanda.sottocategoria === "logica_visiva";
    }

    if (categoriaScelta === "logica") {
        return (
            domanda.categoria === "logica" &&
            domanda.sottocategoria !== "logica_visiva"
        );
    }

    return domanda.categoria === categoriaScelta;
}

function formattaCategoriaFiltro(categoria) {
    if (categoria === "logica_visiva") {
        return "Logica Visiva";
    }

    return formattaTesto(categoria);
}

'''

        testo = sostituisci_regex(
            testo,
            r'function\s+ottieniNumeroDomandeRichiesto\s*\(',
            funzioni_categoria + 'function ottieniNumeroDomandeRichiesto(',
            "funzioni per categoria speciale",
        )
    else:
        print("Funzioni categoria speciale già presenti")

    testo = sostituisci_regex(
        testo,
        r'elementi\.questionMeta\.textContent\s*=\s*`\$\{formattaTesto\(domanda\.categoria\)\} · `\s*\+\s*`\$\{formattaTesto\(domanda\.livello\)\}`\s*;',
        '''const categoriaMeta =
        domanda.sottocategoria === "logica_visiva"
            ? "Logica Visiva"
            : formattaTesto(domanda.categoria);

    elementi.questionMeta.textContent =
        `${categoriaMeta} · ${formattaTesto(domanda.livello)}`;''',
        "testo categoria durante il quiz",
    )

    APP_FILE.write_text(testo, encoding="utf-8")
    print("File aggiornato:", APP_FILE)


def aggiorna_style_css():
    testo = STYLE_FILE.read_text(encoding="utf-8")

    if "/* ===== LOGICA VISIVA SVG ===== */" in testo:
        print("CSS logica visiva già presente")
        return

    blocco_css = r'''

/* ===== LOGICA VISIVA SVG ===== */

.question-image-box {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 18px 0 20px;
    padding: 14px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.35);
}

.question-image-box img {
    display: block;
    width: 100%;
    max-width: 620px;
    max-height: 360px;
    object-fit: contain;
}

.option-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.option-button span {
    font-weight: 800;
}

.option-image {
    width: 100%;
    max-width: 150px;
    max-height: 150px;
    object-fit: contain;
    padding: 8px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.35);
}

.option-button.correct .option-image {
    border-color: rgba(34, 197, 94, 0.85);
}

.option-button.wrong .option-image {
    border-color: rgba(239, 68, 68, 0.85);
}

@media (max-width: 720px) {
    .question-image-box img {
        max-height: 300px;
    }

    .option-image {
        max-width: 120px;
        max-height: 120px;
    }
}
'''

    STYLE_FILE.write_text(testo + blocco_css, encoding="utf-8")
    print("File aggiornato:", STYLE_FILE)


def main():
    aggiorna_app_js()
    aggiorna_style_css()

    print("")
    print("----- DEMO LOGICA VISIVA COLLEGATA -----")
    print("Ora il menu deve mostrare anche: Logica Visiva")
    print("Nel filtro Logica normale saranno escluse le domande di Logica Visiva")


main()
