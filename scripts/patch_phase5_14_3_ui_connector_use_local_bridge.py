#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.14.3 — PATCH UI CONNECTOR USE LOCAL BRIDGE

Modifica:
- demo-rag/phase5-14-ui-buttons-real-connector.js

Comportamento:
- prima prova funzioni browser reali;
- se non esistono, chiama bridge locale Python:
  http://127.0.0.1:8765/api/generate

Non usa fallback/demo.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "demo-rag" / "phase5-14-ui-buttons-real-connector.js"

text = JS.read_text(encoding="utf-8")

if "phase5LocalBackendBridgeGenerate" not in text:
    insert_after = '''  function findRealMotor(kind) {
    const candidates = MOTOR_CANDIDATES[kind] || [];

    for (const name of candidates) {
      if (typeof window[name] === "function") {
        return { name, fn: window[name] };
      }
    }

    return null;
  }

'''

    bridge_block = '''  async function phase5LocalBackendBridgeGenerate(kind, inputText) {
    const response = await fetch("http://127.0.0.1:8765/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        kind,
        text: inputText,
        strictNoFallback: true,
        source: "phase5-14-ui"
      })
    });

    const payload = await response.json();

    if (!response.ok || !payload.ok) {
      throw new Error(
        "Bridge locale backend non ha prodotto output valido: " +
        (payload.error || response.status)
      );
    }

    return payload;
  }

'''

    if insert_after not in text:
      raise SystemExit("FAIL - anchor findRealMotor non trovato nel connector JS")

    text = text.replace(insert_after, insert_after + bridge_block, 1)

old = '''    if (!motor) {
      renderError(
        kind,
        "Nessuna funzione browser reale trovata per " + kind +
        ". Serve agganciare questa pagina al bridge/engine reale, non a fallback."
      );
      return;
    }

    try {
      const result = await motor.fn(inputText, {
        phase: PHASE,
        kind,
        strictNoFallback: true,
        source: "ui-button"
      });

      renderOutput(kind, result, motor.name);
    } catch (error) {
      renderError(kind, error && error.stack ? error.stack : String(error));
    }
'''

new = '''    try {
      if (motor) {
        const result = await motor.fn(inputText, {
          phase: PHASE,
          kind,
          strictNoFallback: true,
          source: "ui-button"
        });

        renderOutput(kind, result, motor.name);
        return;
      }

      const bridgePayload = await phase5LocalBackendBridgeGenerate(kind, inputText);
      renderOutput(kind, bridgePayload.result, "local_backend_bridge_8765");

    } catch (error) {
      renderError(kind, error && error.stack ? error.stack : String(error));
    }
'''

if old not in text:
    raise SystemExit("FAIL - blocco !motor non trovato nel connector JS")

text = text.replace(old, new, 1)

JS.write_text(text, encoding="utf-8")

print("PASS - Fase 5.14.3: UI connector ora usa bridge locale backend se non trova funzioni browser")
