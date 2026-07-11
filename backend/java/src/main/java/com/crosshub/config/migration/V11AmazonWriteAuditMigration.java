package com.crosshub.config.migration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@Order(11)
public class V11AmazonWriteAuditMigration {
    private static final Logger log = LoggerFactory.getLogger(V11AmazonWriteAuditMigration.class);

    private final JdbcTemplate jdbc;

    public V11AmazonWriteAuditMigration(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void migrate() {
        try {
            jdbc.execute("ALTER TABLE amazon_write_job ADD COLUMN initiated_by_user_id INTEGER");
        } catch (Exception ignored) {
            // column may already exist
        }
        try {
            jdbc.execute("ALTER TABLE amazon_write_job ADD COLUMN initiated_by_name TEXT NOT NULL DEFAULT ''");
        } catch (Exception ignored) {
            // column may already exist
        }

        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS amazon_write_audit (
                  id TEXT PRIMARY KEY,
                  tenant_id INTEGER NOT NULL,
                  write_job_id TEXT NOT NULL,
                  platform_account_id TEXT NOT NULL,
                  item_id TEXT NOT NULL,
                  action TEXT NOT NULL,
                  status TEXT NOT NULL,
                  initiated_by_user_id INTEGER,
                  initiated_by_name TEXT NOT NULL DEFAULT '',
                  request_json TEXT NOT NULL DEFAULT '{}',
                  result_json TEXT NOT NULL DEFAULT '{}',
                  error_code TEXT NOT NULL DEFAULT '',
                  error_message TEXT NOT NULL DEFAULT '',
                  created_at TEXT NOT NULL
                )
                """);
        jdbc.execute("""
                CREATE INDEX IF NOT EXISTS idx_amazon_write_audit_tenant_created
                ON amazon_write_audit (tenant_id, created_at DESC)
                """);
        jdbc.execute("""
                CREATE INDEX IF NOT EXISTS idx_amazon_write_audit_item
                ON amazon_write_audit (tenant_id, item_id, created_at DESC)
                """);
        log.info("V11 amazon_write_audit schema ready");
    }
}
