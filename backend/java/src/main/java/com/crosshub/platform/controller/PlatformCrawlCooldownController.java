package com.crosshub.platform.controller;

import com.crosshub.common.ApiResult;
import com.crosshub.common.TenantCrawlCooldownService;
import com.crosshub.tenant.service.DataScopeService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/platform")
public class PlatformCrawlCooldownController {
    private final DataScopeService dataScopeService;
    private final TenantCrawlCooldownService crawlCooldownService;

    public PlatformCrawlCooldownController(
            DataScopeService dataScopeService,
            TenantCrawlCooldownService crawlCooldownService
    ) {
        this.dataScopeService = dataScopeService;
        this.crawlCooldownService = crawlCooldownService;
    }

    @PostMapping("/crawl-cooldown/touch")
    public Map<String, Object> touch() {
        Long tenantId = dataScopeService.requireTenantId();
        crawlCooldownService.recordSuccess(tenantId);
        return ApiResult.ok(Map.of("recorded", true, "tenant_id", tenantId));
    }
}
