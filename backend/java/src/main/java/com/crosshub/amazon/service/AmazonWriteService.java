package com.crosshub.amazon.service;

import java.util.List;
import java.util.Map;

public interface AmazonWriteService {
    String WRITE_TASK_TYPE = "amazon_write";

    Map<String, Object> replyMessage(String id, String templateId, String note);

    Map<String, Object> handleReview(String id, String note);

    Map<String, Object> acknowledgeCase(String id, String note);

    Map<String, Object> shipOutbound(String id, String trackingNo);

    Map<String, Object> getWriteJob(String jobId);

    List<Map<String, Object>> listWriteAudit(String itemId, int limit);

    void onAgentTaskCompleted(
            String agentTaskId,
            String status,
            Map<String, Object> result,
            String errorCode,
            String errorMessage
    );

    void onAgentTaskStarted(String agentTaskId);
}
