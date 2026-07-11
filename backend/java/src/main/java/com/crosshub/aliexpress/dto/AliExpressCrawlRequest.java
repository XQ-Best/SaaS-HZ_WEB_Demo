package com.crosshub.aliexpress.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record AliExpressCrawlRequest(
        @JsonProperty("report_time") String reportTime,
        /** orders | violations | all（默认 all：订单+违规单次爬取） */
        @JsonProperty("scope") String scope
) {
    public String resolvedScope() {
        if (scope == null || scope.isBlank()) {
            return "all";
        }
        return scope.trim().toLowerCase();
    }
}

