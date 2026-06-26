package com.crosshub.temu.web;

import com.crosshub.temu.service.WarehouseSiteService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/warehouse")
public class WarehouseSiteController {
    private final WarehouseSiteService siteService;

    public WarehouseSiteController(WarehouseSiteService siteService) {
        this.siteService = siteService;
    }

    @GetMapping("/sites")
    public Map<String, Object> listSites(@RequestParam(value = "activeOnly", defaultValue = "false") boolean activeOnly) {
        return Map.of("code", 0, "data", siteService.listSites(activeOnly));
    }

    @PostMapping("/sites")
    public Map<String, Object> createSite(@RequestBody SiteRequest request) {
        return Map.of("code", 0, "data", siteService.createSite(toPayload(request)));
    }

    @PutMapping("/sites/{id}")
    public Map<String, Object> updateSite(@PathVariable("id") String id, @RequestBody SiteRequest request) {
        return Map.of("code", 0, "data", siteService.updateSite(id, toPayload(request)));
    }

    @PatchMapping("/sites/{id}/status")
    public Map<String, Object> updateStatus(@PathVariable("id") String id, @RequestBody StatusRequest request) {
        return Map.of("code", 0, "data", siteService.updateStatus(id, request.status()));
    }

    @DeleteMapping("/sites/{id}")
    public Map<String, Object> deleteSite(@PathVariable("id") String id) {
        siteService.deleteSite(id);
        return Map.of("code", 0, "data", true);
    }

    private WarehouseSiteService.SitePayload toPayload(SiteRequest request) {
        return new WarehouseSiteService.SitePayload(
                request.name(),
                request.code(),
                request.address(),
                request.status(),
                request.sortOrder()
        );
    }

    public record SiteRequest(
            String name,
            String code,
            String address,
            Boolean status,
            Integer sortOrder
    ) {}

    public record StatusRequest(boolean status) {}
}
