# RAG Documento Studio V4.4 - PDF exact capture

Questo fix non ridisegna il PDF a mano.

Architettura corretta:

- la pagina genera il materiale visivo
- il fix cattura il contenuto generato come immagine
- il PDF viene composto da immagini paginate
- niente intestazioni Chrome
- niente window.print
- niente testo riscritto con simboli strani
- niente card ridisegnate in JavaScript separato
