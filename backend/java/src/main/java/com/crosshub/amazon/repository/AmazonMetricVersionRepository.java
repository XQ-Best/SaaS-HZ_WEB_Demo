package com.crosshub.amazon.repository;

import com.crosshub.amazon.entity.AmazonMetricVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AmazonMetricVersionRepository extends JpaRepository<AmazonMetricVersion, String> {
    List<AmazonMetricVersion> findBySyncVersionIdOrderByMetricKeyAsc(String syncVersionId);
}
