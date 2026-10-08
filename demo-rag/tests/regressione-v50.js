/* RAG V5.0 - regressioni senza dipendenze, eseguibile nella console del browser:
   RAGV50Regression.run()
   Non altera textarea, file o risultati dell'app.
*/
(function(root) {
  "use strict";
  const fixtures={
    oneHeading:"# INDUSTRIA\n## Le trasformazioni\n"+
      "Le fabbriche sostituirono le botteghe grazie all'utilizzo delle macchine industriali.\n"+
      "Il carbone forniva energia alle macchine a vapore impiegate nella produzione.\n"+
      "Le ferrovie accelerarono il trasporto delle merci e la circolazione delle persone.\n"+
      "Le città crebbero perché molti lavoratori abbandonarono le campagne.\n"+
      "Le condizioni di lavoro erano difficili per la durata prolungata degli orari.\n"+
      "L'elettricità trasformò la successiva fase dello sviluppo industriale.",
    contrast:"# CONFRONTO\n## Gruppi\n"+
      "Il campione A contiene il 20% di studenti e il 30% di lavoratori nel gruppo esaminato.\n"+
      "Il campione B contiene il 25% di studenti e il 30% di lavoratori nel gruppo esaminato.\n"+
      "Il campione C non contiene il 20% di studenti e il 30% di lavoratori nel gruppo esaminato.",
    decimals:"# ECONOMIA\n## Valori\n"+
      "Il tasso del gruppo A è 4.5% e quello del gruppo B è 4.8%.\n"+
      "La differenza è 0.3 punti percentuali e non equivale allo 0.3% del tasso.",
    steps:"# RICETTA\n## Preparazione\n"+
      "1. Versa acqua nella pentola.\n2. Aggiungi sale all'acqua.\n"+
      "3. Cuoci la pasta per 9 minuti.\n4. Scola la pasta con attenzione.",
    untitled:"Le api raccolgono nettare e polline dai fiori per portare nutrimento nel loro alveare.\n"+
      "La regina depone le uova mentre le operaie difendono la colonia.\n\n"+
      "L'alveare contiene celle esagonali di cera utilizzate per conservare il miele.\n"+
      "Le api comunicano la posizione dei fiori mediante una danza che indica la direzione.",
    biology:"# CICLO DELL'ACQUA\n## Evaporazione\n"+
      "Il Sole trasforma l'acqua dei mari in vapore che raggiunge gli strati dell'atmosfera.\n"+
      "## Condensazione\nIl vapore si raffredda e forma minuscole gocce che diventano nuvole.\n"+
      "## Pioggia\nLe gocce si uniscono e ricadono sulla superficie come precipitazioni.",
    rules:"# NORME\n## Accesso\n"+
      "I visitatori devono registrarsi prima di entrare negli spazi comuni riservati.\n"+
      "## Emergenze\nLe uscite devono rimanere libere per consentire una rapida evacuazione."
  };
  function run() {
    const api=root.RAGContentQualityV50;
    if(!api) return {passed:false,error:"Caricare prima rag-content-quality-v50.js"};
    const results=[];
    function test(name,success,description) {
      results.push({name,passed:!!success,description:description||""});
    }
    const one=api.analyze(fixtures.oneHeading);
    test("Più concetti da un solo capitolo",one?.concepts.length>=5,"Attese almeno 5 card");
    test("Riassunto copre tutte le parti",one?.summary.length>=3,"Attese almeno 3 parti");
    const diff=api.analyze(fixtures.contrast);
    test("20% e 25% distinti",diff?.concepts.some(x=>x.fatto.includes("20%"))&&
      diff?.concepts.some(x=>x.fatto.includes("25%")),"Nessun fatto numerico perso");
    test("Negazione conservata",diff?.concepts.some(x=>x.fatto.includes("non contiene")),"Differenza semantica mantenuta");
    const decimals=api.analyze(fixtures.decimals);
    test("Decimali intatti",decimals?.concepts.some(x=>x.fatto.includes("4.5%")&&x.fatto.includes("4.8%")));
    const steps=api.analyze(fixtures.steps);
    test("Quattro passaggi procedurali",steps?.concepts.length===4);
    test("Titoli Markdown mantenuti",one?.profile.materia==="INDUSTRIA");
    const free=api.analyze(fixtures.untitled);
    test("Senza titoli",free?.concepts.length>=3);
    let allValid=true,domains=0,quizProduced=0;
    for(const input of Object.values(fixtures)){
      const data=api.analyze(input);
      if(!data||!data.concepts.length||!data.summary.length)allValid=false;
      const quiz=api.makeQuiz(data);
      quizProduced+=quiz.length;
      for(const q of quiz) {
        if(q.options.length!==4||new Set(q.options.map(x=>x.toLowerCase())).size!==4||
           !q.options.includes(q.correct))allValid=false;
      }
      domains++;
    }
    test("Risultati per 7 strutture",allValid,"Materia, numeri, procedure, senza titoli");
    test("Quiz con opzioni uniche",quizProduced>=6,"Nessuna domanda con risposte duplicate");
    return {passed:results.every(x=>x.passed),count:results.length,failed:results.filter(x=>!x.passed),results,domains,quizProduced};
  }
  root.RAGV50Regression={run,fixtures};
})(window);
