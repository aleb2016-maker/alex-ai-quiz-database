package com.alex.pdf;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

public class JsonCardLoader {
    private JsonCardLoader() {
    }

    @SuppressWarnings("unchecked")
    public static PdfDocumentData load(Path jsonPath) throws IOException {
        String raw = Files.readString(jsonPath, StandardCharsets.UTF_8);
        Object parsed = MinimalJson.parse(raw);
        if (!(parsed instanceof Map<?, ?>)) {
            throw new IllegalArgumentException("Il file JSON deve contenere un oggetto principale.");
        }
        return PdfDocumentData.fromJsonObject((Map<String, Object>) parsed);
    }
}
