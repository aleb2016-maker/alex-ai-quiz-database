package com.alex.pdf;

import java.util.ArrayList;
import java.util.List;

public class CardData {
    public final String title;
    public final String badge;
    public final String body;
    public final String category;
    public final String imagePath;
    public final List<String> points;

    public CardData(String title, String badge, String body, String category, String imagePath, List<String> points) {
        this.title = safe(title, "Senza titolo");
        this.badge = safe(badge, "CARD");
        this.body = safe(body, "");
        this.category = safe(category, "generale");
        this.imagePath = safe(imagePath, "");
        this.points = points == null ? new ArrayList<>() : cleanPoints(points);
    }

    private static List<String> cleanPoints(List<String> raw) {
        List<String> cleaned = new ArrayList<>();
        for (String item : raw) {
            String value = safe(item, "");
            if (!value.isBlank()) {
                cleaned.add(value);
            }
        }
        return cleaned;
    }

    private static String safe(String value, String fallback) {
        if (value == null) {
            return fallback;
        }
        String cleaned = value.trim();
        return cleaned.isEmpty() ? fallback : cleaned;
    }
}
