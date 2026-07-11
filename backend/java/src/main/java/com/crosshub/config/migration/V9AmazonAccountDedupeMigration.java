package com.crosshub.config.migration;

import com.crosshub.amazon.service.AmazonAccountDedupeService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

@Component
@Order(9)
public class V9AmazonAccountDedupeMigration {
    private static final Logger log = LoggerFactory.getLogger(V9AmazonAccountDedupeMigration.class);

    private final AmazonAccountDedupeService dedupeService;

    public V9AmazonAccountDedupeMigration(AmazonAccountDedupeService dedupeService) {
        this.dedupeService = dedupeService;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void migrate() {
        int removed = dedupeService.dedupeAllTenants();
        log.info("V9 Amazon account dedupe completed, removed {} duplicate row(s)", removed);
    }
}
