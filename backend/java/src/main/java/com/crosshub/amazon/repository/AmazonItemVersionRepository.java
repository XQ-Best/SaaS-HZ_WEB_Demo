package com.crosshub.amazon.repository;

import com.crosshub.amazon.entity.AmazonItemVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;

public interface AmazonItemVersionRepository extends JpaRepository<AmazonItemVersion, String> {
    List<AmazonItemVersion> findBySyncVersionIdAndItemTypeInOrderBySyncedAtDesc(
            String syncVersionId,
            Collection<String> itemTypes
    );
}
