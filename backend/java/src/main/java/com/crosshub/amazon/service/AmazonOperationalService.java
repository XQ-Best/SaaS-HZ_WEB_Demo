package com.crosshub.amazon.service;

import java.util.Map;

public interface AmazonOperationalService {
    Map<String, Object> daily(String storeId, String syncVersionId);
    Map<String, Object> insights(String storeId, String syncVersionId);
    Map<String, Object> syncVersions(String storeId, String scope, int limit);
    Map<String, Object> spApiStatus();
    Map<String, Object> integrationStatus();
}
