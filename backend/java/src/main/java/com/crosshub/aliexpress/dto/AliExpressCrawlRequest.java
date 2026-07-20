package com.crosshub.aliexpress.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record AliExpressCrawlRequest(
        @JsonProperty("report_time") String reportTime,
        /** orders | violations | all（默认 all：订单+违规单次爬取） */
        @JsonProperty("scope") String scope,
        @JsonProperty("force") Boolean force,
        @JsonProperty("record_cooldown") Boolean recordCooldown
) {
    public String resolvedScope() {
        if (scope == null || scope.isBlank()) {
            return "all";
        }
        return scope.trim().toLowerCase();
    }

    public boolean resolvedForce() {
        return Boolean.TRUE.equals(force);
    }

    public boolean resolvedRecordCooldown() {
        return recordCooldown == null || recordCooldown;
    }
}

