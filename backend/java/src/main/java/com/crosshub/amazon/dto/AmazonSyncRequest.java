package com.crosshub.amazon.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record AmazonSyncRequest(
        String scope,
        @JsonProperty("platform_account_id") String platformAccountId,
        @JsonProperty("force") Boolean force,
        @JsonProperty("record_cooldown") Boolean recordCooldown
) {
    public boolean resolvedForce() {
        return Boolean.TRUE.equals(force);
    }

    public boolean resolvedRecordCooldown() {
        return recordCooldown == null || recordCooldown;
    }
}
