package com.alex.pdf;

import java.awt.Color;
import java.util.Locale;

public class PdfTheme {
    public final Color primary;
    public final Color secondary;
    public final Color background;
    public final Color cardBackground;
    public final Color text;
    public final Color mutedText;
    public final Color line;

    public PdfTheme(Color primary, Color secondary, Color background, Color cardBackground, Color text, Color mutedText, Color line) {
        this.primary = primary;
        this.secondary = secondary;
        this.background = background;
        this.cardBackground = cardBackground;
        this.text = text;
        this.mutedText = mutedText;
        this.line = line;
    }

    public static PdfTheme forName(String name) {
        String key = name == null ? "" : name.toLowerCase(Locale.ROOT);

        if (key.contains("sport") || key.contains("allen")) {
            return new PdfTheme(
                    new Color(20, 116, 95),
                    new Color(43, 176, 138),
                    new Color(236, 250, 245),
                    new Color(255, 255, 255),
                    new Color(16, 37, 34),
                    new Color(79, 99, 95),
                    new Color(180, 222, 211)
            );
        }

        if (key.contains("poesia") || key.contains("poem")) {
            return new PdfTheme(
                    new Color(108, 63, 151),
                    new Color(169, 126, 214),
                    new Color(247, 241, 253),
                    new Color(255, 255, 255),
                    new Color(44, 33, 56),
                    new Color(100, 85, 116),
                    new Color(213, 195, 232)
            );
        }

        if (key.contains("storia") || key.contains("racconto")) {
            return new PdfTheme(
                    new Color(151, 83, 39),
                    new Color(210, 145, 84),
                    new Color(253, 246, 236),
                    new Color(255, 255, 255),
                    new Color(55, 38, 26),
                    new Color(112, 91, 72),
                    new Color(230, 201, 168)
            );
        }

        if (key.contains("curriculum") || key.contains("cv")) {
            return new PdfTheme(
                    new Color(47, 78, 132),
                    new Color(89, 126, 194),
                    new Color(238, 244, 252),
                    new Color(255, 255, 255),
                    new Color(24, 36, 60),
                    new Color(86, 98, 120),
                    new Color(184, 203, 232)
            );
        }

        if (key.contains("hobby") || key.contains("progetto") || key.contains("tempo")) {
            return new PdfTheme(
                    new Color(196, 105, 31),
                    new Color(232, 151, 61),
                    new Color(255, 247, 235),
                    new Color(255, 255, 255),
                    new Color(66, 43, 22),
                    new Color(120, 91, 55),
                    new Color(240, 203, 158)
            );
        }

        return new PdfTheme(
                new Color(37, 73, 132),
                new Color(37, 151, 140),
                new Color(236, 242, 250),
                new Color(255, 255, 255),
                new Color(24, 35, 51),
                new Color(88, 102, 122),
                new Color(188, 203, 225)
        );
    }
}
