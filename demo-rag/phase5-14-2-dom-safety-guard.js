/*
FASE 5.14.2 — DOM SAFETY GUARD

Evita che vecchi script di layout blocchino la pagina con:
HierarchyRequestError: appendChild - new child contains the parent.

Non genera output.
Non modifica i motori.
*/

(function () {
  "use strict";

  if (window.__phase5_14_2_dom_guard_installed__) return;
  window.__phase5_14_2_dom_guard_installed__ = true;

  const originalAppendChild = Node.prototype.appendChild;

  window.__phase5_14_2_dom_guard__ = {
    phase: "5.14.2",
    blockedAppendChild: 0,
    active: true
  };

  Node.prototype.appendChild = function phase5142SafeAppendChild(child) {
    try {
      if (
        child &&
        typeof child.contains === "function" &&
        child.contains(this)
      ) {
        window.__phase5_14_2_dom_guard__.blockedAppendChild += 1;
        console.warn(
          "[Phase 5.14.2] appendChild bloccato: il nuovo figlio contiene il parent.",
          { parent: this, child: child }
        );
        return child;
      }
    } catch (error) {
      console.warn("[Phase 5.14.2] DOM guard warning:", error);
    }

    return originalAppendChild.call(this, child);
  };

  console.log("[Phase 5.14.2] DOM safety guard attivo");
})();
