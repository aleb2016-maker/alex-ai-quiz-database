(function (global) {
  class QuizEngine {
    constructor(questions) {
      this.allQuestions = Array.isArray(questions) ? questions : [];
      this.activeQuestions = [];
      this.currentIndex = 0;
      this.score = 0;
      this.answeredCount = 0;
      this.selectedAnswers = new Map();
    }

    startQuiz({ categoria = "tutte", livello = "tutti", numeroDomande = 10 } = {}) {
      const filteredQuestions = this.allQuestions
        .filter((question) => this.categoryMatches(question, categoria))
        .filter((question) => this.levelMatches(question, livello));

      this.activeQuestions = this.shuffle(filteredQuestions);

      if (numeroDomande > 0) {
        this.activeQuestions = this.activeQuestions.slice(0, numeroDomande);
      }

      this.currentIndex = 0;
      this.score = 0;
      this.answeredCount = 0;
      this.selectedAnswers.clear();

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

      const options = this.readOptions(question);
      const correctAnswer = this.readCorrectAnswer(question);
      const answerKey = question.id || `QUESTION_${this.currentIndex}`;

      if (!options.includes(selectedAnswer)) {
        throw new Error("La risposta selezionata non è tra le opzioni della domanda.");
      }

      if (this.selectedAnswers.has(answerKey)) {
        throw new Error("Questa domanda ha già ricevuto una risposta.");
      }

      const isCorrect = selectedAnswer === correctAnswer;

      if (isCorrect) {
        this.score += 1;
      }

      this.answeredCount += 1;
      this.selectedAnswers.set(answerKey, selectedAnswer);

      return {
        isCorrect,
        selectedAnswer,
        correctAnswer,
        explanation: question.spiegazione || question.explanation || "Spiegazione non disponibile.",
        score: this.score,
        totalAnswered: this.answeredCount,
        totalQuestions: this.activeQuestions.length,
      };
    }

    moveNext() {
      if (this.hasNext()) {
        this.currentIndex += 1;
      }

      return this.currentQuestion();
    }

    hasNext() {
      return this.currentIndex < this.activeQuestions.length - 1;
    }

    isFinished() {
      return this.activeQuestions.length > 0 && this.answeredCount >= this.activeQuestions.length;
    }

    progressText() {
      if (!this.activeQuestions.length) {
        return "0/0";
      }

      return `${this.currentIndex + 1}/${this.activeQuestions.length}`;
    }

    summary() {
      const total = this.activeQuestions.length;
      const percentage = ScoreEngine.percentage(this.score, total);
      const label = ScoreEngine.label(this.score, total);

      return {
        score: this.score,
        totalQuestions: total,
        percentage,
        label,
        finalMessage: ScoreEngine.finalMessage(this.score, total),
      };
    }

    availableCategories() {
      return [...new Set(
        this.allQuestions
          .map((question) => question.categoria || question.category || "")
          .filter(Boolean)
      )].sort();
    }

    availableLevels() {
      return [...new Set(
        this.allQuestions
          .map((question) => question.livello || question.difficulty || "")
          .filter(Boolean)
      )].sort();
    }

    categoryMatches(question, categoria) {
      const selectedCategory = this.slug(categoria);

      if (selectedCategory === "tutte") {
        return true;
      }

      const questionCategory = this.slug(question.categoria || question.category);
      const questionSubcategory = this.slug(question.sottocategoria || question.subcategory);
      const questionTags = Array.isArray(question.tags)
        ? question.tags.map((tag) => this.slug(tag))
        : [];

      if (
        selectedCategory === questionCategory ||
        selectedCategory === questionSubcategory ||
        questionTags.includes(selectedCategory)
      ) {
        return true;
      }

      if (selectedCategory === "fisica") {
        return questionSubcategory.includes("fisica") ||
          questionTags.some((tag) => tag.includes("fisica"));
      }

      if (selectedCategory === "chimica") {
        return questionSubcategory.includes("chimica") ||
          questionTags.some((tag) => tag.includes("chimica"));
      }

      if (selectedCategory === "biologia") {
        return questionSubcategory.includes("biologia") ||
          questionTags.some((tag) => tag.includes("biologia"));
      }

      return false;
    }

    levelMatches(question, livello) {
      const selectedLevel = this.slug(livello);

      if (selectedLevel === "tutti") {
        return true;
      }

      return this.slug(question.livello || question.difficulty) === selectedLevel;
    }

    readOptions(question) {
      if (Array.isArray(question.opzioni)) {
        return question.opzioni;
      }

      if (Array.isArray(question.options)) {
        return question.options;
      }

      return [];
    }

    readCorrectAnswer(question) {
      return question.risposta_corretta || question.correct_answer || question.answer || "";
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

      if (!Array.isArray(questions) || questions.length === 0) {
        return [
          {
            questionId: "DATABASE",
            severity: "error",
            message: "Il database non contiene domande.",
          },
        ];
      }

      questions.forEach((question, index) => {
        const id = question.id || `QUESTION_${index + 1}`;
        const options = this.readOptions(question);
        const correctAnswer = question.risposta_corretta || question.correct_answer || question.answer;

        if (!question.id) {
          issues.push({ questionId: id, severity: "warning", message: "ID mancante." });
        }

        if (question.id && ids.has(question.id)) {
          issues.push({ questionId: id, severity: "error", message: "ID duplicato." });
        }

        if (question.id) {
          ids.add(question.id);
        }

        if (!(question.categoria || question.category)) {
          issues.push({ questionId: id, severity: "error", message: "Categoria mancante." });
        }

        if (!(question.livello || question.difficulty)) {
          issues.push({ questionId: id, severity: "error", message: "Livello mancante." });
        }

        if (!(question.domanda || question.question)) {
          issues.push({ questionId: id, severity: "error", message: "Testo domanda mancante." });
        }

        if (options.length !== 4) {
          issues.push({ questionId: id, severity: "error", message: "La domanda deve avere 4 opzioni." });
        }

        if (options.some((option) => !String(option || "").trim())) {
          issues.push({ questionId: id, severity: "error", message: "Una o più opzioni sono vuote." });
        }

        if (new Set(options).size !== options.length) {
          issues.push({ questionId: id, severity: "error", message: "Opzioni duplicate." });
        }

        if (!correctAnswer) {
          issues.push({ questionId: id, severity: "error", message: "Risposta corretta mancante." });
        }

        if (correctAnswer && !options.includes(correctAnswer)) {
          issues.push({ questionId: id, severity: "error", message: "Risposta corretta non presente tra le opzioni." });
        }

        if (!(question.spiegazione || question.explanation)) {
          issues.push({ questionId: id, severity: "warning", message: "Spiegazione mancante." });
        }

        if (!(question.distrattore_forte || question.strong_distractor)) {
          issues.push({ questionId: id, severity: "warning", message: "Distrattore forte non indicato." });
        }
      });

      return issues;
    }

    static blockingErrors(questions) {
      return this.validate(questions).filter((issue) => issue.severity === "error");
    }

    static hasBlockingErrors(questions) {
      return this.blockingErrors(questions).length > 0;
    }

    static readOptions(question) {
      if (Array.isArray(question.opzioni)) {
        return question.opzioni;
      }

      if (Array.isArray(question.options)) {
        return question.options;
      }

      return [];
    }
  }

  class ScoreEngine {
    static percentage(score, total) {
      if (!total || total <= 0) {
        return 0;
      }

      return Math.trunc((score / total) * 100);
    }

    static label(score, total) {
      const percentage = this.percentage(score, total);

      if (percentage >= 100) return "Eccellente";
      if (percentage >= 95) return "Ottimo";
      if (percentage >= 90) return "Distinto";
      if (percentage >= 80) return "Buono";
      if (percentage >= 70) return "Discreto";
      if (percentage >= 60) return "Sufficiente";

      return "Da migliorare";
    }

    static finalMessage(score, total) {
      return `Risultato: ${score}/${total} - ${this.label(score, total)}`;
    }
  }

  global.AlexQuizEngine = {
    QuizEngine,
    QuizQualityValidator,
    ScoreEngine,
  };
})(window);
