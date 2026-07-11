package com.crosshub.amazon.util;

import java.util.Locale;
import java.util.Map;
import java.util.regex.Pattern;

/** 过滤 Seller Central 误抓的 UI 文案 / 纯价格 / 非商品 ASIN。 */
public final class AmazonProductRowFilter {
    private static final Pattern ASIN = Pattern.compile("^[A-Z0-9]{10}$", Pattern.CASE_INSENSITIVE);
    private static final Pattern GCID_LIKE = Pattern.compile("^G\\d{9}$", Pattern.CASE_INSENSITIVE);
    private static final Pattern STATUS_ONLY = Pattern.compile("^(在售|停售|缺货|active|inactive|out of stock|–|-)$", Pattern.CASE_INSENSITIVE);
    private static final Pattern PRICE_ONLY = Pattern.compile(
            "^(?:US\\$|USD\\$?|\\$|EUR€?|£|¥|CN¥|R\\$)?\\s*[\\d,]+(?:\\.\\d+)?(?:\\s*(?:USD|EUR|GBP|CNY|JPY))?\\s*$",
            Pattern.CASE_INSENSITIVE
    );
    private static final Pattern UI_ACTION = Pattern.compile(
            "^(了解更多|创建\\s*A/?B\\s*试验|查看建议|编辑未来|报告缺失|learn more|create a/?b test|view suggestion|edit future|report missing)",
            Pattern.CASE_INSENSITIVE
    );
    private static final Pattern DATE_ONLY = Pattern.compile(
            "(\\d{4}[/-]\\d{1,2}[/-]\\d{1,2}.*(?:GMT|UTC|AM|PM))|(^\\d{4}[/-]\\d{1,2}[/-]\\d{1,2}$)",
            Pattern.CASE_INSENSITIVE
    );

    private AmazonProductRowFilter() {
    }

    public static boolean isValidProductRow(Map<String, Object> row) {
        if (row == null || row.isEmpty()) {
            return false;
        }
        String asin = text(row.get("asin")).toUpperCase(Locale.ROOT);
        if (!ASIN.matcher(asin).matches() || GCID_LIKE.matcher(asin).matches()) {
            return false;
        }
        String name = text(firstNonBlank(row.get("product_name"), row.get("productName")));
        if (isJunkProductName(name)) {
            return false;
        }
        if (!name.matches(".*[A-Za-z\\u4e00-\\u9fff].*")) {
            return false;
        }
        return hasActivity(row) || looksLikeProductTitle(name);
    }

    public static boolean isJunkProductName(String name) {
        String text = text(name);
        if (text.isEmpty() || STATUS_ONLY.matcher(text).matches() || PRICE_ONLY.matcher(text).matches()) {
            return true;
        }
        if (UI_ACTION.matcher(text).find()) {
            return true;
        }
        if (DATE_ONLY.matcher(text).find()) {
            return true;
        }
        if (text.length() <= 10 && !text.matches(".*[A-Za-z]{4,}.*") && text.matches("[\\u4e00-\\u9fff/A-B\\s]+")) {
            return true;
        }
        return false;
    }

    private static boolean looksLikeProductTitle(String name) {
        String text = text(name);
        if (isJunkProductName(text)) {
            return false;
        }
        if (text.length() >= 24) {
            return true;
        }
        var matcher = Pattern.compile("[A-Za-z\\u4e00-\\u9fff]{2,}").matcher(text);
        int words = 0;
        while (matcher.find()) {
            words++;
        }
        return words >= 4;
    }

    private static boolean hasActivity(Map<String, Object> row) {
        return parseAmount(firstNonBlank(row.get("revenue_30d"), row.get("revenue7d"))) > 0
                || parseAmount(firstNonBlank(row.get("orders_30d"), row.get("orders7d"))) > 0
                || parseAmount(firstNonBlank(row.get("inventory"), row.get("units_on_hand"))) > 0;
    }

    private static double parseAmount(Object value) {
        if (value == null) {
            return 0;
        }
        String cleaned = String.valueOf(value).replaceAll("[^\\d.-]", "");
        if (cleaned.isBlank()) {
            return 0;
        }
        try {
            return Double.parseDouble(cleaned);
        } catch (NumberFormatException ex) {
            return 0;
        }
    }

    private static String firstNonBlank(Object... values) {
        for (Object value : values) {
            String text = text(value);
            if (!text.isEmpty()) {
                return text;
            }
        }
        return "";
    }

    private static String text(Object value) {
        return value == null ? "" : String.valueOf(value).trim();
    }
}
