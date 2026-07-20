package com.crosshub.amazon.repository;

import com.crosshub.amazon.entity.AmazonProductVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AmazonProductVersionRepository extends JpaRepository<AmazonProductVersion, String> {
    List<AmazonProductVersion> findBySyncVersionIdOrderByRankNoAsc(String syncVersionId);
}
