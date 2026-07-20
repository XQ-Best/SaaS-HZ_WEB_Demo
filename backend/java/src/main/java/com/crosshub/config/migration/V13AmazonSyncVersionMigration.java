package com.crosshub.config.migration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@Order(13)
public class V13AmazonSyncVersionMigration {
    private static final Logger log = LoggerFactory.getLogger(V13AmazonSyncVersionMigration.class);

    private final JdbcTemplate jdbc;

    public V13AmazonSyncVersionMigration(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void migrate() {
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS amazon_sync_version (
                  id TEXT PRIMARY KEY,
                  sync_job_id TEXT NOT NULL,
                  tenant_id INTEGER NOT NULL,
                  platform_account_id TEXT NOT NULL,
                  scope TEXT NOT NULL,
                  status TEXT NOT NULL DEFAULT 'success',
                  synced_at TEXT NOT NULL,
                  product_count INTEGER NOT NULL DEFAULT 0,
                  metric_count INTEGER NOT NULL DEFAULT 0,
                  item_count INTEGER NOT NULL DEFAULT 0,
                  result_summary TEXT NOT NULL DEFAULT '{}',
                  created_at TEXT NOT NULL
                )
                """);
        jdbc.execute("""
                CREATE INDEX IF NOT EXISTS idx_amazon_sync_version_lookup
                ON amazon_sync_version (tenant_id, platform_account_id, synced_at DESC)
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS amazon_product_version (
                  id TEXT PRIMARY KEY,
                  sync_version_id TEXT NOT NULL,
                  tenant_id INTEGER NOT NULL,
                  platform_account_id TEXT NOT NULL,
                  asin TEXT NOT NULL,
                  sku TEXT NOT NULL DEFAULT '',
                  product_name TEXT NOT NULL DEFAULT '',
                  orders_30d INTEGER NOT NULL DEFAULT 0,
                  revenue_30d TEXT NOT NULL DEFAULT '',
                  page_views INTEGER NOT NULL DEFAULT 0,
                  inventory INTEGER NOT NULL DEFAULT 0,
                  acos REAL NOT NULL DEFAULT 0,
                  ad_spend_30d TEXT NOT NULL DEFAULT '',
                  tacos REAL NOT NULL DEFAULT 0,
                  conversion_rate REAL NOT NULL DEFAULT 0,
                  period_days INTEGER NOT NULL DEFAULT 30,
                  rank_no INTEGER NOT NULL DEFAULT 0,
                  currency TEXT NOT NULL DEFAULT 'USD',
                  synced_at TEXT NOT NULL,
                  UNIQUE (sync_version_id, asin)
                )
                """);
        jdbc.execute("""
                CREATE INDEX IF NOT EXISTS idx_amazon_product_version_lookup
                ON amazon_product_version (sync_version_id, rank_no)
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS amazon_metric_version (
                  id TEXT PRIMARY KEY,
                  sync_version_id TEXT NOT NULL,
                  tenant_id INTEGER NOT NULL,
                  platform_account_id TEXT NOT NULL,
                  metric_key TEXT NOT NULL,
                  metric_label TEXT NOT NULL DEFAULT '',
                  status TEXT NOT NULL DEFAULT 'normal',
                  value_text TEXT NOT NULL DEFAULT '',
                  threshold_text TEXT NOT NULL DEFAULT '',
                  trend TEXT NOT NULL DEFAULT 'stable',
                  note_text TEXT NOT NULL DEFAULT '',
                  synced_at TEXT NOT NULL,
                  UNIQUE (sync_version_id, metric_key)
                )
                """);
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS amazon_item_version (
                  id TEXT PRIMARY KEY,
                  sync_version_id TEXT NOT NULL,
                  tenant_id INTEGER NOT NULL,
                  platform_account_id TEXT NOT NULL,
                  item_type TEXT NOT NULL,
                  external_key TEXT NOT NULL DEFAULT '',
                  payload_json TEXT NOT NULL DEFAULT '{}',
                  synced_at TEXT NOT NULL,
                  UNIQUE (sync_version_id, item_type, id)
                )
                """);
        jdbc.execute("""
                CREATE INDEX IF NOT EXISTS idx_amazon_item_version_lookup
                ON amazon_item_version (sync_version_id, item_type)
                """);
        log.info("V13AmazonSyncVersionMigration applied");
    }
}
