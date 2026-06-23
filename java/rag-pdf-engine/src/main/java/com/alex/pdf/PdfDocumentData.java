package com.alex.pdf;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class PdfDocumentData {
    public final String title;
    public final String subtitle;
    public final String theme;
    public final String footer;
    public final int cardsPerPage;
    public final List<CardData> cards;

    public PdfDocumentData(String title, String subtitle, String theme, String footer, int cardsPerPage, List<CardData> cards) {
        this.title = safe(title, "Documento formativo");
        this.subtitle = safe(subtitle, "Card generate dal motore RAG");
        this.theme = safe(theme, "azienda");
        this.footer = safe(footer, "Alex AI Workspace - Motore PDF Java");
        this.cardsPerPage = cardsPerPage <= 0 ? 2 : Math.min(4, Math.max(1, cardsPerPage));
        this.cards = cards == null ? new ArrayList<>() : cards;
    }

    @SuppressWarnings("unchecked")
    public static PdfDocumentData fromJsonObject(Map<String, Object> root) {
        String title = firstString(root, "title", "titolo", "documentTitle");
        String subtitle = firstString(root, "subtitle", "sottotitolo", "description", "descrizione");
        String theme = firstString(root, "theme", "tema", "documentType", "tipoDocumento");
        String footer = firstString(root, "footer", "piedePagina", "piePagina");
        int cardsPerPage = firstInt(root, 2, "cardsPerPage", "cards_per_page", "cardPerPagina");

        Object rawCards = firstObject(root, "cards", "card", "items", "contenuti");
        List<CardData> cards = new ArrayList<>();

        if (rawCards instanceof List<?>) {
            for (Object item : (List<?>) rawCards) {
                if (item instanceof Map<?, ?>) {
                    Map<String, Object> map = (Map<String, Object>) item;
                    String cardTitle = firstString(map, "title", "titolo", "heading");
                    String badge = firstString(map, "badge", "categoria", "label", "tipo");
                    String body = firstString(map, "body", "text", "testo", "contenuto", "description", "descrizione");
                    String category = firstString(map, "category", "categoriaGrafica", "theme", "tipoDocumento");
                    String imagePath = firstString(map, "imagePath", "image", "immagine", "icon", "icona");
                    List<String> points = firstStringList(map, "points", "bullets", "punti", "elenco");
                    cards.add(new CardData(cardTitle, badge, body, category, imagePath, points));
                }
            }
        }

        if (cards.isEmpty()) {
            throw new IllegalArgumentException("Il JSON non contiene card valide. Serve un array 'cards' con title/body/badge.");
        }

        return new PdfDocumentData(title, subtitle, theme, footer, cardsPerPage, cards);
    }

    private static String safe(String value, String fallback) {
        if (value == null) {
            return fallback;
        }
        String cleaned = value.trim();
        return cleaned.isEmpty() ? fallback : cleaned;
    }

    private static Object firstObject(Map<String, Object> map, String... keys) {
        for (String key : keys) {
            if (map.containsKey(key)) {
                return map.get(key);
            }
        }
        return null;
    }

    private static String firstString(Map<String, Object> map, String... keys) {
        Object value = firstObject(map, keys);
        if (value == null) {
            return "";
        }
        return String.valueOf(value);
    }

    private static int firstInt(Map<String, Object> map, int fallback, String... keys) {
        Object value = firstObject(map, keys);
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        if (value != null) {
            try {
                return Integer.parseInt(String.valueOf(value).trim());
            } catch (NumberFormatException ignored) {
                return fallback;
            }
        }
        return fallback;
    }

    private static List<String> firstStringList(Map<String, Object> map, String... keys) {
        Object value = firstObject(map, keys);
        List<String> result = new ArrayList<>();
        if (value instanceof List<?>) {
            for (Object item : (List<?>) value) {
                if (item != null) {
                    result.add(String.valueOf(item));
                }
            }
        }
        return result;
    }
}
