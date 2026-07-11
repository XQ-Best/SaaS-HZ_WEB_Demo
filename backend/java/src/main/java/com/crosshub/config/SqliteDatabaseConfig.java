package com.crosshub.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * Java 与 Python 共用 crosshub.db；启用 WAL 与 busy_timeout 避免 SQLITE_BUSY。
 */
@Component
@Order(0)
public class SqliteDatabaseConfig {
    private static final Logger log = LoggerFactory.getLogger(SqliteDatabaseConfig.class);

    private final JdbcTemplate jdbc;

    public SqliteDatabaseConfig(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void configureSqlite() {
        String journalMode = jdbc.queryForObject("PRAGMA journal_mode=WAL", String.class);
        jdbc.execute("PRAGMA busy_timeout=30000");
        jdbc.execute("PRAGMA synchronous=NORMAL");
        log.info("SQLite pragmas applied: journal_mode={}, busy_timeout=30000ms", journalMode);
    }
}
