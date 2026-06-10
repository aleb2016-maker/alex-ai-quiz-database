import { useState } from "react";
import "./App.css";

function App() {
  // Qui salviamo quello che scrive l'utente.
  const [messaggioUtente, setMessaggioUtente] = useState("");

  // Qui salviamo il messaggio principale dell'agente.
  const [messaggioAgente, setMessaggioAgente] = useState("");

  // Qui salviamo il tipo di risposta: chat, quiz, memoria.
  const [tipoRisposta, setTipoRisposta] = useState("");

  // Qui salviamo il risultato completo restituito dall'agente.
  const [risultatoAgente, setRisultatoAgente] = useState(null);

  // Qui controlliamo se il backend sta rispondendo.
  const [staCaricando, setStaCaricando] = useState(false);

  async function inviaMessaggio() {
    if (messaggioUtente.trim() === "") {
      setMessaggioAgente("Scrivi prima un messaggio.");
      setTipoRisposta("");
      setRisultatoAgente(null);
      return;
    }

    setStaCaricando(true);
    setMessaggioAgente("");
    setTipoRisposta("");
    setRisultatoAgente(null);

    try {
      const risposta = await fetch("http://127.0.0.1:8000/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: messaggioUtente,
        }),
      });

      const dati = await risposta.json();

      setTipoRisposta(dati.tipo);
      setMessaggioAgente(dati.messaggio);
      setRisultatoAgente(dati.risultato);
    } catch (errore) {
      setTipoRisposta("errore");
      setMessaggioAgente("Errore: il backend FastAPI non risponde.");
      setRisultatoAgente(null);
    }

    setStaCaricando(false);
  }

  function mostraRisultatoChat() {
    return (
      <div className="scheda-risultato">
        <h3>Risposta chat</h3>
        <p>{risultatoAgente}</p>
      </div>
    );
  }

  function mostraRisultatoQuiz() {
    return (
      <div className="lista-domande">
        {risultatoAgente.map((domandaQuiz, indice) => (
          <div className="scheda-domanda" key={indice}>
            <div className="intestazione-domanda">
              <span>Domanda {indice + 1}</span>
              <span>{domandaQuiz.categoria}</span>
              <span>{domandaQuiz.difficolta}</span>
            </div>

            <h3>{domandaQuiz.domanda}</h3>

            <div className="lista-risposte">
              {domandaQuiz.risposte.map((risposta, indiceRisposta) => (
                <div className="risposta-quiz" key={indiceRisposta}>
                  <strong>{String.fromCharCode(65 + indiceRisposta)})</strong>
                  <span>{risposta}</span>
                </div>
              ))}
            </div>

            <div className="box-spiegazione">
              <strong>Risposta corretta:</strong>{" "}
              {String.fromCharCode(65 + domandaQuiz.risposta_corretta)}
              <br />
              <strong>Spiegazione:</strong> {domandaQuiz.spiegazione}
            </div>
          </div>
        ))}
      </div>
    );
  }

  function mostraRisultatoMemoria() {
    return (
      <div className="lista-memorie">
        {risultatoAgente.map((memoria) => (
          <div className="scheda-memoria" key={memoria.id}>
            <h3>{memoria.title}</h3>

            <p>
              <strong>Categoria:</strong> {memoria.category}
            </p>

            <p>
              <strong>Contenuto:</strong>
            </p>

            <p>{memoria.content}</p>

            <p className="data-memoria">
              Salvata il: {memoria.created_at}
            </p>
          </div>
        ))}
      </div>
    );
  }

  function mostraRisultatoAgente() {
    if (!risultatoAgente) {
      return null;
    }

    if (tipoRisposta === "chat") {
      return mostraRisultatoChat();
    }

    if (tipoRisposta === "quiz") {
      return mostraRisultatoQuiz();
    }

    if (tipoRisposta === "memoria") {
      return mostraRisultatoMemoria();
    }

    return null;
  }

  return (
    <div className="pagina">
      <div className="contenitore-chat">
        <h1>Alex AI Workspace</h1>

        <p className="sottotitolo">
          Mini agente personale collegato a chat, quiz e memoria.
        </p>

        <div className="box-esempi">
          <p>Prova a scrivere:</p>
          <ul>
            <li>Ciao agente</li>
            <li>Creami un quiz di AI</li>
            <li>Mostrami le mie preferenze salvate in memoria</li>
          </ul>
        </div>

        <textarea
          value={messaggioUtente}
          onChange={(evento) => setMessaggioUtente(evento.target.value)}
          placeholder="Scrivi una richiesta per il tuo agente..."
        />

        <button onClick={inviaMessaggio}>
          {staCaricando ? "Invio..." : "Invia all'agente"}
        </button>

        <div className="box-risposta">
          <h2>Risposta agente</h2>

          {tipoRisposta && (
            <p className="tipo-risposta">
              Tipo risposta: <strong>{tipoRisposta}</strong>
            </p>
          )}

          {messaggioAgente && (
            <p className="messaggio-agente">{messaggioAgente}</p>
          )}

          {mostraRisultatoAgente()}
        </div>
      </div>
    </div>
  );
}

export default App;