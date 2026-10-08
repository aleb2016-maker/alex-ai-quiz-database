/* RAG exports V5.0 - offline browser exports for all four generated modes.
 * No server/API requests; uses the already loaded jsPDF library for searchable PDF.
 */
(function (root, document) {
  "use strict";
  const modes={summary:"Riassunto",cards:"Card",study:"Domande studio",test:"Quiz"};
  const actions={btnScaricaTxt:"txt",btnScaricaPdf:"pdf",btnScaricaHtml:"html",btnScaricaJson:"json"};
  function collect(){
    const engine=root.ragConceptDocumentEngineV46;
    const data=engine&&typeof engine.getExportSnapshot==="function"?engine.getExportSnapshot():null;
    if(!data||!modes[data.kind]||!Array.isArray(data.items)||!data.items.length)return null;
    return data;
  }
  function plain(value){return String(value==null?"":value).replace(/\r\n?/g,"\n").trim();}
  function niceFilename(data,extension){
    const stamp=new Date().toISOString().slice(0,16).replace(/[T:]/g,"-");
    return "rag-"+data.kind+"-"+stamp+"."+extension;
  }
  function itemLines(data,index){
    const item=data.items[index],rows=[];
    if(data.kind==="summary"||data.kind==="cards"){
      rows.push((index+1)+". "+plain(item.heading||"Argomento"));
      if(item.topic&&item.topic!==item.heading)rows.push("Categoria: "+plain(item.topic));
      rows.push(plain(item.body));
    }else if(data.kind==="study"){
      rows.push((index+1)+". "+plain(item.heading||"Domanda studio"));
      rows.push("DOMANDA: "+plain(item.question));
      rows.push("RISPOSTA: "+plain(item.answer)); // Always export the hidden flip side.
    }else if(data.kind==="test"){
      rows.push((index+1)+". "+plain(item.question));
      (item.options||[]).forEach((option,i)=>rows.push(String.fromCharCode(65+i)+") "+plain(option)));
      rows.push("RISPOSTA CORRETTA: "+plain(item.correct));
      if(item.explanation)rows.push("SPIEGAZIONE: "+plain(item.explanation));
    }
    return rows;
  }
  function structuredLines(data,includeOriginal){
    const lines=["RAG DOCUMENTI - "+modes[data.kind].toLocaleUpperCase("it"),
      "Documento: "+plain(data.title||"Documento analizzato"),
      "Elementi generati: "+data.items.length,""];
    data.items.forEach((item,i)=>{lines.push(...itemLines(data,i),"");});
    if(includeOriginal){
      lines.push("DOCUMENTO ORIGINALE","",plain(data.source||"Non disponibile"));
    }
    return lines;
  }
  function toTxt(data){return structuredLines(data,true).join("\n")+"\n";}
  function htmlEscape(text){return String(text==null?"":text).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");}
  function toHtml(data){
    const sections=data.items.map((item,i)=>
      '<section class="entry"><h2>'+htmlEscape((i+1)+". "+(item.heading||item.question||"Contenuto"))+'</h2>'+
      (data.kind==="summary"||data.kind==="cards"?
        '<p>'+htmlEscape(item.body||"")+'</p>':
      data.kind==="study"?
        '<p><strong>Domanda:</strong> '+htmlEscape(item.question||"")+'</p>'+
        '<p><strong>Risposta:</strong> '+htmlEscape(item.answer||"")+'</p>':
        '<p>'+htmlEscape(item.question||"")+'</p><ol type="A">'+(item.options||[]).map(v=>'<li>'+htmlEscape(v)+'</li>').join("")+'</ol>'+
        '<p><strong>Risposta corretta:</strong> '+htmlEscape(item.correct||"")+'</p>'+
        '<p>'+htmlEscape(item.explanation||"")+'</p>')+'</section>').join("\n");
    return '<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
      '<title>'+htmlEscape(modes[data.kind])+' - RAG Documenti</title><style>'+
      'body{font:17px/1.55 system-ui,sans-serif;background:#0b1225;color:#f3f5ff;padding:22px;max-width:1050px;margin:auto}'+
      '.entry{background:#1d2542;border:1px solid #536488;border-radius:16px;padding:20px;margin:18px 0}'+
      'h1{font-size:1.8rem}h2{font-size:1.25rem}p,li{white-space:pre-wrap}'+
      'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#121a32;padding:18px;border-radius:12px}'+
      '@media print{body{background:#fff;color:#111}.entry,pre{background:#fff;color:#111;border-color:#bbb}}'+
      '</style></head><body><h1>'+htmlEscape(modes[data.kind])+'</h1>'+
      '<p>Documento: '+htmlEscape(data.title||"Documento analizzato")+'</p>'+sections+
      '<section><h2>Documento originale</h2><pre>'+htmlEscape(data.source||"")+'</pre></section></body></html>';
  }
  function toJson(data){
    return JSON.stringify({type:"materiale_generato_rag",version:"5.0",generatedAt:new Date().toISOString(),
      mode:data.kind,title:data.title||"",source:data.source||"",items:data.items},null,2);
  }
  function pdfText(input){
    // Standard PDF Helvetica covers Latin-1 accents but not emoji and smart punctuation.
    return plain(input).replace(/[\u2018\u2019]/g,"'").replace(/[\u201C\u201D]/g,'"')
      .replace(/[\u2013\u2014]/g,"-").replace(/\u2026/g,"...").replace(/\u2022/g,"-")
      .replace(/\u00a0/g," ").replace(/[^\u0009\u000a\u000d\u0020-\u00ff]/g,"");
  }
  function makePdf(data,PDFClass){
    const PDF=PDFClass||root.jspdf&&root.jspdf.jsPDF;
    if(!PDF)throw new Error("Libreria jsPDF non disponibile: verifica la connessione e ricarica la pagina.");
    const doc=new PDF({unit:"mm",format:"a4",compress:true});
    const pageH=297, margin=17, maxW=176;
    let y=19;
    function addParagraph(value,opts){
      const bold=opts&&opts.bold,size=(opts&&opts.size)||10;
      doc.setFont("helvetica",bold?"bold":"normal");
      doc.setFontSize(size);
      const text=pdfText(value);
      const rows=text.split("\n").flatMap(line=>line?doc.splitTextToSize(line,maxW):[""]);
      const step=size>=14?7:5.3;
      for(const row of rows){
        if(y+step>pageH-margin){doc.addPage();y=19;}
        if(row)doc.text(row,margin,y);
        y+=step;
      }
      y+=(opts&&opts.after)!=null?opts.after:3;
    }
    addParagraph("RAG DOCUMENTI - "+modes[data.kind],{bold:true,size:17,after:4});
    addParagraph("Documento: "+(data.title||"Documento analizzato"),{size:11,after:6});
    data.items.forEach((item,i)=>{
      const list=itemLines(data,i);
      const heading=list.shift();
      addParagraph(heading,{bold:true,size:12,after:2});
      list.forEach(line=>addParagraph(line,{size:10,after:line?2:2}));
      y+=4;
    });
    addParagraph("DOCUMENTO ORIGINALE",{bold:true,size:12,after:3});
    addParagraph(data.source||"Non disponibile",{size:9,after:4});
    const pages=doc.internal&&doc.internal.getNumberOfPages?doc.internal.getNumberOfPages():1;
    for(let i=1;i<=pages;i++){
      doc.setPage(i);doc.setFont("helvetica","normal");doc.setFontSize(9);
      doc.text("RAG Documenti - "+modes[data.kind]+" - pagina "+i+"/"+pages,margin,289);
    }
    return doc;
  }
  function saveBlob(filename,body,mime){
    const blob=new Blob([body],{type:mime});
    const url=URL.createObjectURL(blob);
    const anchor=document.createElement("a");
    anchor.href=url;anchor.download=filename;
    document.body.appendChild(anchor);
    anchor.click();anchor.remove();
    // Safari/Chrome sometimes need the URL to outlive the click handler.
    root.setTimeout(()=>URL.revokeObjectURL(url),1500);
  }
  function run(format){
    const data=collect();
    if(!data){
      root.alert("Genera prima Riassunto, Card, Test o Domande studio: non c'è un risultato da scaricare.");
      return false;
    }
    try{
      if(format==="pdf"){makePdf(data).save(niceFilename(data,"pdf"));}
      else if(format==="txt")saveBlob(niceFilename(data,"txt"),toTxt(data),"text/plain;charset=utf-8");
      else if(format==="html")saveBlob(niceFilename(data,"html"),toHtml(data),"text/html;charset=utf-8");
      else if(format==="json")saveBlob(niceFilename(data,"json"),toJson(data),"application/json;charset=utf-8");
      return true;
    }catch(error){console.error("RAG esportazione "+format,error);
      root.alert("Errore nell'esportazione "+format.toUpperCase()+": "+(error.message||String(error)));
      return false;
    }
  }
  function install(){
    // Anche il PDF aggiuntivo creato dal layout deve esportare il file vero,
    // senza aprire la finestra di stampa o duplicare il download.
    if(!document.__ragPdfToolbarV50){
      document.__ragPdfToolbarV50=true;
      document.addEventListener("click",event=>{
        const toolbar=event.target&&event.target.closest&&event.target.closest(".rag-pdf-rigido-btn");
        if(!toolbar)return;
        event.preventDefault();
        event.stopPropagation();
        if(event.stopImmediatePropagation)event.stopImmediatePropagation();
        run("pdf");
      },true);
    }
    Object.entries(actions).forEach(([id,format])=>{
      const button=document.getElementById(id);
      if(!button||button.dataset.ragExportV50==="1")return;
      button.dataset.ragExportV50="1";
      button.addEventListener("click",event=>{event.preventDefault();run(format);});
    });
  }
  root.RAGExportV50={collect,structuredLines,itemLines,toTxt,toHtml,toJson,makePdf,run,install};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",install);
  else install();
})(window,document);
