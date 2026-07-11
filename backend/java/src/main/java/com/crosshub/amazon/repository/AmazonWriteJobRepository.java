package com.crosshub.amazon.repository;

import com.crosshub.amazon.entity.AmazonWriteJob;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface AmazonWriteJobRepository extends JpaRepository<AmazonWriteJob, String> {
    Optional<AmazonWriteJob> findByIdAndTenantId(String id, Long tenantId);

    Optional<AmazonWriteJob> findFirstByAgentTaskId(String agentTaskId);

    List<AmazonWriteJob> findByTenantIdAndPlatformAccountIdAndStatusIn(
            Long tenantId,
            String platformAccountId,
            List<String> statuses
    );
}
