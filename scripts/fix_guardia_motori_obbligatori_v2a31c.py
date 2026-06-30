from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
target = ROOT / "demo-rag" / "universal-document-learning-engine.js"

report_dir = ROOT / "reports" / "fix_guardia_motori_obbligatori_v2a31c"
backup_dir = report_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

txt = target.read_text(encoding="utf-8")

backup = backup_dir / f"universal-document-learning-engine.js.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
backup.write_text(txt, encoding="utf-8")

start_marker = "function verificaMotoriObbligatoriV2A16(azione) {"
end_marker = "function registraUsoMotoriV2A16"

start = txt.find(start_marker)
if start == -1:
    raise SystemExit("ERRORE: non trovo verificaMotoriObbligatoriV2A16")

end = txt.find(end_marker, start)
if end == -1:
    raise SystemExit("ERRORE: non trovo registraUsoMotoriV2A16 dopo verificaMotoriObbligatoriV2A16")

new_guard = r'''function verificaMotoriObbligatoriV2A16(azione) {
  /*
   * V2A31C
   * La vecchia guardia V2A16 bloccava il pulsante anche quando i motori esistevano
   * nello scope reale del file, ma non venivano letti correttamente come export globali.
   * Questo controllo verifica sia lo scope locale sia window, senza bypassare motori mancanti.
   */
  const root = typeof window !== "undefined" ? window : {};
  const registry = root.__ragMotoriObbligatoriV2A31B || {};

  const locali = {
    profiliDocumento: typeof profiliDocumento !== "undefined" ? profiliDocumento : null,
    riconosciTema: typeof riconosciTema === "function" ? riconosciTema : null,
    creaCards: typeof creaCards === "function" ? creaCards : null,
    generaRiassunto: typeof generaRiassunto === "function" ? generaRiassunto : null
  };

  const base = [
    ["profiliDocumento", "profili documento: poesia, storia, curriculum, aziendale, personale, hobby, sport"],
    ["riconosciTema", "motore riconoscimento tema/documento"],
    ["creaCards", "motore card/concetti/sezioni"]
  ];

  const perAzione = {
    riassunto: [
      ["generaRiassunto", "funzione riassunto principale"],
      ["creaCards", "riassunto agganciato a card, profilo e sezioni"]
    ],
    card: [
      ["creaCards", "generatore card ufficiale"]
    ],
    test: [
      ["creaCards", "test agganciato a concetti/card ufficiali"]
    ],
    domande: [
      ["creaCards", "domande studio agganciate a concetti/card ufficiali"]
    ]
  };

  const richiesti = base.concat(perAzione[azione] || []);
  const mancanti = [];

  richiesti.forEach(function (item) {
    const nome = item[0];
    const descrizione = item[1];

    const valoreLocale = locali[nome];
    const valoreWindow = root[nome];
    const valoreRegistry = registry[nome];

    const ok = !!valoreLocale || !!valoreWindow || !!valoreRegistry;

    if (!ok) {
      mancanti.push("- " + nome + " -> " + descrizione);
    }
  });

  if (mancanti.length) {
    const messaggio =
      "Blocco V2A.16: pulsante non agganciato ai motori obbligatori.\n\n" +
      "Azione: " + azione + "\n\n" +
      "Motori mancanti:\n" +
      mancanti.join("\n");

    if (typeof alert === "function") {
      alert(messaggio);
    }

    throw new Error(messaggio);
  }

  if (typeof window !== "undefined") {
    window.__ultimoControlloMotoriObbligatoriV2A31C = {
      ok: true,
      azione: azione,
      motori: richiesti.map(function (item) { return item[0]; })
    };
  }

  return true;
}

'''

txt = txt[:start] + new_guard + txt[end:]

target.write_text(txt, encoding="utf-8")

report = report_dir / "report_fix_guardia_motori_obbligatori_v2a31c.md"
report.write_text(
    "# Fix guardia motori obbligatori V2A31C\n\n"
    "- Sostituita la guardia V2A16 con controllo locale + window + registry.\n"
    "- Non bypassa motori assenti: controlla che esistano davvero.\n"
    "- Obiettivo: eliminare il blocco falso sul pulsante Genera riassunto.\n"
    "- Non modificati HTML, CSS, PDF, card, test, domande studio.\n"
    f"- Backup: {backup}\n",
    encoding="utf-8"
)

print("OK V2A31C: guardia motori obbligatori corretta.")
print(f"Backup creato: {backup}")
print(f"Report scritto: {report}")
