from pathlib import Path


PERCORSO_SCRIPT = Path("scripts/review_option_structure.py")


vecchio_blocco = '''        if somiglianza_ab < 0.18:
            problemi.append(
                f"Il distrattore B sembra poco vicino alla risposta corretta. Somiglianza A/B: {somiglianza_ab}"
            )

        if somiglianza_ab + 0.08 < max(somiglianza_ac, somiglianza_ad):
            problemi.append(
                "Il distrattore B non sembra più vicino alla corretta rispetto a C/D."
            )

        if somiglianza_cd < 0.16:
            problemi.append(
                f"I distrattori C e D sembrano poco vicini tra loro. Somiglianza C/D: {somiglianza_cd}"
            )
'''


nuovo_blocco = '''        opzioni_molto_brevi = all(
            len(estrai_token(opzione)) <= 2
            for opzione in opzioni
        )

        if not opzioni_molto_brevi:
            if somiglianza_ab < 0.10:
                problemi.append(
                    f"Il distrattore B sembra poco vicino alla risposta corretta. Somiglianza A/B: {somiglianza_ab}"
                )

            if somiglianza_cd < 0.09:
                problemi.append(
                    f"I distrattori C e D sembrano poco vicini tra loro. Somiglianza C/D: {somiglianza_cd}"
                )
'''


def main():
    contenuto = PERCORSO_SCRIPT.read_text(encoding="utf-8")

    if vecchio_blocco not in contenuto:
        print("Blocco da sostituire non trovato.")
        print("Non ho modificato il file.")
        return

    nuovo_contenuto = contenuto.replace(
        vecchio_blocco,
        nuovo_blocco
    )

    PERCORSO_SCRIPT.write_text(
        nuovo_contenuto,
        encoding="utf-8"
    )

    print("Controllo struttura opzioni aggiornato alla versione V2.")
    print("File modificato:")
    print(PERCORSO_SCRIPT)


main()