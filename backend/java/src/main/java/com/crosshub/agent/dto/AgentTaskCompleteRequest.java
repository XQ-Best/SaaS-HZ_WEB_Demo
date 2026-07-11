package com.crosshub.agent.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public record AgentTaskCompleteRequest(
        String status,
        Map<String, Object> result,
        @JsonProperty("error_code") @JsonAlias("errorCode") String errorCode,
        @JsonProperty("error_message") @JsonAlias("errorMessage") String errorMessage
) {}
