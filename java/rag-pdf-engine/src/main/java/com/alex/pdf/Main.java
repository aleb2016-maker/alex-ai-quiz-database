package com.alex.pdf;

import java.nio.file.Path;

public class Main {
    public static void main(String[] args) throws Exception {
        Path input;
        Path output;

        if (args.length >= 2) {
            input = Path.of(args[0]);
            output = Path.of(args[1]);
        } else {
            input = Path.of("input/sei_card_sport_image_only_v21.json");
            output = Path.of("output/SOLO-SEI-CARD-SPORT-V21.pdf");
        }

        System.out.println("📥 JSON input: " + input.toAbsolutePath());
        PdfDocumentData data = JsonCardLoader.load(input);
        System.out.println("📌 Titolo: " + data.title);
        System.out.println("🧩 Card lette: " + data.cards.size());
        System.out.println("📄 Card per pagina: " + data.cardsPerPage);

        new PdfCardEngine().generate(data, output);
        int pages = (int) Math.ceil(data.cards.size() / (double) data.cardsPerPage);
        System.out.println("✅ PDF V21 image-only generato: " + output.toAbsolutePath());
        System.out.println("📚 Pagine/card previste: " + pages);
        System.out.println("🟢 Regola layout: una pagina 16:9 per ogni immagine card gia generata");
    }
}
