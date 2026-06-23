package com.alex.pdf;

import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDFont;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class TextBox {
    private TextBox() {
    }

    public static String cleanForPdf(String text) {
        if (text == null) {
            return "";
        }
        return text
                .replace('\u2013', '-')
                .replace('\u2014', '-')
                .replace('\u2018', '\'')
                .replace('\u2019', '\'')
                .replace('\u201c', '"')
                .replace('\u201d', '"')
                .replace('\u2026', '.')
                .replace('\u2022', '-')
                .replace('\u00a0', ' ')
                .replaceAll("[\\p{So}\\p{Cn}]", "")
                .trim();
    }

    public static List<String> wrap(String text, PDFont font, float fontSize, float maxWidth) throws IOException {
        String cleaned = cleanForPdf(text).replace('\n', ' ').replace('\r', ' ');
        String[] words = cleaned.split("\\s+");
        List<String> lines = new ArrayList<>();
        StringBuilder current = new StringBuilder();

        for (String word : words) {
            if (word.isEmpty()) {
                continue;
            }
            String candidate = current.length() == 0 ? word : current + " " + word;
            if (width(candidate, font, fontSize) <= maxWidth) {
                current.setLength(0);
                current.append(candidate);
            } else {
                if (current.length() > 0) {
                    lines.add(current.toString());
                    current.setLength(0);
                }
                if (width(word, font, fontSize) <= maxWidth) {
                    current.append(word);
                } else {
                    lines.addAll(splitLongWord(word, font, fontSize, maxWidth));
                }
            }
        }

        if (current.length() > 0) {
            lines.add(current.toString());
        }

        if (lines.isEmpty()) {
            lines.add("");
        }
        return lines;
    }

    public static float drawWrapped(PDPageContentStream cs, String text, PDFont font, float fontSize,
                                    float x, float y, float maxWidth, float lineHeight, int maxLines) throws IOException {
        List<String> lines = wrap(text, font, fontSize, maxWidth);
        int count = Math.min(lines.size(), maxLines);
        for (int i = 0; i < count; i++) {
            String line = lines.get(i);
            if (i == count - 1 && lines.size() > maxLines) {
                line = ellipsize(line, font, fontSize, maxWidth);
            }
            cs.beginText();
            cs.setFont(font, fontSize);
            cs.newLineAtOffset(x, y - i * lineHeight);
            cs.showText(cleanForPdf(line));
            cs.endText();
        }
        return count * lineHeight;
    }

    private static List<String> splitLongWord(String word, PDFont font, float fontSize, float maxWidth) throws IOException {
        List<String> parts = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        for (int i = 0; i < word.length(); i++) {
            String candidate = current.toString() + word.charAt(i);
            if (width(candidate, font, fontSize) <= maxWidth) {
                current.append(word.charAt(i));
            } else {
                if (current.length() > 0) {
                    parts.add(current.toString());
                    current.setLength(0);
                }
                current.append(word.charAt(i));
            }
        }
        if (current.length() > 0) {
            parts.add(current.toString());
        }
        return parts;
    }

    private static String ellipsize(String line, PDFont font, float fontSize, float maxWidth) throws IOException {
        String suffix = "...";
        String candidate = line;
        while (candidate.length() > 0 && width(candidate + suffix, font, fontSize) > maxWidth) {
            candidate = candidate.substring(0, candidate.length() - 1).trim();
        }
        return candidate + suffix;
    }

    private static float width(String value, PDFont font, float fontSize) throws IOException {
        return font.getStringWidth(cleanForPdf(value)) / 1000f * fontSize;
    }
}
