/* Motore RAG V5.0 - analisi estrattiva universale nel browser.
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
   if(!sections.length&&!block.length&&!intro.length&&i<3&&(/^#\s+[^#]/.test(line)||(!/^#{2,6}\s/.test(line)&&headingText(line)===headingText(line).toLocaleUpperCase("it"))))intro.push(headingText(line));
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
 // Mai cancellare frasi sulla base della sola somiglianza: numeri, unità,
 // soggetti e negazioni distinti restano sempre fatti differenti.
 const seen=new Set();
 return sections.map((part,sectionIndex)=>{
  const selected=[];
  for(const original of splitFacts(part.body)){
   const value=flat(original),key=norm(value);
   if(!key||seen.has(key))continue;
   seen.add(key);selected.push(value);
  }
  const meaningful=selected.filter(value=>!
   /^(?:una risposta completa|per ripassare|in questa sezione vedremo|questo esercizio chiede|il seguente esempio)/i.test(value));
  return {...part,sectionIndex,facts:meaningful.length?meaningful:selected};
 }).filter(x=>x.facts.length);
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
 const value=facts[0]||"", t=flat(topic);
 const date=value.match(dateRE),number=value.match(amountRE);
 const definition=value.match(/^(.{4,82}?)\s+(?:è|sono|significa|consiste in|si definisce|indica)\s+(.{18,})/i);
 if(definition){
   let subject=definition[1].trim().replace(/^(?:inoltre|infatti|tuttavia|quindi)\s*,?\s*/i,"");
   if(subject.split(/\s+/).length<=10)return "Che cosa afferma il testo su «"+subject+"»?";
 }
 if(/\b(?:deve|devono|bisogna|occorre|è necessario|si consiglia|si procede)\b/i.test(value))
   return "Quale operazione o regola descrive il testo in «"+t+"»?";
 if(date)return "Che cosa riporta il documento riguardo alla data "+date[0]+"?";
 if(number)return "Quale informazione è associata al valore "+number[0]+"?";
 if(/\b(?:perché|poiché|a causa di|per effetto|provoca|comporta|permette|consente)\b/i.test(value))
   return "Quale relazione di causa o effetto è descritta in «"+t+"»?";
 if(/\b(?:rispetto a|mentre|invece|differenza|al contrario|non)\b/i.test(value))
   return "Quale distinzione viene spiegata nel passaggio «"+t+"»?";
 return "Qual è il fatto essenziale descritto in «"+t+"»?";
}
function unitTitle(value,base,i){
 const text=flat(value);
 // Rimuovi avverbi introduttivi e scegli la prima proposizione completa breve.
 let phrase=text.replace(/^(?:inoltre|tuttavia|in particolare|per esempio)\s*,?\s*/i,"");
 phrase=phrase.split(/[;:]/)[0].replace(/[.!?]+$/,"");
 if(phrase.length>78) {
   const cut=phrase.slice(0,78);
   const last=cut.lastIndexOf(" ");
   phrase=cut.slice(0,last>37?last:78).trim();
 }
 phrase=phrase.replace(/\s+(?:di|da|per|con|a|e|o|in|su|del|della|degli|delle|dei|il|la)$/i,"");
 return phrase.length>=16?phrase:base+" — "+(i+1);
}
function analyze(input){
 const source=tidy(input);if(source.length<28)return null;
 const parsed=splitBlocks(source),groups=uniqueFacts(parsed.sections);
 if(!groups.length)return null;
 const units=[];
 for(const part of groups){
  part.facts.forEach((fact,i)=>{
   // Ogni fatto autosufficiente diventa un'unità. Un capitolo non riduce il
   // numero dei concetti disponibili e la copertura rimane distribuita.
   const name=part.title==="Contenuto principale"||
     /^Paragrafo \d+/i.test(part.title)?unitTitle(fact,"Tema "+(part.sectionIndex+1),i):
     (part.facts.length===1?part.title:part.title+": "+unitTitle(fact,part.title,i));
   units.push({title:name,body:fact,facts:[fact],parentTitle:part.title,
    sourceBody:part.body,sectionIndex:part.sectionIndex});
  });
 }
 const selected=spread(units,Math.max(8,Math.min(30,Math.ceil(units.length*.85))));
 const groupsForSummary=[];
 const MAX_SUMMARY=25;
 for(const group of groups){
  // Un riassunto sintetizza l'intero capitolo senza limitarsi alle prime 2 frasi.
  for(let i=0;i<group.facts.length;i+=2){
   const batch=group.facts.slice(i,i+2);
   groupsForSummary.push({title:group.title+(group.facts.length>2?" — "+(Math.floor(i/2)+1):""),
    text:batch.map(v=>compact(v,350)).join(" ")});
  }
 }
 const summary=spread(groupsForSummary,MAX_SUMMARY);
 const concepts=selected.map((u,i)=>({title:u.title,ramo:u.parentTitle,icon:icon(u.parentTitle),
    fatto:compact(u.facts[0],350),domanda:question(u.title,u.facts),
    risposta:compact(u.facts[0],350),source:u.facts[0]}));
 const profile={materia:parsed.title||"documento analizzato",contesto:"analisi locale",categoria:"informazioni effettive"};
 return {profile,sections:units,summary,concepts,originalSections:groups,
    source,stats:{sections:groups.length,facts:units.length,selected:selected.length}};
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
 // Un abbinamento è valido solo se nessun distrattore è sostenuto dal
 // passaggio completo interrogato, neppure in frasi non selezionate.
 const correct=s.facts[0],body=norm(s.sourceBody||s.body);
 const alternatives=all.filter(x=>x!==s)
   .flatMap(x=>x.facts)
   .filter(v=>v!==correct && !body.includes(norm(v)) &&
     overlap(v,correct)<.4 &&
     !splitFacts(s.sourceBody||s.body).some(f=>overlap(f,v)>.62));
 if(alternatives.length<3)return null;
 const picks=spread(alternatives,3),choices=[correct,...picks].map(v=>compact(v,215));
 if(new Set(choices.map(norm)).size!==4)return null;
 return {q:"Quale delle seguenti informazioni è sostenuta dal passaggio «"+s.title+"»?",
  correct:choices[0],options:shuffle(choices),explanation:correct,kind:"abbinamento"};
}
function qCloze(s,all){
 const value=s.facts[0];if(!value||words(value).length<4)return null;
 const freq=new Map();
 all.flatMap(x=>x.facts).forEach(t=>words(t).forEach(w=>freq.set(w,(freq.get(w)||0)+1)));
 const tokens=words(value),titleTokens=new Set(words(s.parentTitle||s.title));
 const bad=new Set(("soprattutto comunque tuttavia inoltre effettivamente principalmente generalmente " +
   "infine successivamente particolarmente probabilmente importante maggiormente direttamente " +
   "disponibile possibile necessario maggiore minore differenti diversi").split(" "));
 const options=tokens.filter(v=>v.length>=5&&v.length<=19&&/^[a-z]+$/.test(v)&&
   !bad.has(v)&&!titleTokens.has(v));
 if(!options.length)return null;
 // Termini informativi favoriti: più specifici, meno frequenti e non avverbi.
 options.sort((a,b)=>(b.length/6-2*(freq.get(b)||0)-(b.endsWith("mente")?3:0))-
                   (a.length/6-2*(freq.get(a)||0)-(a.endsWith("mente")?3:0)));
 const term=options[0];
 const regex=new RegExp("\\b"+term+"\\b","i"),match=value.match(regex);
 if(!match)return null;const correct=match[0];
 const candidates=[...freq.keys()].filter(v=>
   v!==term&&!tokens.includes(v)&&v.length>=5&&v.length<=19&&
   Math.abs(v.length-term.length)<=4&&!bad.has(v)&&
   !/mente$/.test(v)&&!norm(s.sourceBody||s.body).includes(v));
 if(candidates.length<3)return null;
 // Distrattori dello stesso formato lessicale; scarta quelli sostenuti
 // dalla frase originale o dall'intero paragrafo.
 const suffix=term.slice(-3);
 candidates.sort((a,b)=>(b.endsWith(suffix)?1:0)-(a.endsWith(suffix)?1:0)||
    Math.abs(a.length-term.length)-Math.abs(b.length-term.length));
 const alternatives=spread(candidates.slice(0,16),3);
 const opts=[correct,...alternatives];
 if(new Set(opts.map(norm)).size!==4)return null;
 const masked=compact(value.replace(regex,"_____"),205);
 return {q:"Quale termine del documento completa correttamente questo passaggio? «"+masked+"»",
   correct,options:shuffle(opts),explanation:value,kind:"termine"};
}
function makeQuiz(data){
 if(!data||!data.sections||!data.sections.length)return[];
 const all=data.sections;
 const selected=spread(all,Math.min(24,all.length)),out=[],used=new Set();
 let numeric=0;
 for(const section of selected){
  // I quesiti su numeri/date sono limitati; non è un quiz solo mnemonico.
  const allowNumeric=numeric<Math.max(1,Math.floor(selected.length*.33));
  const q=(allowNumeric?(qDate(section)||qNumeric(section)):null)||
     qCloze(section,all)||qMatch(section,all);
  if(!q||new Set(q.options.map(norm)).size!==4||!q.options.includes(q.correct)||used.has(norm(q.q)))continue;
  // Rifiuta domande con opzioni uguali o appoggiate al fatto esaminato.
  if(q.kind==="abbinamento"){
   const sourceFacts=splitFacts(section.sourceBody||section.body).map(norm);
   if(q.options.some(v=>v!==q.correct&&sourceFacts.some(t=>t.includes(norm(v)))))continue;
  }
  used.add(norm(q.q));out.push(q);
  if(q.kind==="data"||q.kind==="numero")numeric++;
 }
 return out;
}

root.RAGContentQualityV50={analyze,makeQuiz,splitBlocks,splitFacts};
})(window);