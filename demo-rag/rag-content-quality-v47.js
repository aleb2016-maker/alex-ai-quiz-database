/* RAG Content Quality V4.7: motore estrattivo locale, senza API. */
(function(root){
"use strict";
const mesi="gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split(" ");
const dateRE=new RegExp("\\b([0-3]?\\d)\\s+("+mesi.join("|")+")\\s+(1[89]\\d{2}|20\\d{2})\\b","i");
const yearRE=/\b(1[89]\d{2}|20\d{2})\b/;
function clean(s){return String(s||"").replace(/\r\n?/g,"\n").replace(/[ \t]+/g," ").trim();}
function norm(s){return clean(s).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9 ]/g," ").replace(/\s+/g," ").trim();}
function title(s){return clean(s).replace(/^#{1,6}\s*/,"").replace(/^\d+[.)]\s*/,"").replace(/[*_\x60]/g,"").trim();}
function heading(line,next){const t=title(line);return /^#{1,6}\s+\S/.test(line)||/^\d+[.)]\s+[A-ZÀ-Ü]/.test(line)||!!next&&t.length>8&&t.length<76&&!/[.!?;:]$/.test(t)&&(t===t.toUpperCase()||t.split(" ").length<=6&&!/[.,]/.test(t));}
function parse(s){
 const lines=clean(s).split("\n"),out=[];let label="Contenuti principali",acc=[];
 function push(){let b=clean(acc.join(" "));if(b)out.push({title:label,body:b});acc=[];}
 for(let i=0;i<lines.length;i++){const v=lines[i].trim();if(!v){if(label==="Contenuti principali")push();continue;}
  const next=(lines.slice(i+1).find(x=>x.trim())||"").trim();
  if(heading(v,next)){push();label=title(v);}else acc.push(v.replace(/^[-*]\s+/,""));
 }
 push();return out.length?out:[{title:"Contenuti principali",body:clean(s)}];
}
function sentences(s){return (clean(s).replace(/\n/g," ").match(/[^.!?]+[.!?]?/g)||[]).map(x=>x.trim()).filter(x=>x.length>=35&&x.split(/\s+/).length>=7);}
const stops=new Set("quale quali delle della degli della dalla nella nelle negli alla alle sulla sulle come sono stato stata questi questa quello questa viene vengono hanno anche dopo prima durante documenti documento testo principali sulla nello della dello ogni tutti molto indicati".split(" "));
function keys(s){return norm(s).split(" ").filter(v=>v.length>3&&!stops.has(v));}
function facts(section){
 const seen=new Set();const items=[];
 for(const sentence of sentences(section.body)){const k=norm(sentence);if(seen.has(k))continue;seen.add(k);
  const overlap=keys(section.title).filter(w=>keys(sentence).includes(w)).length;
  const score=overlap*2+Math.min(sentence.length/100,2)+(yearRE.test(sentence)?2:0)+(/caus|port|provoc|perché|seguito|conseguenz|determin/i.test(sentence)?1:0);
  items.push({value:sentence.slice(0,430),score,index:items.length});
 }
 return items.sort((a,b)=>b.score-a.score).slice(0,3).sort((a,b)=>a.index-b.index).map(x=>x.value);
}
function question(s){
 const t=norm(s);
 if(/caus|ragion|origine|motivi/.test(t))return "Quali furono le cause descritte nella sezione «"+s+"»?";
 if(/attentat|assassin/.test(t))return "Che cosa accadde durante «"+s+"»?";
 if(/ingress|interven/.test(t))return "Come avvenne «"+s+"»?";
 if(/innovaz|tecnolog|invenzion/.test(t))return "Quali innovazioni sono descritte nella sezione «"+s+"»?";
 if(/conseguen|effetti|risultat/.test(t))return "Quali conseguenze descrive il testo nella sezione «"+s+"»?";
 if(/fine|conclus|armistizio/.test(t))return "Come si conclusero gli eventi descritti in «"+s+"»?";
 if(/svolta|cambiament|trasformaz/.test(t))return "Quali cambiamenti avvennero durante «"+s+"»?";
 if(/trince|svilupp|fasi|movimento/.test(t))return "Come si svilupparono i fatti trattati in «"+s+"»?";
 return "Quali fatti principali sono spiegati nella sezione «"+s+"»?";
}
function icon(s){const t=norm(s);if(/caus/.test(t))return"🧩";if(/attentat/.test(t))return"👥";if(/tecnolog|innovaz/.test(t))return"⚙️";if(/conseguen/.test(t))return"📊";if(/guerra|trince/.test(t))return"🛡️";if(/fine|svolta|ingress/.test(t))return"🗓️";return"📚";}
function spread(items,max){if(items.length<=max)return items;return Array.from({length:max},(_,i)=>items[Math.floor(i*items.length/max)]);}
function analyze(input){
 const source=clean(input);if(source.length<40)return null;
 const sections=parse(source).map(s=>({title:s.title,body:s.body,facts:facts(s)})).filter(s=>s.facts.length);
 if(!sections.length)return null;
 const selected=spread(sections,14);
 return {profile:{materia:sections.length>1?sections[0].title:"testo caricato",contesto:"documento analizzato",categoria:"contenuti del documento"},
 sections:sections,
 concepts:selected.map(s=>({title:s.title,ramo:s.title,icon:icon(s.title),fatto:s.facts[0],risposta:s.facts.slice(0,2).join(" "),domanda:question(s.title)})),
 summary:selected.map(s=>({title:s.title,text:s.facts.slice(0,2).join(" ")}))};
}
function shuffle(a){const x=a.slice();for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[x[i],x[j]]=[x[j],x[i]];}return x;}
function qDate(s){
 const fact=s.facts.find(x=>dateRE.test(x));if(!fact)return null;const m=fact.match(dateRE),year=Number(m[3]),correct=m[0];
 const masked=fact.replace(dateRE,"_____").slice(0,190);
 return {q:"Quale data completa il passaggio della sezione «"+s.title+"»? «"+masked+"»",correct:correct,
 options:shuffle([correct,...[year-1,year+1,year+2].map(y=>m[1]+" "+m[2]+" "+y)]),explanation:fact};
}
function qYear(s){
 const fact=s.facts.find(x=>yearRE.test(x));if(!fact)return null;const m=fact.match(yearRE),year=Number(m[1]),correct=m[0];
 return {q:"Quale anno completa il passaggio della sezione «"+s.title+"»? «"+fact.replace(yearRE,"_____").slice(0,190)+"»",
 correct,options:shuffle([correct,String(year-1),String(year+1),String(year+2)]),explanation:fact};
}
function qFact(s,sections){
 const correct=s.facts[0];const others=sections.filter(x=>x!==s).map(x=>x.facts[0]).filter(x=>x&&x!==correct);
 if(others.length<3)return null;
 return {q:"Quale affermazione riguarda «"+s.title+"» secondo il documento?",correct,
 options:shuffle([correct,...spread(others,3)]),explanation:correct};
}
function makeQuiz(data){return spread(data.sections||[],12).map(s=>qDate(s)||qYear(s)||qFact(s,data.sections)).filter(Boolean).filter(q=>new Set(q.options.map(norm)).size===4);}
root.RAGContentQualityV47={analyze,makeQuiz,parse,facts};
})(window);
