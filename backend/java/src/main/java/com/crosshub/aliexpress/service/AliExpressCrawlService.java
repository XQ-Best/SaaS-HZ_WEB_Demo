package com.crosshub.aliexpress.service;

import com.crosshub.aliexpress.dto.AliExpressCrawlRequest;
import com.crosshub.aliexpress.entity.AliExpressCrawlJob;

public interface AliExpressCrawlService {
    AliExpressCrawlJob triggerCrawl(AliExpressCrawlRequest request);
    AliExpressCrawlJob triggerViolationSync();
    AliExpressCrawlJob triggerViolationSync(boolean force);
    AliExpressCrawlJob triggerViolationSync(boolean force, boolean recordCooldown);
    AliExpressCrawlJob getJob(String jobId);
}

