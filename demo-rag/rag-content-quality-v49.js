/* Motore RAG V4.9 - analisi estrattiva universale nel browser.
   Nessun testo inventato, nessuna dipendenza da materie o API esterne. */
(function(root) {
"use strict";
const stop=new Set(("della delle dello degli dalla dalle dalla nella nelle nello negli sulla sulle sugli alla alle allo agli " +
"che chi cui con per tra fra non ma gli nel nei uno una un il lo la le i e ed o ad di da in su al ai " +
"sono era erano viene vengono stato stata stati ogni tutti tutto molto più come questo questa questi queste " +
"quello quella quelli quelle avere anche dopo prima durante oltre stesso altra altri altre sia documento " +
"testo sezione informazioni argomento punto principale vengono degli delle della così ancora").split(/\s+/));
const month="gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split(" ");
const dateRE=new RegExp("\\b([0-3]?\\d)\\s+("+month.join("|")+")\\s+(1[89]\\d{2}|20\\d{2})\\b","i");
const yearRE=/\b(1[89]\d{2}|20\d{2})\b/;
const amountRE=/\b\d+(?:[.,]\d+)?\s*(?:%|€|euro|km|kg|g|mg|ml|litri|metri|ore|minuti|giorni|anni|persone|utenti|gradi|°c)\b/i;
function tidy(x){return String(x??"").replace(/\r\n?/g,"\n").replace(/\u00a0/g," ").replace(/[ \t]+/g," ").trim();}
function flat(x){return tidy(x).replace(/\s+/g," ").trim();}
function norm(x){return flat(x).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase("it").replace(/[^a-z0-9 ]/g," ").replace(/\s+/g," ").trim();}
function words(x){return norm(x).split(" ").filter(w=>w.length>=4&&!stop.has(w));}
function headingText(x){return tidy(x).replace(/^#{1,6}\s*/,"").replace(/^\d+[.)]\s*/,"").replace(/^[-*+]\s+/,"").replace(/[*_\x60]/g,"").trim();}
function likelyHeading(s){
 const line=tidy(s), t=headingText(line);
 if(!t||t.length>110)return false;
 if(/^#{1,6}\s+\S/.test(line)||/^\d{1,2}[.)]\s+[A-ZÀ-Ü]/.test(line))return true;
 if(/[.!?;:]$/.test(t)||t.length<5)return false;
 return (t===t.toLocaleUpperCase("it")&&/[a-zA-ZÀ-ÿ]/.test(t)) || (t.length<65&&t.split(/\s+/).length<=7&&!/,/.test(t));
}
function splitFacts(body){
 const lines=tidy(body).split("\n").map(x=>x.trim()).filter(Boolean);
 const out=[];
 for(const line of lines){
  // Un elenco può contenere un fatto per voce.
  const raw=line.replace(/^[-•*]\s*/,"").replace(/^\d+[.)]\s+/,"");
  const fragments=raw.match(/[^.!?]+(?:[.!?]+|$)/g)||[raw];
  for(const fragment of fragments){
   const value=flat(fragment).replace(/^[-•*]\s*/,"");
   if(value.length>=23 && value.split(/\s+/).length>=4)out.push(value);
  }
 }
 return out;
}
function splitBlocks(source){
 const lines=tidy(source).split("\n");
 const sections=[],intro=[];
 let label=null,block=[];
 function flush(){
  const body=tidy(block.join("\n")); block=[];
  if(!body)return;
  const name=label||("Paragrafo "+(sections.length+1));
  sections.push({title:name,body,order:sections.length});
 }
 for(let i=0;i<lines.length;i++){
  const line=lines[i].trim();
  if(!line){if(!label&&block.length)flush();continue;}
  if(likelyHeading(line)){
   // Un titolo isolato iniziale non deve diventare un fatto o una scheda.
   if(!sections.length&&!block.length&&!intro.length&&i<3)intro.push(headingText(line));
   else {flush();label=headingText(line);}
   continue;
  }
  block.push(line);
  // I blocchi non titolati molto lunghi vengono divisi senza perdere contenuti.
  if(!label&&block.join(" ").length>980)flush();
 }
 flush();
 // Evita di scartare il testo se tutto era una sola frase o un elenco.
 if(!sections.length&&flat(source))sections.push({title:"Contenuto principale",body:flat(source),order:0});
 let name=intro[0]||"";
 if(!name){const first=lines.find(x=>x.trim())||"";const t=headingText(first);
   if(t.length>=8&&t.length<=110&&t===t.toLocaleUpperCase("it")&&!/[.!?]$/.test(t))name=t;
 }
 return {title:name,sections};
}
function signature(x){return norm(x).slice(0,240);}
function overlap(a,b){
 const aa=new Set(words(a)),bb=new Set(words(b));
 if(!aa.size||!bb.size)return 0;
 let hit=0;for(const w of aa)if(bb.has(w))hit++;
 return hit/Math.max(1,Math.min(aa.size,bb.size));
}
function scoreFact(s,title,index,all,frequency){
 const ws=words(s), unique=new Set(ws);
 const key=words(title);
 const related=key.filter(x=>unique.has(x)).length;
 const topical=ws.reduce((sum,w)=>sum+1/Math.sqrt(frequency.get(w)||1),0)/Math.max(1,ws.length);
 let score=2*related+Math.min(s.length,185)/95+topical*.9+(index===0?.5:0);
 if(/\b(?:perché|poiché|quindi|causa|permette|consente|comporta|provoca|in seguito|si basa|risulta|prevede|serve|deve)\b/i.test(s))score+=.65;
 if(dateRE.test(s)||yearRE.test(s)||amountRE.test(s))score+=.4;
 if(/^(il documento|il testo|in questa sezione|questo paragrafo)\b/i.test(s))score-=1;
 if(s.length>365)score-=1;
 return score;
}
function uniqueFacts(sections){
 const all=sections.flatMap(s=>splitFacts(s.body));
 const counts=new Map();all.forEach(f=>words(f).forEach(w=>counts.set(w,(counts.get(w)||0)+1)));
 const seen=[];
 return sections.map(s=>{
  const ranked=splitFacts(s.body).map((value,index)=>({value,index,weight:scoreFact(value,s.title,index,all,counts)}))
   .filter(({value})=>!seen.some(old=>overlap(old,value)>.85));
  const selected=[];
  // Relevance + diversity: seleziona fatti centrali ma non troppo simili.
  while(ranked.length&&selected.length<4){
   ranked.sort((a,b)=>(b.weight-selected.reduce((n,x)=>Math.max(n,overlap(x.value,b.value)),0)*2)-
                         (a.weight-selected.reduce((n,x)=>Math.max(n,overlap(x.value,a.value)),0)*2));
   const item=ranked.shift();
   if(selected.some(x=>overlap(x.value,item.value)>.77))continue;
   selected.push(item);
  }
  selected.sort((a,b)=>a.index-b.index);
  selected.forEach(x=>seen.push(x.value));
  return {...s,facts:selected.map(x=>x.value)};
 }).filter(s=>s.facts.length);
}
function spread(arr,max){
 if(arr.length<=max)return arr.slice();
 const index=new Set();for(let i=0;i<max;i++)index.add(Math.min(arr.length-1,Math.floor((i+.35)*arr.length/max)));
 return [...index].map(i=>arr[i]);
}
function compact(x,limit=255){
 const text=flat(x);
 if(text.length<=limit)return text;
 const head=text.slice(0,limit+1);
 const split=Math.max(head.lastIndexOf(". "),head.lastIndexOf("; "),head.lastIndexOf(", "));
 if(split>limit*.6)return head.slice(0,split+1);
 const space=head.lastIndexOf(" ");
 return head.slice(0,Math.max(0,space)).replace(/[,:; ]+$/,"")+"…";
}
function icon(title){
 const ws=words(title),ix=ws.reduce((sum,w)=>sum+w.charCodeAt(0),0);
 return ["📚","🧩","🔎","💡","📋","⚙️","🌐","🗂️"][ix%8];
}
function question(topic,facts){
 const text=facts[0]||"",head=topic.replace(/^Paragrafo \d+:?\s*/i,"").trim();
 // Le domande dipendono da strutture linguistiche generali, non dalla materia.
 if(/\b(causa|cause|motivi|ragioni|ragione)\b/i.test(head))return "Quali cause o motivi emergono riguardo a «"+head+"»?";
 if(/\b(conseguenze|effetti|risultati|impatto)\b/i.test(head))return "Quali effetti o conseguenze sono descritti in «"+head+"»?";
 if(/\b(procedura|istruzioni|metodo|passaggi|fasi|preparazione)\b/i.test(head))return "Quali passaggi sono indicati per «"+head+"»?";
 if(/\b(obiettivi|scopo|finalità|vantaggi)\b/i.test(head))return "Qual è lo scopo o il vantaggio descritto in «"+head+"»?";
 if(/\b(requisiti|condizioni|regole|norme)\b/i.test(head))return "Quali requisiti o condizioni sono indicati per «"+head+"»?";
 if(/\b(rischi|problemi|limiti)\b/i.test(head))return "Quali rischi o limiti emergono riguardo a «"+head+"»?";
 if(/\b(definizione|significato|concetto)\b/i.test(head))return "Come viene definito «"+head+"»?";
 if(/\b(perché|poiché|a causa|grazie a)\b/i.test(text))return "Per quali ragioni si verifica quanto descritto in «"+head+"»?";
 if(dateRE.test(text))return "Quale evento o informazione viene collegato alla data nella parte «"+head+"»?";
 if(/\b(deve|occorre|bisogna|si consiglia|si procede)\b/i.test(text))return "Che cosa occorre fare secondo «"+head+"»?";
 if(/\b(è|sono|comprende|consiste in|significa)\b/i.test(text))return "Che cosa viene spiegato riguardo a «"+head+"»?";
 return "Quale informazione essenziale emerge dalla parte «"+head+"»?";
}
function analyze(input){
 const source=tidy(input);if(source.length<28)return null;
 const parsed=splitBlocks(source);
 const sections=uniqueFacts(parsed.sections);
 if(!sections.length)return null;
 // Quando non ci sono titoli, usa la prima frase significativa come titolo breve.
 sections.forEach((s,i)=>{
  if(/^Paragrafo \d+|^Contenuto principale$/i.test(s.title)){
   const first=s.facts[0]||"",intro=first.replace(/^[-•*]\s*/,"").split(/\s+/).slice(0,6).join(" ");
   s.title="Tema "+(i+1)+": "+intro.replace(/[.,;:!?]+$/,"");
  }
 });
 const picked=spread(sections,14);
 const profile={materia:parsed.title||"documento analizzato",contesto:"analisi locale",categoria:"contenuti effettivi"};
 const summary=picked.map(s=>({title:s.title,text:s.facts.slice(0,2).map(f=>compact(f,260)).join(" ")}));
 const concepts=picked.map(s=>({title:s.title,ramo:s.title,icon:icon(s.title),fatto:compact(s.facts[0],350),
   domanda:question(s.title,s.facts),risposta:s.facts.slice(0,2).map(f=>compact(f,260)).join(" ")}));
 return {profile,sections,summary,concepts,stats:{sections:sections.length,facts:sections.reduce((n,s)=>n+s.facts.length,0)}};
}
function shuffle(x){
 const a=x.slice();for(let j=a.length-1;j>0;j--){let i=Math.floor(Math.random()*(j+1));[a[i],a[j]]=[a[j],a[i]]}return a;
}
function qDate(s){
 const value=s.facts.find(x=>dateRE.test(x));if(!value)return null;
 const m=value.match(dateRE),correct=m[0],year=Number(m[3]);
 return {q:"Quale data completa il testo su «"+s.title+"»? «"+compact(value.replace(dateRE,"_____"),190)+"»",
  correct,options:shuffle([correct,...[year-1,year+1,year+2].map(y=>m[1]+" "+m[2]+" "+y)]),
  explanation:value,kind:"data"};
}
function qNumeric(s){
 const value=s.facts.find(f=>amountRE.test(f)||yearRE.test(f));if(!value)return null;
 const match=value.match(amountRE)||value.match(yearRE),correct=match[0];
 let options=[];
 if(yearRE.test(correct)&&/^\d{4}$/.test(correct)){
  const y=Number(correct);options=[correct,String(y-1),String(y+1),String(y+2)];
 }else{
  const n=correct.match(/[\d.,]+/),number=n?Number(n[0].replace(",",".")):NaN;
  if(!Number.isFinite(number)||number===0)return null;
  const values=[number,number*1.2,number*.8,number*1.5].map(x=>Number.isInteger(number)?String(Math.round(x)):String(Number(x.toFixed(2))).replace(".",","));
  options=values.map(x=>correct.replace(n[0],x));
 }
 if(new Set(options.map(norm)).size<4)return null;
 return {q:"Quale valore completa il passaggio su «"+s.title+"»? «"+compact(value.replace(correct,"_____"),190)+"»",
   correct,options:shuffle(options),explanation:value,kind:"numero"};
}
function qMatch(s,all){
 const correct=s.facts[0];
 const others=all.filter(x=>x!==s).flatMap(x=>x.facts.slice(0,2))
  .filter(x=>norm(x)!==norm(correct)&&overlap(x,correct)<.55);
 if(others.length<3)return null;
 const choices=spread(others,3).map(x=>compact(x,215));
 const clipped=compact(correct,215);
 if(new Set([clipped,...choices].map(norm)).size<4)return null;
 return {q:"Quale affermazione appartiene alla parte «"+s.title+"»?",
 correct:clipped,options:shuffle([clipped,...choices]),explanation:correct,kind:"abbinamento"};
}
function qCloze(s,all){
 const candidate=s.facts.find(x=>words(x).length>=5);
 if(!candidate)return null;
 const counts=new Map();
 all.flatMap(x=>x.facts).forEach(sentence=>words(sentence).forEach(w=>counts.set(w,(counts.get(w)||0)+1)));
 const source=words(candidate);
 const options=source.filter(w=>w.length>=5&&w.length<=17&&/^[a-z]+$/.test(w)&&
     (counts.get(w)||0)<=2&&!words(s.title).includes(w));
 const chosen=options.length?options[Math.floor(options.length*.6)]:null;
 if(!chosen)return null;
 const regex=new RegExp("\\b"+chosen+"\\b","i");
 const m=candidate.match(regex);if(!m)return null;
 const correct=m[0],other=[...counts.keys()].filter(w=>w!==chosen&&
   !source.includes(w)&&Math.abs(w.length-chosen.length)<=5&&w.length>=5);
 if(other.length<3)return null;
 other.sort((a,b)=>Math.abs(a.length-chosen.length)-Math.abs(b.length-chosen.length));
 const wrong=spread(other.slice(0,15),3);
 return {q:"Quale termine completa il passaggio su «"+s.title+"»? «"+compact(candidate.replace(regex,"_____"),190)+"»",
  correct,options:shuffle([correct,...wrong]),explanation:candidate,kind:"termine"};
}
function makeQuiz(data){
 if(!data||!data.sections)return[];
 const list=spread(data.sections,12);
 const out=[],used=new Set();let numericCount=0;
 for(const section of list){
  // Non trasformare ogni frase con una data nello stesso quiz di date.
  const canNumeric=numericCount<Math.ceil(list.length*.4);
  const q=(canNumeric?(qDate(section)||qNumeric(section)):null)||
    qMatch(section,data.sections)||qCloze(section,data.sections)||qDate(section)||qNumeric(section);
  if(!q||new Set(q.options.map(norm)).size!==4||used.has(norm(q.q)))continue;
  if(q.kind==="data"||q.kind==="numero")numericCount++;
  used.add(norm(q.q));out.push(q);
 }
 return out;
}
root.RAGContentQualityV49={analyze,makeQuiz,splitBlocks,splitFacts};
})(window);