package com.crosshub.amazon.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "amazon_write_job")
public class AmazonWriteJob {
    @Id
    private String id;

    @Column(name = "tenant_id", nullable = false)
    private Long tenantId;

    @Column(name = "platform_account_id", nullable = false)
    private String platformAccountId;

    @Column(name = "agent_task_id", nullable = false)
    private String agentTaskId = "";

    @Column(name = "item_id", nullable = false)
    private String itemId;

    @Column(nullable = false)
    private String action;

    @Column(nullable = false)
    private String status;

    @Column(name = "request_json", nullable = false)
    private String requestJson = "{}";

    @Column(name = "result_json", nullable = false)
    private String resultJson = "{}";

    @Column(name = "error_code", nullable = false)
    private String errorCode = "";

    @Column(name = "error_message", nullable = false)
    private String errorMessage = "";

    @Column(name = "created_at", nullable = false)
    private String createdAt;

    @Column(name = "finished_at", nullable = false)
    private String finishedAt = "";

    @Column(name = "initiated_by_user_id")
    private Long initiatedByUserId;

    @Column(name = "initiated_by_name", nullable = false)
    private String initiatedByName = "";

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public Long getTenantId() { return tenantId; }
    public void setTenantId(Long tenantId) { this.tenantId = tenantId; }
    public String getPlatformAccountId() { return platformAccountId; }
    public void setPlatformAccountId(String platformAccountId) { this.platformAccountId = platformAccountId; }
    public String getAgentTaskId() { return agentTaskId; }
    public void setAgentTaskId(String agentTaskId) { this.agentTaskId = agentTaskId; }
    public String getItemId() { return itemId; }
    public void setItemId(String itemId) { this.itemId = itemId; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getRequestJson() { return requestJson; }
    public void setRequestJson(String requestJson) { this.requestJson = requestJson; }
    public String getResultJson() { return resultJson; }
    public void setResultJson(String resultJson) { this.resultJson = resultJson; }
    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getFinishedAt() { return finishedAt; }
    public void setFinishedAt(String finishedAt) { this.finishedAt = finishedAt; }
    public Long getInitiatedByUserId() { return initiatedByUserId; }
    public void setInitiatedByUserId(Long initiatedByUserId) { this.initiatedByUserId = initiatedByUserId; }
    public String getInitiatedByName() { return initiatedByName; }
    public void setInitiatedByName(String initiatedByName) { this.initiatedByName = initiatedByName; }
}
