package com.crosshub.common;

public class CrawlCooldownException extends RuntimeException {
    private final long remainingMs;

    public CrawlCooldownException(long remainingMs) {
        super(AppErrorCode.CRAWL_COOLDOWN.getUserMessage());
        this.remainingMs = remainingMs;
    }

    public long getRemainingMs() {
        return remainingMs;
    }
}
