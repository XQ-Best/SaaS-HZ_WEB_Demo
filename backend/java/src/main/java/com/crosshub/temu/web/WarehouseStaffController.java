package com.crosshub.temu.web;

import com.crosshub.temu.service.WarehouseStaffService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/warehouse")
public class WarehouseStaffController {
    private final WarehouseStaffService staffService;

    public WarehouseStaffController(WarehouseStaffService staffService) {
        this.staffService = staffService;
    }

    @GetMapping("/members")
    public Map<String, Object> listMembers() {
        return Map.of("code", 0, "data", staffService.listStaff());
    }

    @PostMapping("/members")
    public Map<String, Object> createMember(@RequestBody StaffRequest request) {
        return Map.of("code", 0, "data", staffService.createStaff(toPayload(request)));
    }

    @PutMapping("/members/{id}")
    public Map<String, Object> updateMember(@PathVariable("id") Long id, @RequestBody StaffRequest request) {
        return Map.of("code", 0, "data", staffService.updateStaff(id, toPayload(request)));
    }

    @PatchMapping("/members/{id}/status")
    public Map<String, Object> updateStatus(@PathVariable("id") Long id, @RequestBody StatusRequest request) {
        return Map.of("code", 0, "data", staffService.updateStatus(id, request.status()));
    }

    @DeleteMapping("/members/{id}")
    public Map<String, Object> deleteMember(@PathVariable("id") Long id) {
        staffService.deleteStaff(id);
        return Map.of("code", 0, "data", true);
    }

    private WarehouseStaffService.StaffPayload toPayload(StaffRequest request) {
        return new WarehouseStaffService.StaffPayload(
                request.name(),
                request.account(),
                request.password(),
                request.phone(),
                request.role(),
                request.status(),
                request.warehouseIds()
        );
    }

    public record StaffRequest(
            String name,
            String account,
            String password,
            String phone,
            String role,
            Boolean status,
            java.util.List<String> warehouseIds
    ) {}

    public record StatusRequest(boolean status) {}
}
