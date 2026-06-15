# Creare una web app quiz

## File principale

Il file generato si chiama:

database_quiz.json

## Uso semplice

Nel pacchetto web trovi:

index.html
database_quiz.json

Apri index.html nel browser.

## Uso in React o Next.js

Puoi mettere database_quiz.json dentro la cartella public e caricarlo con fetch.

Esempio:

const response = await fetch("/database_quiz.json");
const databaseQuiz = await response.json();

## Vantaggio

Il database resta separato dalla grafica. Puoi creare quiz diversi cambiando solo il JSON.
