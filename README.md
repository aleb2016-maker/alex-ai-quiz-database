# Alex AI Quiz Database

Progetto riutilizzabile per creare, controllare e distribuire quiz interattivi di qualità.

Non è solo una demo online: è un motore completo per costruire database di domande, verificare la qualità, generare pacchetti scaricabili e creare quiz personalizzati riutilizzabili in altri progetti web o Android.

## Stato del progetto

Il progetto contiene **640 domande ufficiali**, divise tra area AI ITS e area Scienze.

Sezioni incluse:

- AI
- Informatica
- Matematica
- Inglese
- Logica testuale
- Logica visiva
- Scienze generali
- Biologia
- Chimica
- Fisica
- Fisica quantistica

## Obiettivo

L’obiettivo è creare una base solida per generare quiz su qualsiasi argomento, con controlli automatici che aiutano a evitare domande duplicate, risposte troppo facili, errori nei dati e problemi di qualità.

Il progetto può essere usato per:

- provare quiz già pronti nella demo online;
- creare pacchetti personalizzati;
- esportare pacchetti web e Android;
- costruire nuove app quiz partendo da una struttura già controllata.

## Qualità delle domande

Ogni domanda è pensata per avere:

- una risposta corretta;
- tre distrattori forti;
- opzioni plausibili e simili tra loro;
- spiegazioni chiare;
- nessuna risposta palesemente eliminabile;
- controlli contro duplicati e domande troppo simili.

Per le domande di inglese, le spiegazioni includono anche:

- `Traduzione domanda:`
- `Traduzione risposta:`

In questo modo il quiz può funzionare anche come piccolo strumento di studio.

## Logica visiva

La sezione di Logica visiva usa immagini e opzioni visuali.

I controlli verificano:

- coerenza tra immagine, risposta corretta e spiegazione;
- presenza delle immagini;
- assenza di domande suggerite;
- spiegazioni complete;
- forma, colore, numero di lati e oggetti interni.

Nelle domande visive il testo può essere volutamente neutro, perché la differenza reale è nelle immagini, nelle opzioni e nella logica visuale interna.

## Scarica pacchetto personalizzato

Nella demo è presente una sezione dedicata alla creazione di un pacchetto personalizzato.

Passaggi semplici:

1. apri la demo online del progetto;
2. scorri fino alla sezione **Scarica pacchetto personalizzato**;
3. scegli le materie o l’area di quiz che vuoi inserire nel pacchetto;
4. genera il pacchetto;
5. scarica il file `.zip`;
6. estrai lo ZIP sul computer;
7. apri il pacchetto web oppure usa i file generati come base per un nuovo progetto;
8. se vuoi creare un’app Android, copia il database e i file del motore nella struttura Android indicata nel pacchetto.

Questa funzione serve a trasformare il progetto in una base riutilizzabile: non solo una demo da provare, ma uno strumento per creare nuovi quiz partendo da contenuti già controllati.

## Motori principali

Comandi principali del progetto:

```bash
python3 scripts/validate_questions.py
python3 scripts/build_database.py
python3 scripts/check_duplicates.py
python3 scripts/controllo_qualita_completo.py
python3 scripts/controllo_totale_progetto.py
```

Il comando più importante è:

```bash
python3 scripts/controllo_totale_progetto.py
```

Questo comando verifica in modo unico:

- database ufficiali;
- generazione del database finale;
- controllo duplicati;
- qualità testuale;
- qualità Logica visiva;
- premi ed effetti visivi AI ITS;
- demo principali;
- pacchetti ZIP principali.

## File principali

```text
data/                 Database ufficiali
data/logica/          Database di logica testuale e visiva
demo-ai/              Demo web AI ITS
demo-scienze/         Demo web Scienze
dist/                 Database finale completo
downloads/            Pacchetti web e Android
scripts/              Motori, validatori e strumenti di build
reports/              Report automatici dei controlli
backups/              Backup non ufficiali
runtime/              File riutilizzabili per effetti e logica web
```

## Pacchetti disponibili

Il progetto genera e controlla pacchetti per:

- demo web AI ITS;
- demo web Scienze;
- pacchetto Android AI ITS;
- pacchetto Android Scienze;
- pacchetti personalizzati creati dalla demo.

I pacchetti vengono verificati dal controllo totale del progetto.

## Flusso consigliato

Dopo aver modificato o aggiunto domande:

```bash
python3 scripts/validate_questions.py
python3 scripts/build_database.py
python3 scripts/check_duplicates.py
python3 scripts/controllo_qualita_completo.py
python3 scripts/controllo_totale_progetto.py
```

Se tutti i controlli passano, il progetto è pronto per essere salvato e distribuito.

## Riutilizzo

Questo progetto può diventare la base per nuovi quiz e nuove app.

Per creare un nuovo quiz si può:

1. aggiungere un nuovo file JSON in `data/`;
2. seguire la struttura delle domande esistenti;
3. lanciare i motori di controllo;
4. generare il database finale;
5. esportare una demo o un pacchetto.

## Stato qualità

Lo stato attuale dei controlli è positivo:

- validazione database superata;
- build database superata;
- controllo duplicati superato;
- controllo qualità testuale superato;
- controllo Logica visiva superato;
- verifica premi ed effetti visivi superata;
- pacchetti principali validi.

Il progetto è pronto come base solida per nuove espansioni, nuovi argomenti e future app quiz.
