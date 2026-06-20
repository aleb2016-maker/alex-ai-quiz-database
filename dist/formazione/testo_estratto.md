# Documento RAG di test: Sicurezza informatica aziendale

## Scopo del documento

Questo documento è stato creato come fonte di prova per il motore RAG del progetto quiz.
Può essere inserito nella cartella `rag/documenti/` per generare quiz, test e mini-corsi sulla sicurezza informatica aziendale.

L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali.
Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e trasformarli in domande controllate.

---

## 1. Cos'è la sicurezza informatica

La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali.
Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.

Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link sospetti o condividono dati riservati senza controllo.

La sicurezza informatica ha tre obiettivi principali:

- proteggere la riservatezza dei dati;
- garantire l'integrità delle informazioni;
- mantenere disponibili servizi e strumenti quando servono.

Riservatezza significa che solo le persone autorizzate possono accedere a certe informazioni.
Integrità significa che i dati non devono essere modificati in modo non autorizzato.
Disponibilità significa che sistemi, documenti e servizi devono rimanere accessibili agli utenti autorizzati.

---

## 2. Password sicure

Una password sicura deve essere lunga, difficile da indovinare e diversa per ogni servizio.
Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account.

Una buona password dovrebbe contenere parole non ovvie, numeri, simboli e una lunghezza adeguata.
Un esempio debole è `password123`, perché è corta, comune e facile da provare automaticamente.
Un esempio più forte è una frase lunga e personale, non facilmente collegabile alla persona, con alcune variazioni.

Il metodo migliore è usare un password manager.
Un password manager permette di salvare password lunghe e uniche senza doverle ricordare tutte.
L'utente deve ricordare solo la password principale del password manager, che deve essere molto robusta.

Le password non devono essere scritte su fogli lasciati sulla scrivania, inviate via email o condivise in chat non sicure.
Se una password viene comunicata a un'altra persona, non è più veramente personale.

---

## 3. Autenticazione a due fattori

L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
Il primo fattore è qualcosa che l'utente conosce, come la password.
Il secondo fattore può essere qualcosa che l'utente possiede, come uno smartphone, oppure qualcosa che l'utente è, come un'impronta digitale.

La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.
Anche se un attaccante scopre la password, deve superare anche il secondo controllo.

I codici temporanei generati da app di autenticazione sono generalmente più sicuri dei codici ricevuti via SMS.
Gli SMS possono essere esposti a rischi come cambio SIM fraudolento o intercettazioni.
Tuttavia, usare SMS come secondo fattore è comunque meglio che usare solo la password.

Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.

---

## 4. Phishing

Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.
Spesso arriva tramite email, SMS, messaggi social o siti che imitano servizi reali.

Un messaggio di phishing può sembrare urgente.
Può dire che un account verrà bloccato, che un pacco è fermo, che bisogna verificare un pagamento o che è necessario aggiornare subito una password.
L'obiettivo è spingere l'utente ad agire in fretta senza controllare.

Alcuni segnali di rischio sono:

- indirizzo del mittente strano o leggermente diverso da quello ufficiale;
- link che non portano al dominio reale;
- errori grammaticali o frasi insolite;
- richiesta di password, codici o dati bancari;
- tono minaccioso o eccessivamente urgente;
- allegati inattesi.

Non bisogna cliccare link sospetti.
È meglio aprire il sito ufficiale digitando l'indirizzo nel browser oppure usando un'app già installata.
In azienda, un'email sospetta dovrebbe essere segnalata al reparto IT o al responsabile della sicurezza.

---

## 5. Malware e allegati pericolosi

Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.
Può arrivare tramite allegati email, link infetti, software pirata, chiavette USB sconosciute o siti compromessi.

Un tipo particolare di malware è il ransomware.
Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.
Pagare non garantisce sempre il recupero dei dati e può incoraggiare ulteriori attacchi.

Per ridurre il rischio malware è importante:

- evitare software non autorizzato;
- non aprire allegati inattesi;
- aggiornare sistema operativo e applicazioni;
- usare strumenti antivirus o sistemi di protezione endpoint;
- fare backup regolari;
- limitare i privilegi amministrativi.

Un utente non dovrebbe lavorare sempre con account amministratore se non necessario.
Limitare i permessi riduce i danni nel caso in cui un programma malevolo venga eseguito.

---

## 6. Backup

Il backup è una copia di sicurezza dei dati.
Serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.

Un backup efficace deve essere regolare, verificato e separato dal sistema principale.
Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche quello.

Una regola utile è mantenere più copie dei dati importanti, possibilmente su supporti o servizi diversi.
Non basta creare backup: bisogna anche testare il ripristino.
Un backup che non può essere ripristinato correttamente non è davvero utile.

In un contesto aziendale, il backup deve essere pianificato.
Bisogna decidere quali dati salvare, ogni quanto salvarli, dove conservarli e chi può accedervi.

---

## 7. Aggiornamenti software

Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.
Rimandare gli aggiornamenti per troppo tempo può lasciare un sistema esposto ad attacchi già conosciuti.

Un attaccante spesso sfrutta vulnerabilità note.
Quando una correzione viene pubblicata, anche gli attaccanti possono studiare il problema e cercare sistemi non aggiornati.

Aggiornare non significa solo aggiornare il sistema operativo.
Bisogna mantenere aggiornati anche browser, app, plugin, software aziendali, strumenti di sicurezza e dispositivi di rete.

In azienda, gli aggiornamenti dovrebbero essere gestiti con una procedura controllata.
Prima si valuta la compatibilità, poi si distribuisce la correzione, poi si verifica che il sistema funzioni correttamente.

---

## 8. Dati sensibili

I dati sensibili sono informazioni che devono essere protette con particolare attenzione.
Possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.

Non tutti i dati hanno lo stesso livello di rischio.
Un volantino pubblico può essere condiviso liberamente, mentre un file con credenziali, documenti interni o dati dei clienti richiede protezioni più forti.

Prima di condividere un file bisogna chiedersi:

- chi deve realmente accedere a questo contenuto?
- il destinatario è corretto?
- il canale usato è sicuro?
- il file contiene dati non necessari?
- serve una protezione aggiuntiva, come password o permessi limitati?

Un errore comune è inviare file riservati al destinatario sbagliato.
Per questo è utile controllare sempre indirizzo, allegati e contenuto prima di premere invio.

---

## 9. Permessi e principio del minimo privilegio

Il principio del minimo privilegio dice che ogni utente deve avere solo i permessi necessari per svolgere il proprio lavoro.
Non tutti devono poter modificare file critici, accedere a dati sensibili o installare software.

Questo principio riduce il danno possibile in caso di errore o compromissione di un account.
Se un account con pochi permessi viene violato, l'attaccante avrà meno possibilità di causare danni gravi.

I permessi devono essere controllati periodicamente.
Quando una persona cambia ruolo o lascia l'azienda, i suoi accessi devono essere modificati o rimossi.
Lasciare attivi account non più necessari è un rischio.

---

## 10. Reti Wi-Fi e connessioni pubbliche

Le reti Wi-Fi pubbliche possono essere comode, ma non sempre sono sicure.
Un attaccante potrebbe creare una rete con un nome simile a quello di un bar, hotel o aeroporto per intercettare il traffico degli utenti.

Quando si usa una rete pubblica è meglio evitare operazioni sensibili, come accesso a conti bancari, sistemi aziendali o pannelli amministrativi.
Se necessario, è preferibile usare una VPN aziendale o una connessione mobile personale.

Anche in casa o in ufficio la rete Wi-Fi deve essere protetta con password forte e crittografia adeguata.
La password del router non dovrebbe rimanere quella predefinita se è debole o facilmente prevedibile.

---

## 11. Comportamenti corretti in azienda

La sicurezza informatica dipende anche da comportamenti quotidiani.
Bloccare lo schermo quando ci si allontana dalla postazione impedisce ad altre persone di usare il computer senza autorizzazione.
Non lasciare documenti riservati sulla scrivania riduce il rischio di accesso non autorizzato.

Un dipendente dovrebbe segnalare subito incidenti, errori o sospetti.
Nascondere un clic su un link sospetto o una password inserita in un sito falso può peggiorare la situazione.
Una segnalazione rapida permette all'azienda di reagire prima che il danno aumenti.

La cultura della sicurezza non deve basarsi sulla paura, ma sulla responsabilità.
Gli errori possono capitare, ma devono essere comunicati rapidamente.

---

## 12. Uso del documento per quiz e mini-corsi

Questo documento può essere usato dal motore RAG per generare domande su:

- password sicure;
- autenticazione a due fattori;
- phishing;
- malware;
- ransomware;
- backup;
- aggiornamenti software;
- protezione dei dati;
- permessi utente;
- reti Wi-Fi pubbliche;
- comportamenti corretti in azienda.

Le domande generate dovrebbero avere una risposta corretta e tre distrattori forti.
Un buon distrattore non deve essere assurdo.
Deve sembrare plausibile, ma essere sbagliato per un dettaglio preciso.

Esempio di domanda possibile:

Domanda: Perché è rischioso usare la stessa password su più servizi?

Risposta corretta: Perché se un servizio viene violato, la stessa password può essere provata anche su altri account.

Distrattore forte: Perché una password uguale impedisce sempre l'attivazione della 2FA.

Distrattore medio: Perché i browser cancellano automaticamente tutte le password uguali.

Distrattore medio: Perché una password usata più volte diventa più corta nel tempo.

La risposta corretta è la prima, perché il rischio principale è il riutilizzo delle credenziali su più servizi.
