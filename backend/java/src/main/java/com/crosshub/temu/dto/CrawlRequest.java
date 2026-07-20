package com.crosshub.temu.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record CrawlRequest(String reportTime, Boolean seed, Boolean force, @JsonProperty("record_cooldown") Boolean recordCooldown) {
    public boolean resolvedForce() {
        return Boolean.TRUE.equals(force);
    }

    public boolean resolvedRecordCooldown() {
        return recordCooldown == null || recordCooldown;
    }
}
