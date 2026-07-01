# mini_llm/lab/tokenizer_char_v1.py

from __future__ import annotations


class CharTokenizerV1:
    """
    Tokenizer semplice a caratteri.

    Trasforma testo in numeri e numeri in testo.
    Serve solo come primo test didattico per capire la base di un LLM.
    """

    def __init__(self, text: str):
        chars = sorted(list(set(text)))

        self.stoi = {char: index for index, char in enumerate(chars)}
        self.itos = {index: char for char, index in self.stoi.items()}
        self.vocab_size = len(chars)

    def encode(self, text: str) -> list[int]:
        return [self.stoi[char] for char in text if char in self.stoi]

    def decode(self, tokens: list[int]) -> str:
        return "".join(self.itos[token] for token in tokens if token in self.itos)


def main() -> None:
    corpus = """
    Questo è il primo piccolo test del nostro LLM personale.
    Il testo viene trasformato in numeri.
    Poi i numeri vengono trasformati di nuovo in testo.
    """

    tokenizer = CharTokenizerV1(corpus)

    testo_test = "piccolo LLM"
    tokens = tokenizer.encode(testo_test)
    testo_ricostruito = tokenizer.decode(tokens)

    print("Vocabolario totale:", tokenizer.vocab_size)
    print("Testo originale:", testo_test)
    print("Token numerici:", tokens)
    print("Testo ricostruito:", testo_ricostruito)


if __name__ == "__main__":
    main()
