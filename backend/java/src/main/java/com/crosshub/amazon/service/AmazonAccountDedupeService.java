package com.crosshub.amazon.service;

public interface AmazonAccountDedupeService {
    /** 合并同一租户下 external_shop_id 重复的 Amazon 绑定，返回删除的重复账号数。 */
    int dedupeAllTenants();

    int dedupeTenant(Long tenantId);
}
