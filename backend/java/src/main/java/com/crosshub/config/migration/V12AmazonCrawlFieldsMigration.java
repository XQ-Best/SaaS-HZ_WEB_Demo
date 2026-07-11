package com.crosshub.config.migration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@Order(12)
public class V12AmazonCrawlFieldsMigration {
    private static final Logger log = LoggerFactory.getLogger(V12AmazonCrawlFieldsMigration.class);

    private final JdbcTemplate jdbc;

    public V12AmazonCrawlFieldsMigration(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void migrate() {
        try {
            jdbc.execute("ALTER TABLE amazon_product_snapshot ADD COLUMN tacos REAL NOT NULL DEFAULT 0");
        } catch (Exception ignored) {
            // column may already exist
        }
        try {
            jdbc.execute("ALTER TABLE amazon_product_snapshot ADD COLUMN conversion_rate REAL NOT NULL DEFAULT 0");
        } catch (Exception ignored) {
            // column may already exist
        }
        try {
            jdbc.execute("ALTER TABLE amazon_product_snapshot ADD COLUMN period_days INTEGER NOT NULL DEFAULT 30");
        } catch (Exception ignored) {
            // column may already exist
        }
        try {
            jdbc.execute("ALTER TABLE platform_account ADD COLUMN amazon_merchant_id TEXT NOT NULL DEFAULT ''");
        } catch (Exception ignored) {
            // column may already exist
        }
        log.info("V12AmazonCrawlFieldsMigration applied");
    }
}
