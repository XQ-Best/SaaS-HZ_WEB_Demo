package com.crosshub.common;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class TenantCrawlCooldownService {
    public static final long COOLDOWN_MS = 3L * 60 * 60 * 1000;
    private static final DateTimeFormatter TS = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final JdbcTemplate jdbc;
    private final ConcurrentHashMap<String, Boolean> pendingJobRecordFlags = new ConcurrentHashMap<>();

    public TenantCrawlCooldownService(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void registerJobRecordPolicy(String jobId, boolean recordCooldown) {
        if (jobId == null || jobId.isBlank()) {
            return;
        }
        pendingJobRecordFlags.put(jobId, recordCooldown);
    }

    public void onJobSuccess(String jobId, Long tenantId) {
        if (tenantId == null || tenantId <= 0) {
            return;
        }
        Boolean record = jobId == null ? Boolean.TRUE : pendingJobRecordFlags.remove(jobId);
        if (record == null || record) {
            recordSuccess(tenantId);
        }
    }

    public void assertAllowed(Long tenantId, boolean force) {
        if (force || tenantId == null || tenantId <= 0) {
            return;
        }
        long remaining = remainingMs(tenantId);
        if (remaining > 0) {
            throw new CrawlCooldownException(remaining);
        }
    }

    public long remainingMs(Long tenantId) {
        LocalDateTime last = loadLastSuccessAt(tenantId);
        if (last == null) {
            return 0;
        }
        long elapsed = ChronoUnit.MILLIS.between(last, LocalDateTime.now());
        long remaining = COOLDOWN_MS - elapsed;
        return remaining > 0 ? remaining : 0;
    }

    public void recordSuccess(Long tenantId) {
        if (tenantId == null || tenantId <= 0) {
            return;
        }
        String now = now();
        jdbc.update("""
                INSERT INTO tenant_crawl_cooldown (tenant_id, last_success_at, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(tenant_id) DO UPDATE SET
                  last_success_at = excluded.last_success_at,
                  updated_at = excluded.updated_at
                """, tenantId, now, now);
    }

    private LocalDateTime loadLastSuccessAt(Long tenantId) {
        if (tenantId == null || tenantId <= 0) {
            return null;
        }
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT last_success_at FROM tenant_crawl_cooldown WHERE tenant_id = ? LIMIT 1",
                tenantId
        );
        if (rows.isEmpty()) {
            return null;
        }
        Object raw = rows.get(0).get("last_success_at");
        return parseTime(raw == null ? "" : String.valueOf(raw));
    }

    private LocalDateTime parseTime(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return LocalDateTime.parse(value.trim(), TS);
        } catch (Exception ignored) {
            return null;
        }
    }

    private String now() {
        return LocalDateTime.now().format(TS);
    }
}
