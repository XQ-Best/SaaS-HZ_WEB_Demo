package com.crosshub.amazon.repository;

import com.crosshub.amazon.entity.AmazonSyncVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface AmazonSyncVersionRepository extends JpaRepository<AmazonSyncVersion, String> {
    Optional<AmazonSyncVersion> findByIdAndTenantId(String id, Long tenantId);

    Optional<AmazonSyncVersion> findBySyncJobId(String syncJobId);

    List<AmazonSyncVersion> findByTenantIdAndPlatformAccountIdInOrderBySyncedAtDesc(
            Long tenantId,
            Collection<String> platformAccountIds
    );
}
