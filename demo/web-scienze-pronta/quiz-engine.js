(function (global) {
  class QuizEngine {
    constructor(questions) {
      this.allQuestions = Array.isArray(questions) ? questions : [];
      this.activeQuestions = [];
      this.currentIndex = 0;
      this.score = 0;
      this.answeredCount = 0;
    }

    startQuiz({ categoria = "tutte", livello = "tutti", numeroDomande = 10 } = {}) {
      const filtered = this.allQuestions
        .filter((question) => this.categoryMatches(question, categoria))
        .filter((question) => livello === "tutti" || question.livello === livello);

      this.activeQuestions = this.shuffle(filtered);

      if (numeroDomande > 0) {
        this.activeQuestions = this.activeQuestions.slice(0, numeroDomande);
      }

      this.currentIndex = 0;
      this.score = 0;
      this.answeredCount = 0;

      return this.activeQuestions;
    }

    currentQuestion() {
      return this.activeQuestions[this.currentIndex] || null;
    }

    answer(selectedAnswer) {
      const question = this.currentQuestion();

      if (!question) {
        throw new Error("Nessuna domanda attiva.");
      }

      const isCorrect = selectedAnswer === question.risposta_corretta;

      if (isCorrect) {
        this.score += 1;
      }

      this.answeredCount += 1;

      return {
        isCorrect,
        selectedAnswer,
        correctAnswer: question.risposta_corretta,
        explanation: question.spiegazione || "Spiegazione non disponibile.",
        score: this.score,
        totalAnswered: this.answeredCount,
      };
    }

    moveNext() {
      this.currentIndex += 1;
      return this.currentQuestion();
    }

    hasNext() {
      return this.currentIndex < this.activeQuestions.length - 1;
    }

    progressText() {
      if (!this.activeQuestions.length) {
        return "0/0";
      }

      return `${this.currentIndex + 1}/${this.activeQuestions.length}`;
    }

    categoryMatches(question, categoria) {
      const selected = this.slug(categoria);

      if (selected === "tutte") {
        return true;
      }

      const category = this.slug(question.categoria);
      const subcategory = this.slug(question.sottocategoria);
      const tags = Array.isArray(question.tags)
        ? question.tags.map((tag) => this.slug(tag))
        : [];

      if (selected === category || selected === subcategory || tags.includes(selected)) {
        return true;
      }

      if (selected === "fisica") {
        return subcategory.includes("fisica") || tags.some((tag) => tag.includes("fisica"));
      }

      if (selected === "chimica") {
        return subcategory.includes("chimica") || tags.some((tag) => tag.includes("chimica"));
      }

      if (selected === "biologia") {
        return subcategory.includes("biologia") || tags.some((tag) => tag.includes("biologia"));
      }

      return false;
    }

    shuffle(array) {
      const copy = [...array];

      for (let index = copy.length - 1; index > 0; index--) {
        const randomIndex = Math.floor(Math.random() * (index + 1));
        [copy[index], copy[randomIndex]] = [copy[randomIndex], copy[index]];
      }

      return copy;
    }

    slug(text) {
      return String(text || "")
        .trim()
        .toLowerCase()
        .replace(/[àá]/g, "a")
        .replace(/[èé]/g, "e")
        .replace(/[ìí]/g, "i")
        .replace(/[òó]/g, "o")
        .replace(/[ùú]/g, "u")
        .replace(/\s+/g, "_")
        .replace(/-/g, "_");
    }
  }

  class QuizQualityValidator {
    static validate(questions) {
      const issues = [];
      const ids = new Set();

      questions.forEach((question, index) => {
        const id = question.id || `QUESTION_${index + 1}`;

        if (!question.id) {
          issues.push({ questionId: id, severity: "warning", message: "ID mancante." });
        }

        if (question.id && ids.has(question.id)) {
          issues.push({ questionId: id, severity: "error", message: "ID duplicato." });
        }

        ids.add(question.id);

        if (!question.categoria) {
          issues.push({ questionId: id, severity: "error", message: "Categoria mancante." });
        }

        if (!question.livello) {
          issues.push({ questionId: id, severity: "error", message: "Livello mancante." });
        }

        if (!question.domanda) {
          issues.push({ questionId: id, severity: "error", message: "Testo domanda mancante." });
        }

        if (!Array.isArray(question.opzioni) || question.opzioni.length !== 4) {
          issues.push({ questionId: id, severity: "error", message: "La domanda deve avere 4 opzioni." });
        }

        if (Array.isArray(question.opzioni) && new Set(question.opzioni).size !== question.opzioni.length) {
          issues.push({ questionId: id, severity: "error", message: "Opzioni duplicate." });
        }

        if (!question.risposta_corretta) {
          issues.push({ questionId: id, severity: "error", message: "Risposta corretta mancante." });
        }

        if (Array.isArray(question.opzioni) && !question.opzioni.includes(question.risposta_corretta)) {
          issues.push({ questionId: id, severity: "error", message: "Risposta corretta non presente tra le opzioni." });
        }

        if (!question.spiegazione) {
          issues.push({ questionId: id, severity: "warning", message: "Spiegazione mancante." });
        }
      });

      return issues;
    }

    static hasBlockingErrors(questions) {
      return this.validate(questions).some((issue) => issue.severity === "error");
    }
  }

  global.AlexQuizEngine = {
    QuizEngine,
    QuizQualityValidator,
  };
})(window);
