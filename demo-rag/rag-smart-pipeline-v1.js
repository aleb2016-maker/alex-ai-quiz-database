(function () {
  "use strict";

  const VERSION = "rag-smart-pipeline-v1";

  function requireGlobal(name) {
    if (!window[name]) {
      throw new Error(`Modulo mancante: ${name}`);
    }
    return window[name];
  }

  function textFromDocumentInput(documentInput) {
    return documentInput && documentInput.text ? documentInput.text.clean || documentInput.text.original || "" : "";
  }

  async function createDocumentFromText(text, title, sourceType) {
    const DocumentInput = requireGlobal("RagDocumentInputUnicoV1");
    return DocumentInput.fromText(text, title || "Documento utente", sourceType || "manuale");
  }

  async function createDocumentFromFile(file) {
    const DocumentInput = requireGlobal("RagDocumentInputUnicoV1");
    return DocumentInput.fromFile(file);
  }

  function buildKnowledge(documentInput, options) {
    const Extractors = requireGlobal("RagKnowledgeExtractorsV1");
    return Extractors.buildKnowledgeBase(documentInput, options || {});
  }

  function buildPlan(knowledgeBase) {
    const Planner = requireGlobal("RagDidacticPlannerV1");
    return Planner.buildPlan(knowledgeBase);
  }

  function generateOutput(knowledgeBase, plan) {
    const Generator = requireGlobal("RagKnowledgeLinkedGeneratorV1");
    return Generator.generateAll(knowledgeBase, plan);
  }

  function validate(documentInput, knowledgeBase, output) {
    const Validator = requireGlobal("RagGeneralValidatorV1");
    return Validator.validateAll({
      kb: knowledgeBase,
      output,
      documentText: textFromDocumentInput(documentInput)
    });
  }

  async function runFromText(text, title, options) {
    const documentInput = await createDocumentFromText(text, title, "manuale");
    const knowledgeBase = buildKnowledge(documentInput, options);
    const plan = buildPlan(knowledgeBase);
    const output = generateOutput(knowledgeBase, plan);
    const validation = validate(documentInput, knowledgeBase, output);

    return {
      version: VERSION,
      createdAt: new Date().toISOString(),
      documentInput,
      knowledgeBase,
      plan,
      output,
      validation
    };
  }

  async function runFromFile(file, options) {
    const documentInput = await createDocumentFromFile(file);
    if (documentInput.reading.status !== "loaded") {
      return {
        version: VERSION,
        createdAt: new Date().toISOString(),
        documentInput,
        knowledgeBase: null,
        plan: null,
        output: null,
        validation: {
          valid: false,
          score: 0,
          errors: documentInput.reading.errors || ["documento_non_letto"],
          warnings: documentInput.reading.warnings || []
        }
      };
    }

    const knowledgeBase = buildKnowledge(documentInput, options);
    const plan = buildPlan(knowledgeBase);
    const output = generateOutput(knowledgeBase, plan);
    const validation = validate(documentInput, knowledgeBase, output);

    return {
      version: VERSION,
      createdAt: new Date().toISOString(),
      documentInput,
      knowledgeBase,
      plan,
      output,
      validation
    };
  }

  function renderCards(cards, container) {
    const target = typeof container === "string" ? document.querySelector(container) : container;
    if (!target) return;
    const safeCards = Array.isArray(cards) ? cards : [];
    target.innerHTML = safeCards.map((card) => `
      <article class="rag-smart-card" data-confidence="${card.confidence || 0}">
        <div class="rag-smart-card-badge">${escapeHtml(card.badge || "concetto")}</div>
        <h3>${escapeHtml(card.title || "Card")}</h3>
        <p>${escapeHtml(card.body || "")}</p>
        ${card.evidence ? `<details><summary>Prova nel documento</summary><small>${escapeHtml(card.evidence)}</small></details>` : ""}
      </article>
    `).join("");
  }

  function renderSummary(summary, container) {
    const target = typeof container === "string" ? document.querySelector(container) : container;
    if (!target || !summary) return;
    target.innerHTML = `
      <section class="rag-smart-summary">
        <h3>${escapeHtml(summary.title || "Riassunto")}</h3>
        <p>${escapeHtml(summary.intro || "")}</p>
        <ul>
          ${(summary.keyPoints || []).map((point) => `<li><strong>${escapeHtml(point.title || "Punto")}</strong>: ${escapeHtml(point.text || "")}</li>`).join("")}
        </ul>
      </section>
    `;
  }

  function renderStudyQuestions(questions, container) {
    const target = typeof container === "string" ? document.querySelector(container) : container;
    if (!target) return;
    target.innerHTML = (questions || []).map((question) => `
      <article class="rag-smart-question">
        <h4>${escapeHtml(question.question || "Domanda")}</h4>
        <p>${escapeHtml(question.answer || "")}</p>
        ${question.evidence ? `<details><summary>Prova</summary><small>${escapeHtml(question.evidence)}</small></details>` : ""}
      </article>
    `).join("");
  }

  function renderTest(test, container) {
    const target = typeof container === "string" ? document.querySelector(container) : container;
    if (!target) return;
    target.innerHTML = (test || []).map((question, questionIndex) => `
      <article class="rag-smart-test-question">
        <h4>${questionIndex + 1}. ${escapeHtml(question.question || "Domanda")}</h4>
        <div class="rag-smart-options">
          ${(question.options || []).map((option) => `<button type="button" data-answer="${escapeHtml(option)}" data-correct="${escapeHtml(question.correctAnswer)}">${escapeHtml(option)}</button>`).join("")}
        </div>
        <p class="rag-smart-feedback" hidden></p>
      </article>
    `).join("");

    target.querySelectorAll("button[data-answer]").forEach((button) => {
      button.addEventListener("click", () => {
        const article = button.closest("article");
        const feedback = article.querySelector(".rag-smart-feedback");
        const correct = button.getAttribute("data-correct");
        const answer = button.getAttribute("data-answer");
        feedback.hidden = false;
        feedback.textContent = answer === correct ? "Corretto." : `Non corretto. Risposta corretta: ${correct}`;
      });
    });
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.RagSmartPipelineV1 = {
    VERSION,
    runFromText,
    runFromFile,
    createDocumentFromText,
    createDocumentFromFile,
    buildKnowledge,
    buildPlan,
    generateOutput,
    validate,
    renderCards,
    renderSummary,
    renderStudyQuestions,
    renderTest,
    escapeHtml
  };
})();
