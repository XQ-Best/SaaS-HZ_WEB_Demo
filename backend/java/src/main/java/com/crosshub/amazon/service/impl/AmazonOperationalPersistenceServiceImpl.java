package com.crosshub.amazon.service.impl;

import com.crosshub.amazon.entity.*;
import com.crosshub.amazon.repository.*;
import com.crosshub.amazon.service.AmazonOperationalPersistenceService;
import com.crosshub.amazon.util.AmazonProductRowFilter;
import com.crosshub.platform.repository.PlatformAccountRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
public class AmazonOperationalPersistenceServiceImpl implements AmazonOperationalPersistenceService {
    private static final DateTimeFormatter TS = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final AmazonProductSnapshotRepository productSnapshotRepository;
    private final AmazonAccountMetricRepository accountMetricRepository;
    private final AmazonOperationalItemRepository operationalItemRepository;
    private final AmazonSyncVersionRepository syncVersionRepository;
    private final AmazonProductVersionRepository productVersionRepository;
    private final AmazonMetricVersionRepository metricVersionRepository;
    private final AmazonItemVersionRepository itemVersionRepository;
    private final PlatformAccountRepository platformAccountRepository;
    private final ObjectMapper objectMapper;

    public AmazonOperationalPersistenceServiceImpl(
            AmazonProductSnapshotRepository productSnapshotRepository,
            AmazonAccountMetricRepository accountMetricRepository,
            AmazonOperationalItemRepository operationalItemRepository,
            AmazonSyncVersionRepository syncVersionRepository,
            AmazonProductVersionRepository productVersionRepository,
            AmazonMetricVersionRepository metricVersionRepository,
            AmazonItemVersionRepository itemVersionRepository,
            PlatformAccountRepository platformAccountRepository,
            ObjectMapper objectMapper
    ) {
        this.productSnapshotRepository = productSnapshotRepository;
        this.accountMetricRepository = accountMetricRepository;
        this.operationalItemRepository = operationalItemRepository;
        this.syncVersionRepository = syncVersionRepository;
        this.productVersionRepository = productVersionRepository;
        this.metricVersionRepository = metricVersionRepository;
        this.itemVersionRepository = itemVersionRepository;
        this.platformAccountRepository = platformAccountRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public void persistSyncResult(AmazonSyncJob job, Map<String, Object> result) {
        Long tenantId = job.getTenantId();
        String accountId = job.getPlatformAccountId();
        String syncedAt = text(result.get("synced_at"));
        if (syncedAt.isBlank()) syncedAt = LocalDateTime.now().format(TS);

        persistMerchantId(tenantId, accountId, text(result.get("merchant_id")));

        List<Map<String, Object>> metrics = rows(result.get("account_metrics"));
        if (metrics.isEmpty()) {
            metrics = rows(result.get("metrics"));
        }
        if (!metrics.isEmpty()) {
            accountMetricRepository.deleteByTenantIdAndPlatformAccountId(tenantId, accountId);
            for (Map<String, Object> row : metrics) {
                accountMetricRepository.save(buildMetricSnapshot(tenantId, accountId, syncedAt, row));
            }
        }

        List<Map<String, Object>> products = rows(result.get("products"));
        if (!products.isEmpty()) {
            productSnapshotRepository.deleteByTenantIdAndPlatformAccountId(tenantId, accountId);
            for (Map<String, Object> row : products) {
                if (!AmazonProductRowFilter.isValidProductRow(row)) {
                    continue;
                }
                productSnapshotRepository.save(buildProductSnapshot(tenantId, accountId, syncedAt, row));
            }
        }

        persistItems(tenantId, accountId, syncedAt, "buyer_message", rows(result.get("buyer_messages")));
        persistItems(tenantId, accountId, syncedAt, "review", rows(result.get("reviews")));
        persistItems(tenantId, accountId, syncedAt, "coupon", rows(result.get("coupons")));
        persistItems(tenantId, accountId, syncedAt, "seller_news", rows(result.get("seller_news")));
        persistItems(tenantId, accountId, syncedAt, "shipment", rows(result.get("shipments")));
        persistItems(tenantId, accountId, syncedAt, "case", rows(result.get("cases")));
        persistItems(tenantId, accountId, syncedAt, "outbound_order", rows(result.get("outbound_orders")));

        persistSyncVersion(job, result, syncedAt, metrics, products);
    }

    @Override
    @Transactional
    public void finalizeSyncVersion(String syncJobId, String status, String resultSummary) {
        if (syncJobId == null || syncJobId.isBlank()) {
            return;
        }
        syncVersionRepository.findBySyncJobId(syncJobId).ifPresent(version -> {
            version.setStatus(status == null || status.isBlank() ? "success" : status);
            if (resultSummary != null && !resultSummary.isBlank()) {
                version.setResultSummary(resultSummary);
            }
            syncVersionRepository.save(version);
        });
    }

    private void persistSyncVersion(
            AmazonSyncJob job,
            Map<String, Object> result,
            String syncedAt,
            List<Map<String, Object>> metrics,
            List<Map<String, Object>> products
    ) {
        String versionId = "amz_ver_" + UUID.randomUUID();
        AmazonSyncVersion version = new AmazonSyncVersion();
        version.setId(versionId);
        version.setSyncJobId(job.getId());
        version.setTenantId(job.getTenantId());
        version.setPlatformAccountId(job.getPlatformAccountId());
        version.setScope(job.getScope());
        version.setStatus("success");
        version.setSyncedAt(syncedAt);
        version.setCreatedAt(LocalDateTime.now().format(TS));

        int productCount = 0;
        for (Map<String, Object> row : products) {
            if (!AmazonProductRowFilter.isValidProductRow(row)) {
                continue;
            }
            productVersionRepository.save(buildProductVersion(versionId, job, syncedAt, row));
            productCount++;
        }

        int metricCount = 0;
        for (Map<String, Object> row : metrics) {
            metricVersionRepository.save(buildMetricVersion(versionId, job, syncedAt, row));
            metricCount++;
        }

        int itemCount = 0;
        itemCount += persistVersionItems(versionId, job, syncedAt, "buyer_message", rows(result.get("buyer_messages")));
        itemCount += persistVersionItems(versionId, job, syncedAt, "review", rows(result.get("reviews")));
        itemCount += persistVersionItems(versionId, job, syncedAt, "coupon", rows(result.get("coupons")));
        itemCount += persistVersionItems(versionId, job, syncedAt, "seller_news", rows(result.get("seller_news")));
        itemCount += persistVersionItems(versionId, job, syncedAt, "shipment", rows(result.get("shipments")));
        itemCount += persistVersionItems(versionId, job, syncedAt, "case", rows(result.get("cases")));
        itemCount += persistVersionItems(versionId, job, syncedAt, "outbound_order", rows(result.get("outbound_orders")));

        version.setProductCount(productCount);
        version.setMetricCount(metricCount);
        version.setItemCount(itemCount);
        version.setResultSummary(json(result.get("result_summary")));
        syncVersionRepository.save(version);
    }

    private int persistVersionItems(
            String versionId,
            AmazonSyncJob job,
            String syncedAt,
            String type,
            List<Map<String, Object>> rows
    ) {
        if (rows.isEmpty()) {
            return 0;
        }
        for (Map<String, Object> row : rows) {
            AmazonItemVersion item = new AmazonItemVersion();
            item.setId(textOr(row.get("id"), type + "_" + UUID.randomUUID()));
            item.setSyncVersionId(versionId);
            item.setTenantId(job.getTenantId());
            item.setPlatformAccountId(job.getPlatformAccountId());
            item.setItemType(type);
            item.setExternalKey(text(row.get("external_key")));
            item.setPayloadJson(json(row));
            item.setSyncedAt(textOr(row.get("synced_at"), syncedAt));
            itemVersionRepository.save(item);
        }
        return rows.size();
    }

    private AmazonAccountMetric buildMetricSnapshot(
            Long tenantId,
            String accountId,
            String syncedAt,
            Map<String, Object> row
    ) {
        AmazonAccountMetric m = new AmazonAccountMetric();
        m.setId(textOr(row.get("id"), "metric_" + UUID.randomUUID()));
        m.setTenantId(tenantId);
        m.setPlatformAccountId(accountId);
        m.setMetricKey(text(row.get("metric_key")));
        m.setMetricLabel(textOr(row.get("metric_label"), text(row.get("label"))));
        m.setStatus(textOr(row.get("status"), "normal"));
        m.setValueText(textOr(row.get("value_text"), text(row.get("value"))));
        m.setThresholdText(textOr(row.get("threshold_text"), text(row.get("threshold"))));
        m.setTrend(textOr(row.get("trend"), "stable"));
        m.setNoteText(textOr(row.get("note_text"), text(row.get("note"))));
        m.setSyncedAt(textOr(row.get("synced_at"), syncedAt));
        return m;
    }

    private AmazonMetricVersion buildMetricVersion(
            String versionId,
            AmazonSyncJob job,
            String syncedAt,
            Map<String, Object> row
    ) {
        AmazonMetricVersion m = new AmazonMetricVersion();
        m.setId("metric_ver_" + UUID.randomUUID());
        m.setSyncVersionId(versionId);
        m.setTenantId(job.getTenantId());
        m.setPlatformAccountId(job.getPlatformAccountId());
        m.setMetricKey(text(row.get("metric_key")));
        m.setMetricLabel(textOr(row.get("metric_label"), text(row.get("label"))));
        m.setStatus(textOr(row.get("status"), "normal"));
        m.setValueText(textOr(row.get("value_text"), text(row.get("value"))));
        m.setThresholdText(textOr(row.get("threshold_text"), text(row.get("threshold"))));
        m.setTrend(textOr(row.get("trend"), "stable"));
        m.setNoteText(textOr(row.get("note_text"), text(row.get("note"))));
        m.setSyncedAt(textOr(row.get("synced_at"), syncedAt));
        return m;
    }

    private AmazonProductSnapshot buildProductSnapshot(
            Long tenantId,
            String accountId,
            String syncedAt,
            Map<String, Object> row
    ) {
        AmazonProductSnapshot p = new AmazonProductSnapshot();
        p.setId(textOr(row.get("id"), "prd_" + UUID.randomUUID()));
        p.setTenantId(tenantId);
        p.setPlatformAccountId(accountId);
        applyProductFields(p, row, syncedAt);
        return p;
    }

    private AmazonProductVersion buildProductVersion(
            String versionId,
            AmazonSyncJob job,
            String syncedAt,
            Map<String, Object> row
    ) {
        AmazonProductVersion p = new AmazonProductVersion();
        p.setId("prd_ver_" + UUID.randomUUID());
        p.setSyncVersionId(versionId);
        p.setTenantId(job.getTenantId());
        p.setPlatformAccountId(job.getPlatformAccountId());
        applyProductFields(p, row, syncedAt);
        return p;
    }

    private void applyProductFields(Object target, Map<String, Object> row, String syncedAt) {
        if (target instanceof AmazonProductSnapshot p) {
            p.setAsin(text(row.get("asin")));
            p.setSku(text(row.get("sku")));
            p.setProductName(textOr(row.get("product_name"), text(row.get("productName"))));
            p.setOrders30d(intVal(row.get("orders_30d")));
            p.setRevenue30d(text(row.get("revenue_30d")));
            p.setPageViews(intVal(row.get("page_views")));
            p.setInventory(intVal(row.get("inventory")));
            p.setAcos(doubleVal(row.get("acos")));
            p.setAdSpend30d(text(row.get("ad_spend_30d")));
            p.setTacos(doubleVal(row.get("tacos")));
            p.setConversionRate(doubleVal(row.get("conversion_rate")));
            p.setPeriodDays(intVal(row.get("period_days")) == 0 ? 30 : intVal(row.get("period_days")));
            p.setRankNo(intVal(row.get("rank_no")));
            p.setCurrency(textOr(row.get("currency"), "USD"));
            p.setSyncedAt(textOr(row.get("synced_at"), syncedAt));
            return;
        }
        if (target instanceof AmazonProductVersion p) {
            p.setAsin(text(row.get("asin")));
            p.setSku(text(row.get("sku")));
            p.setProductName(textOr(row.get("product_name"), text(row.get("productName"))));
            p.setOrders30d(intVal(row.get("orders_30d")));
            p.setRevenue30d(text(row.get("revenue_30d")));
            p.setPageViews(intVal(row.get("page_views")));
            p.setInventory(intVal(row.get("inventory")));
            p.setAcos(doubleVal(row.get("acos")));
            p.setAdSpend30d(text(row.get("ad_spend_30d")));
            p.setTacos(doubleVal(row.get("tacos")));
            p.setConversionRate(doubleVal(row.get("conversion_rate")));
            p.setPeriodDays(intVal(row.get("period_days")) == 0 ? 30 : intVal(row.get("period_days")));
            p.setRankNo(intVal(row.get("rank_no")));
            p.setCurrency(textOr(row.get("currency"), "USD"));
            p.setSyncedAt(textOr(row.get("synced_at"), syncedAt));
        }
    }

    private void persistMerchantId(Long tenantId, String accountId, String merchantId) {
        if (merchantId == null || merchantId.isBlank()) {
            return;
        }
        platformAccountRepository.findByIdAndTenantId(accountId, tenantId).ifPresent(account -> {
            if (account.getAmazonMerchantId() == null || account.getAmazonMerchantId().isBlank()) {
                account.setAmazonMerchantId(merchantId);
                platformAccountRepository.save(account);
            }
        });
    }

    private void persistItems(Long tenantId, String accountId, String syncedAt, String type, List<Map<String, Object>> rows) {
        if (rows.isEmpty()) return;
        operationalItemRepository.deleteByTenantIdAndPlatformAccountIdAndItemType(tenantId, accountId, type);
        for (Map<String, Object> row : rows) {
            AmazonOperationalItem item = new AmazonOperationalItem();
            item.setId(textOr(row.get("id"), type + "_" + UUID.randomUUID()));
            item.setTenantId(tenantId);
            item.setPlatformAccountId(accountId);
            item.setItemType(type);
            item.setExternalKey(text(row.get("external_key")));
            item.setPayloadJson(json(row));
            item.setSyncedAt(textOr(row.get("synced_at"), syncedAt));
            operationalItemRepository.save(item);
        }
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> rows(Object value) {
        if (!(value instanceof List<?> list)) return List.of();
        List<Map<String, Object>> out = new ArrayList<>();
        for (Object row : list) if (row instanceof Map<?, ?> m) out.add((Map<String, Object>) m);
        return out;
    }

    private String json(Object v) {
        if (v == null) {
            return "{}";
        }
        try {
            return objectMapper.writeValueAsString(v);
        } catch (Exception e) {
            return "{}";
        }
    }

    private String text(Object v) { return v == null ? "" : String.valueOf(v).trim(); }
    private String textOr(Object v, String fb) { String t = text(v); return t.isBlank() ? fb : t; }
    private Integer intVal(Object v) { try { return v == null || String.valueOf(v).isBlank() ? 0 : Integer.parseInt(String.valueOf(v)); } catch (Exception e) { return 0; } }
    private Double doubleVal(Object v) { try { return v == null || String.valueOf(v).isBlank() ? 0d : Double.parseDouble(String.valueOf(v)); } catch (Exception e) { return 0d; } }
}
