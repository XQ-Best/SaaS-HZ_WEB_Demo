package com.crosshub.amazon.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "amazon_sync_version")
public class AmazonSyncVersion {
    @Id
    private String id;

    @Column(name = "sync_job_id", nullable = false)
    private String syncJobId;

    @Column(name = "tenant_id", nullable = false)
    private Long tenantId;

    @Column(name = "platform_account_id", nullable = false)
    private String platformAccountId;

    @Column(nullable = false)
    private String scope;

    @Column(nullable = false)
    private String status = "success";

    @Column(name = "synced_at", nullable = false)
    private String syncedAt;

    @Column(name = "product_count", nullable = false)
    private Integer productCount = 0;

    @Column(name = "metric_count", nullable = false)
    private Integer metricCount = 0;

    @Column(name = "item_count", nullable = false)
    private Integer itemCount = 0;

    @Column(name = "result_summary", nullable = false)
    private String resultSummary = "{}";

    @Column(name = "created_at", nullable = false)
    private String createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getSyncJobId() { return syncJobId; }
    public void setSyncJobId(String syncJobId) { this.syncJobId = syncJobId; }
    public Long getTenantId() { return tenantId; }
    public void setTenantId(Long tenantId) { this.tenantId = tenantId; }
    public String getPlatformAccountId() { return platformAccountId; }
    public void setPlatformAccountId(String platformAccountId) { this.platformAccountId = platformAccountId; }
    public String getScope() { return scope; }
    public void setScope(String scope) { this.scope = scope; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getSyncedAt() { return syncedAt; }
    public void setSyncedAt(String syncedAt) { this.syncedAt = syncedAt; }
    public Integer getProductCount() { return productCount; }
    public void setProductCount(Integer productCount) { this.productCount = productCount; }
    public Integer getMetricCount() { return metricCount; }
    public void setMetricCount(Integer metricCount) { this.metricCount = metricCount; }
    public Integer getItemCount() { return itemCount; }
    public void setItemCount(Integer itemCount) { this.itemCount = itemCount; }
    public String getResultSummary() { return resultSummary; }
    public void setResultSummary(String resultSummary) { this.resultSummary = resultSummary; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
