const stopwords = new Set(["che","con","per","del","della","dello","delle","degli","dei","alla","allo","alle","agli","una","uno","anche","sono","non","nel","nella","nelle","negli","questo","questa","questi","queste","come","piu","più","viene","essere","può","puo","quindi","tra","fra","gli","sul","sulla","dai","dal","dalle","ad","ed"]);
const fileInput = document.getElementById("fileInput");
const titleInput = document.getElementById("titleInput");
const generateButton = document.getElementById("generateButton");
const statusBox = document.getElementById("statusBox");
const outputBox = document.getElementById("outputBox");

if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
}

function setStatus(message, type = "info") { statusBox.textContent = message; statusBox.className = `status ${type}`; }
function cleanText(text) { return text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim(); }
function splitSentences(text) { return text.replace(/\s+/g, " ").trim().split(/(?<=[.!?])\s+(?=[A-ZÀ-Ü0-9])/).map(s => s.trim()).filter(s => s.length >= 35); }
function tokenize(text) { return (text.toLowerCase().match(/[a-zà-öø-ÿ0-9]{3,}/g) || []).filter(w => !stopwords.has(w) && !/^\d+$/.test(w)); }
function escapeHtml(value) { return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;"); }
function shorten(text, limit = 220) { const compact = text.replace(/\s+/g, " ").trim(); return compact.length <= limit ? compact : compact.slice(0, limit).replace(/\s+\S*$/, "") + "..."; }
function extractKeywords(text, limit = 24) { const counts = new Map(); for (const w of tokenize(text)) counts.set(w, (counts.get(w) || 0) + 1); return [...counts.entries()].sort((a,b)=>b[1]-a[1]).slice(0,limit).map(([parola,frequenza])=>({parola,frequenza})); }
function scoreSentence(sentence, keyMap) { const words = tokenize(sentence); if (!words.length) return 0; const base = words.reduce((t,w)=>t+(keyMap.get(w)||0),0); return base / (1 + Math.abs(words.length - 28) / 65); }
function makeSummary(sentences, keywords, max = 8) { const keyMap = new Map(keywords.map(i => [i.parola, i.frequenza])); return sentences.map((s,i)=>({s,i,score:scoreSentence(s,keyMap)})).sort((a,b)=>b.score-a.score).slice(0,max).sort((a,b)=>a.i-b.i).map(i=>i.s); }
function contextFor(word, sentences) { const low = word.toLowerCase(); return sentences.find(s => s.toLowerCase().includes(low)) || sentences[0] || ""; }
function makeRows(keywords, sentences, limit = 14) { const max = Math.max(...keywords.map(k=>k.frequenza), 1); return keywords.slice(0,limit).map(k => ({ concetto:k.parola, frequenza:k.frequenza, importanza:Math.max(1, Math.min(5, Math.ceil((k.frequenza/max)*5))), spiegazione:shorten(contextFor(k.parola, sentences), 260) })); }
function makeCards(rows, limit = 12) { return rows.slice(0,limit).map((r,i)=>({ id:`RAG-CARD-${String(i+1).padStart(4,"0")}`, fronte:`Concetto chiave: ${r.concetto}`, retro:r.spiegazione, uso:"Ripassa questo punto e prova a rispiegarlo con parole tue." })); }
function makeQuiz(rows, limit = 10) { const contexts = rows.map(r => r.spiegazione); return rows.slice(0,limit).map((r,i)=>{ const correct = shorten(r.spiegazione, 180); const distractors = contexts.map(c=>shorten(c,180)).filter(c=>c && c!==correct).slice(0,3); while (distractors.length < 3) distractors.push(`Il documento cita ${r.concetto}, ma con una relazione diversa da quella corretta.`); const correctIndex = i % 4; const options = [...distractors]; options.splice(correctIndex,0,correct); return { id:`RAG-QUIZ-${String(i+1).padStart(4,"0")}`, categoria:"rag", livello:"intermedio", domanda:`Quale affermazione descrive meglio il concetto “${r.concetto}” secondo il documento?`, opzioni:options, risposta_corretta:correct, indice_risposta_corretta:correctIndex, spiegazione:`La risposta corretta riprende il modo in cui il documento collega “${r.concetto}” al contenuto principale.` }; }); }
async function readPdfText(file) { if (!window.pdfjsLib) throw new Error("PDF.js non disponibile. Per PDF usa lo script Python del pacchetto."); const buffer = await file.arrayBuffer(); const pdf = await pdfjsLib.getDocument({data: buffer}).promise; const pages = []; for (let n=1; n<=pdf.numPages; n++) { const page = await pdf.getPage(n); const content = await page.getTextContent(); pages.push(`[Pagina ${n}]\n` + content.items.map(item => item.str).join(" ")); } return pages.join("\n\n"); }
async function readUploadedFile(file) { return file.name.toLowerCase().endsWith(".pdf") ? readPdfText(file) : file.text(); }
function downloadFile(filename, content, mime = "text/plain") { const blob = new Blob([content], {type:mime}); const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href=url; a.download=filename; a.click(); URL.revokeObjectURL(url); }
function markdownTable(rows) { return ["| Concetto | Frequenza | Importanza | Spiegazione |", "| --- | --- | --- | --- |", ...rows.map(r => `| ${r.concetto} | ${r.frequenza} | ${r.importanza} | ${r.spiegazione.replaceAll("|", "\\|")} |`)].join("\n"); }
function renderOutput(data) {
  outputBox.innerHTML = `
  <section class="panel"><h2>Riassunto</h2><ol>${data.riassunto.map(s=>`<li>${escapeHtml(s)}</li>`).join("")}</ol></section>
  <section class="panel"><h2>Tabella concetti</h2><div class="table-wrap"><table><thead><tr><th>Concetto</th><th>Frequenza</th><th>Importanza</th><th>Spiegazione</th></tr></thead><tbody>${data.tabella_concetti.map(r=>`<tr><td>${escapeHtml(r.concetto)}</td><td>${r.frequenza}</td><td>${r.importanza}/5</td><td>${escapeHtml(r.spiegazione)}</td></tr>`).join("")}</tbody></table></div></section>
  <section class="panel"><h2>Card</h2><div class="cards-grid">${data.cards.map(c=>`<article class="mini-card"><h3>${escapeHtml(c.fronte)}</h3><p>${escapeHtml(c.retro)}</p></article>`).join("")}</div></section>
  <section class="panel"><h2>Quiz</h2>${data.quiz.map((q,qi)=>`<article class="quiz-card"><h3>${qi+1}. ${escapeHtml(q.domanda)}</h3>${q.opzioni.map((o,oi)=>`<button class="quiz-option" data-correct="${o===q.risposta_corretta}">${String.fromCharCode(65+oi)}. ${escapeHtml(o)}</button>`).join("")}<p class="quiz-explanation">${escapeHtml(q.spiegazione)}</p></article>`).join("")}</section>
  <section class="panel"><h2>Scarica output</h2><div class="download-grid"><button id="d1">riassunto.md</button><button id="d2">tabelle_concetti.md</button><button id="d3">cards.json</button><button id="d4">quiz.json</button><button id="d5">analisi_completa.json</button></div></section>`;
  document.querySelectorAll(".quiz-option").forEach(button => button.addEventListener("click", () => { const box = button.closest(".quiz-card"); box.querySelectorAll(".quiz-option").forEach(b => { b.disabled = true; if (b.dataset.correct === "true") b.classList.add("correct"); }); if (button.dataset.correct !== "true") button.classList.add("wrong"); box.querySelector(".quiz-explanation").style.display = "block"; }));
  document.getElementById("d1").onclick = () => downloadFile("riassunto.md", `# Riassunto - ${data.titolo}\n\n` + data.riassunto.map((s,i)=>`${i+1}. ${s}`).join("\n"));
  document.getElementById("d2").onclick = () => downloadFile("tabelle_concetti.md", markdownTable(data.tabella_concetti));
  document.getElementById("d3").onclick = () => downloadFile("cards.json", JSON.stringify(data.cards,null,2), "application/json");
  document.getElementById("d4").onclick = () => downloadFile("quiz.json", JSON.stringify(data.quiz,null,2), "application/json");
  document.getElementById("d5").onclick = () => downloadFile("analisi_completa.json", JSON.stringify(data,null,2), "application/json");
}

generateButton.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) { setStatus("Seleziona prima un file TXT, PDF o Markdown.", "error"); return; }
  try {
    setStatus("Analisi in corso...", "info");
    const text = cleanText(await readUploadedFile(file));
    if (text.length < 120) throw new Error("Testo estratto troppo corto. Il PDF potrebbe essere una scansione immagine.");
    const title = titleInput.value.trim() || file.name.replace(/\.[^.]+$/, "");
    const sentences = splitSentences(text);
    const key = extractKeywords(text);
    const rows = makeRows(key, sentences);
    const data = { titolo:title, file_originale:file.name, generato_il:new Date().toISOString(), statistiche:{caratteri:text.length, parole:tokenize(text).length, frasi:sentences.length, parole_chiave:key.length}, parole_chiave:key, riassunto:makeSummary(sentences,key), tabella_concetti:rows, cards:makeCards(rows), quiz:makeQuiz(rows) };
    renderOutput(data);
    setStatus("✅ Output generati correttamente nella demo.", "success");
  } catch (error) { setStatus(`❌ ${error.message}`, "error"); }
});
