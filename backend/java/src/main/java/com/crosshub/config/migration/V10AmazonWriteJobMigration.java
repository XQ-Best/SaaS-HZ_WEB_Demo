package com.crosshub.config.migration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@Order(10)
public class V10AmazonWriteJobMigration {
    private static final Logger log = LoggerFactory.getLogger(V10AmazonWriteJobMigration.class);

    private final JdbcTemplate jdbc;

    public V10AmazonWriteJobMigration(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void migrate() {
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS amazon_write_job (
                  id TEXT PRIMARY KEY,
                  tenant_id INTEGER NOT NULL,
                  platform_account_id TEXT NOT NULL,
                  agent_task_id TEXT NOT NULL DEFAULT '',
                  item_id TEXT NOT NULL,
                  action TEXT NOT NULL,
                  status TEXT NOT NULL,
                  request_json TEXT NOT NULL DEFAULT '{}',
                  result_json TEXT NOT NULL DEFAULT '{}',
                  error_code TEXT NOT NULL DEFAULT '',
                  error_message TEXT NOT NULL DEFAULT '',
                  created_at TEXT NOT NULL,
                  finished_at TEXT NOT NULL DEFAULT ''
                )
                """);
        jdbc.execute("""
                CREATE INDEX IF NOT EXISTS idx_amazon_write_job_tenant_status
                ON amazon_write_job (tenant_id, status, created_at DESC)
                """);
        log.info("V10 amazon_write_job schema ready");
    }
}
