package com.alex.pdf;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class MinimalJson {
    private final String text;
    private int index;

    private MinimalJson(String text) {
        this.text = text == null ? "" : text;
        this.index = 0;
    }

    public static Object parse(String text) {
        MinimalJson parser = new MinimalJson(text);
        Object value = parser.parseValue();
        parser.skipWhitespace();
        if (!parser.isEnd()) {
            throw parser.error("Caratteri extra dopo la fine del JSON");
        }
        return value;
    }

    private Object parseValue() {
        skipWhitespace();
        if (isEnd()) {
            throw error("JSON vuoto o incompleto");
        }
        char c = peek();
        if (c == '{') {
            return parseObject();
        }
        if (c == '[') {
            return parseArray();
        }
        if (c == '"') {
            return parseString();
        }
        if (c == 't' || c == 'f') {
            return parseBoolean();
        }
        if (c == 'n') {
            return parseNull();
        }
        if (c == '-' || Character.isDigit(c)) {
            return parseNumber();
        }
        throw error("Valore JSON non valido");
    }

    private Map<String, Object> parseObject() {
        expect('{');
        Map<String, Object> map = new LinkedHashMap<>();
        skipWhitespace();
        if (tryConsume('}')) {
            return map;
        }
        while (true) {
            skipWhitespace();
            String key = parseString();
            skipWhitespace();
            expect(':');
            Object value = parseValue();
            map.put(key, value);
            skipWhitespace();
            if (tryConsume('}')) {
                break;
            }
            expect(',');
        }
        return map;
    }

    private List<Object> parseArray() {
        expect('[');
        List<Object> list = new ArrayList<>();
        skipWhitespace();
        if (tryConsume(']')) {
            return list;
        }
        while (true) {
            list.add(parseValue());
            skipWhitespace();
            if (tryConsume(']')) {
                break;
            }
            expect(',');
        }
        return list;
    }

    private String parseString() {
        expect('"');
        StringBuilder out = new StringBuilder();
        while (!isEnd()) {
            char c = next();
            if (c == '"') {
                return out.toString();
            }
            if (c == '\\') {
                if (isEnd()) {
                    throw error("Escape JSON incompleto");
                }
                char e = next();
                switch (e) {
                    case '"': out.append('"'); break;
                    case '\\': out.append('\\'); break;
                    case '/': out.append('/'); break;
                    case 'b': out.append('\b'); break;
                    case 'f': out.append('\f'); break;
                    case 'n': out.append('\n'); break;
                    case 'r': out.append('\r'); break;
                    case 't': out.append('\t'); break;
                    case 'u': out.append(parseUnicode()); break;
                    default: throw error("Escape JSON non valido");
                }
            } else {
                out.append(c);
            }
        }
        throw error("Stringa JSON non chiusa");
    }

    private char parseUnicode() {
        if (index + 4 > text.length()) {
            throw error("Escape unicode incompleto");
        }
        String hex = text.substring(index, index + 4);
        index += 4;
        try {
            return (char) Integer.parseInt(hex, 16);
        } catch (NumberFormatException ex) {
            throw error("Escape unicode non valido");
        }
    }

    private Boolean parseBoolean() {
        if (match("true")) {
            return Boolean.TRUE;
        }
        if (match("false")) {
            return Boolean.FALSE;
        }
        throw error("Boolean JSON non valido");
    }

    private Object parseNull() {
        if (match("null")) {
            return null;
        }
        throw error("Null JSON non valido");
    }

    private Number parseNumber() {
        int start = index;
        if (peek() == '-') {
            index++;
        }
        while (!isEnd() && Character.isDigit(peek())) {
            index++;
        }
        boolean decimal = false;
        if (!isEnd() && peek() == '.') {
            decimal = true;
            index++;
            while (!isEnd() && Character.isDigit(peek())) {
                index++;
            }
        }
        if (!isEnd() && (peek() == 'e' || peek() == 'E')) {
            decimal = true;
            index++;
            if (!isEnd() && (peek() == '+' || peek() == '-')) {
                index++;
            }
            while (!isEnd() && Character.isDigit(peek())) {
                index++;
            }
        }
        String raw = text.substring(start, index);
        try {
            return decimal ? Double.parseDouble(raw) : Long.parseLong(raw);
        } catch (NumberFormatException ex) {
            throw error("Numero JSON non valido");
        }
    }

    private boolean match(String value) {
        if (text.startsWith(value, index)) {
            index += value.length();
            return true;
        }
        return false;
    }

    private void skipWhitespace() {
        while (!isEnd() && Character.isWhitespace(peek())) {
            index++;
        }
    }

    private void expect(char expected) {
        skipWhitespace();
        if (isEnd() || peek() != expected) {
            throw error("Atteso '" + expected + "'");
        }
        index++;
    }

    private boolean tryConsume(char expected) {
        skipWhitespace();
        if (!isEnd() && peek() == expected) {
            index++;
            return true;
        }
        return false;
    }

    private char peek() {
        return text.charAt(index);
    }

    private char next() {
        return text.charAt(index++);
    }

    private boolean isEnd() {
        return index >= text.length();
    }

    private RuntimeException error(String message) {
        return new IllegalArgumentException(message + " alla posizione " + index);
    }
}
