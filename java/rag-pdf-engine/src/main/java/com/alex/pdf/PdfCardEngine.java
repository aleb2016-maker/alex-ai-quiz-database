package com.alex.pdf;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
import org.apache.pdfbox.pdmodel.font.PDType1Font;

import java.awt.Color;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class PdfCardEngine {
    private static final PDType1Font FONT_REGULAR = PDType1Font.HELVETICA;
    private static final PDType1Font FONT_BOLD = PDType1Font.HELVETICA_BOLD;

    // V21: vero image-only.
    // Una pagina 16:9 per ogni immagine card gia renderizzata.
    private static final float PAGE_WIDTH = 960f;
    private static final float PAGE_HEIGHT = 540f;
    private static final PDRectangle CARD_PAGE = new PDRectangle(PAGE_WIDTH, PAGE_HEIGHT);

    public void generate(PdfDocumentData data, Path outputPath) throws IOException {
        if (outputPath.getParent() != null) {
            Files.createDirectories(outputPath.getParent());
        }

        List<CardData> cards = data.cards;

        try (PDDocument document = new PDDocument()) {
            for (int i = 0; i < cards.size(); i++) {
                PDPage page = new PDPage(CARD_PAGE);
                document.addPage(page);
                try (PDPageContentStream cs = new PDPageContentStream(document, page)) {
                    drawRenderedCardImage(document, cs, cards.get(i), i + 1);
                }
            }
            document.save(outputPath.toFile());
        }
    }

    private void drawRenderedCardImage(PDDocument document, PDPageContentStream cs, CardData card, int pageNumber)
            throws IOException {
        Path imagePath = card.imagePath == null || card.imagePath.isBlank() ? null : Path.of(card.imagePath);

        cs.setNonStrokingColor(new Color(3, 12, 25));
        cs.addRect(0, 0, PAGE_WIDTH, PAGE_HEIGHT);
        cs.fill();

        if (imagePath == null || !Files.exists(imagePath)) {
            drawMissingImagePage(cs, card, pageNumber);
            return;
        }

        PDImageXObject image = PDImageXObject.createFromFileByContent(imagePath.toFile(), document);
        float imgW = image.getWidth();
        float imgH = image.getHeight();

        // Fit completo: nessun taglio dell'immagine card.
        float scale = Math.min(PAGE_WIDTH / imgW, PAGE_HEIGHT / imgH);
        float drawW = imgW * scale;
        float drawH = imgH * scale;
        float x = (PAGE_WIDTH - drawW) / 2f;
        float y = (PAGE_HEIGHT - drawH) / 2f;

        cs.drawImage(image, x, y, drawW, drawH);
    }

    private void drawMissingImagePage(PDPageContentStream cs, CardData card, int pageNumber) throws IOException {
        cs.setNonStrokingColor(new Color(245, 245, 245));
        cs.addRect(0, 0, PAGE_WIDTH, PAGE_HEIGHT);
        cs.fill();
        cs.setNonStrokingColor(new Color(130, 0, 0));
        drawText(cs, "IMMAGINE CARD MANCANTE", FONT_BOLD, 30f, 55, PAGE_HEIGHT - 90);
        cs.setNonStrokingColor(new Color(35, 35, 35));
        drawText(cs, "Pagina/card: " + pageNumber, FONT_BOLD, 18f, 55, PAGE_HEIGHT - 135);
        drawText(cs, "Titolo: " + card.title, FONT_REGULAR, 16f, 55, PAGE_HEIGHT - 170);
        drawText(cs, "Il JSON deve contenere imagePath verso la PNG/JPG gia generata dal motore card.", FONT_REGULAR, 14f, 55, PAGE_HEIGHT - 205);
    }

    private void drawText(PDPageContentStream cs, String text, PDType1Font font, float size, float x, float y)
            throws IOException {
        String safe = TextBox.cleanForPdf(text == null ? "" : text);
        if (safe.length() > 125) safe = safe.substring(0, 125);
        cs.beginText();
        cs.setFont(font, size);
        cs.newLineAtOffset(x, y);
        cs.showText(safe);
        cs.endText();
    }
}
