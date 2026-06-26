package com.crosshub.temu.repository;

import com.crosshub.temu.entity.UserWarehouseScope;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserWarehouseScopeRepository extends JpaRepository<UserWarehouseScope, Long> {
    List<UserWarehouseScope> findByTenantIdAndUserId(Long tenantId, Long userId);

    void deleteByTenantIdAndUserId(Long tenantId, Long userId);
}
