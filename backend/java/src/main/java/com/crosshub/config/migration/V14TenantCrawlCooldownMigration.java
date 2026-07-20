package com.crosshub.config.migration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@Order(14)
public class V14TenantCrawlCooldownMigration {
    private static final Logger log = LoggerFactory.getLogger(V14TenantCrawlCooldownMigration.class);

    private final JdbcTemplate jdbc;

    public V14TenantCrawlCooldownMigration(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void migrate() {
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS tenant_crawl_cooldown (
                  tenant_id INTEGER PRIMARY KEY,
                  last_success_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                )
                """);
        log.info("V14TenantCrawlCooldownMigration applied");
    }
}
