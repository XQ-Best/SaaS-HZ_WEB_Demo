<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
import PlatformStorePanel from '@/components/accounts/PlatformStorePanel.vue'

const temuPanel = ref(null)
const aliexpressPanel = ref(null)
const panel1688 = ref(null)
const shopifyPanel = ref(null)
const wordpressPanel = ref(null)
const refreshing = ref(false)

async function refreshAll() {
  refreshing.value = true
  try {
    await Promise.all([
      temuPanel.value?.loadStores?.(),
      aliexpressPanel.value?.loadStores?.(),
      panel1688.value?.loadStores?.(),
      shopifyPanel.value?.loadStores?.(),
      wordpressPanel.value?.loadStores?.(),
    ])
    ElMessage.success('已刷新店铺列表')
  } catch {
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    refreshing.value = false
  }
}
</script>

<template>
  <PageScroll>
    <template #header>
      <PageHeader title="平台账户绑定">
        <template #actions>
          <el-button :loading="refreshing" @click="refreshAll">刷新列表</el-button>
        </template>
      </PageHeader>
    </template>

    <el-divider content-position="left">跨境平台</el-divider>

    <el-row :gutter="16" class="panel-row">
      <el-col :xs="24" :lg="12">
        <PlatformStorePanel
          ref="temuPanel"
          platform="temu"
          label="Temu"
          desc="支持绑定多个 Temu 全托管 / 半托管店铺，请为每个店铺设置便于识别的名称"
          tag-type="warning"
        />
      </el-col>
      <el-col :xs="24" :lg="12">
        <PlatformStorePanel
          ref="aliexpressPanel"
          platform="aliexpress"
          label="AliExpress"
          desc="支持绑定多个速卖通店铺，店铺名称用于系统内区分不同站点或品牌店"
          tag-type="danger"
        />
      </el-col>
    </el-row>

    <el-divider content-position="left">供应链采购</el-divider>
    <el-text type="info" size="small" class="section-desc">
      1688 采购账号用于管理供应商订单、付款与入库跟进，可与 Temu / 速卖通备货需求关联
    </el-text>

    <el-row :gutter="16" class="panel-row">
      <el-col :xs="24" :lg="12">
        <PlatformStorePanel
          ref="panel1688"
          platform="1688"
          label="1688"
          desc="支持绑定多个 1688 采购账号，用于区分主采购号与辅料/备件采购号"
          tag-type="warning"
        />
      </el-col>
    </el-row>

    <section class="dtc-section">
      <el-divider content-position="left">独立站运营</el-divider>
      <el-text type="info" size="small" class="section-desc">
        Shopify 与 WordPress 均属于独立站运营，可在此分别绑定电商店铺与内容站点账号
      </el-text>

      <el-row :gutter="16" class="panel-row">
        <el-col :xs="24" :lg="12">
          <PlatformStorePanel
            ref="shopifyPanel"
            platform="shopify"
            label="Shopify"
            desc="独立站电商店铺，用于同步订单、商品与流量数据（如亿拓户外官网、欧洲站）"
            tag-type="success"
          />
        </el-col>
        <el-col :xs="24" :lg="12">
          <PlatformStorePanel
            ref="wordpressPanel"
            platform="wordpress"
            label="WordPress"
            desc="独立站内容站点，用于博客、品牌页或 WooCommerce 店铺管理"
            tag-type="primary"
          />
        </el-col>
      </el-row>
    </section>
  </PageScroll>
</template>

<style scoped>
.panel-row {
  align-items: stretch;
}

.dtc-section {
  margin-top: 8px;
}

.section-desc {
  display: block;
  margin-bottom: 16px;
}
</style>
