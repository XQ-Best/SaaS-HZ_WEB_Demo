<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
import { fetchAgentNodes, fetchAmazonIntegrationStatus, setupLocalAgent } from '@/api/agentApi'
import { fetchAmazonSpApiStatus } from '@/api/amazonApi'
import {
  downloadCombinedLauncher,
  getLauncherRootHint,
} from '@/utils/agentLauncher'
import { probeLocalZiniao } from '@/utils/ziniaoProbe'
import { probeLocalAgent } from '@/utils/agentProbe'

const loading = ref(false)
const downloading = ref(false)
const agentName = ref('本机助手')
const nodes = ref([])
const integration = ref({})
const spApi = ref({})
const localZiniaoOnline = ref(false)
const localAgentOnline = ref(false)

const agentOnline = computed(
  () => localAgentOnline.value || Boolean(integration.value.agent_online),
)
const ziniaoOnline = computed(() => localZiniaoOnline.value || Boolean(integration.value.ziniao_online))
const allReady = computed(() => agentOnline.value && ziniaoOnline.value)

async function loadAll() {
  loading.value = true
  try {
    const [statusRes, nodesRes, spRes, ziniaoReady, agentReady] = await Promise.all([
      fetchAmazonIntegrationStatus(),
      fetchAgentNodes(),
      fetchAmazonSpApiStatus(),
      probeLocalZiniao(),
      probeLocalAgent(),
    ])
    integration.value = statusRes.data || {}
    nodes.value = nodesRes.data || []
    spApi.value = spRes.data || {}
    localZiniaoOnline.value = ziniaoReady
    localAgentOnline.value = agentReady
  } catch (err) {
    ElMessage.error(err.message || '加载状态失败')
  } finally {
    loading.value = false
  }
}

async function onDownloadLauncher() {
  downloading.value = true
  try {
    const res = await setupLocalAgent(agentName.value.trim() || '本机助手')
    downloadCombinedLauncher(res.data)
    ElMessage.success(
      '已下载「CrossHub-Amazon-Sync-Helper.bat」，请双击运行并保持窗口不要关闭',
    )
    await loadAll()
  } catch (err) {
    ElMessage.error(err.message || '下载同步助手失败')
  } finally {
    downloading.value = false
  }
}

onMounted(loadAll)
</script>

<template>
  <PageScroll>
    <PageHeader
      title="Amazon 同步助手"
      description="用于 Amazon 店铺数据自动同步。下载一个启动文件，双击即可同时启动紫鸟与同步助手。"
    >
      <template #actions>
        <el-button :icon="Refresh" :loading="loading" @click="loadAll">刷新状态</el-button>
      </template>
    </PageHeader>

    <div v-loading="loading" class="agent-page">
      <div class="status-tags">
        <el-tag :type="ziniaoOnline ? 'success' : 'warning'" effect="plain" size="large">
          紫鸟 {{ ziniaoOnline ? '已就绪' : '未就绪' }}
        </el-tag>
        <el-tag :type="agentOnline ? 'success' : 'danger'" effect="plain" size="large">
          同步助手 {{ agentOnline ? '在线' : '离线' }}
        </el-tag>
        <el-tag v-if="allReady" type="success" effect="dark" size="large">可以同步 Amazon 数据</el-tag>
      </div>

      <el-alert
        v-if="allReady"
        type="success"
        :closable="false"
        show-icon
        title="Amazon 同步环境已就绪"
        description="可回到左侧「数据同步」点击重新同步，或在 Amazon 运营页刷新数据。"
      />

      <el-card shadow="never" class="step-card">
        <template #header>
          <span class="step-title">步骤 1：下载并运行同步助手</span>
        </template>
        <ol class="step-list">
          <li>先<strong>完全退出</strong>平时用的紫鸟（含右下角托盘图标）</li>
          <li>点击下方按钮下载启动文件（凭证已自动写入，无需复制 Token）</li>
          <li>双击运行 <code>CrossHub-Amazon-Sync-Helper.bat</code>，脚本会依次启动紫鸟 WebDriver 与同步助手</li>
          <li><strong>保持黑色窗口打开</strong>（关闭即停止同步）</li>
          <li>回到本页点击<strong>刷新状态</strong>，看到「紫鸟 已就绪」与「同步助手 在线」即完成</li>
        </ol>
        <div class="register-row">
          <el-input
            v-model="agentName"
            placeholder="助手名称（可选）"
            style="max-width: 220px"
          />
          <el-button
            type="primary"
            :icon="Download"
            :loading="downloading"
            @click="onDownloadLauncher"
          >
            下载 Amazon 同步助手
          </el-button>
        </div>
        <p class="step-hint">
          若仍显示离线：请<strong>重新下载</strong>启动文件（旧版含中文的文件可能在 Windows 下乱码无法运行），并确认黑色窗口内无报错。
        </p>
        <p class="step-hint">
          若更换电脑或助手失效，可再次点击下载（会自动复用本企业已注册的助手）。
        </p>
      </el-card>

      <el-card shadow="never" class="step-card">
        <template #header>
          <span class="step-title">步骤 2：绑定 Amazon 店铺</span>
        </template>
        <p class="step-lead">
          紫鸟与同步助手均在线后，前往
          <router-link to="/boss/accounts">设置 → 账户绑定</router-link>
          ，使用「从紫鸟导入」绑定 Amazon 店铺。
        </p>
      </el-card>

      <el-collapse class="tech-collapse">
        <el-collapse-item title="IT 参考（运营可忽略）" name="it">
          <p class="step-hint">
            启动文件默认项目路径：{{ getLauncherRootHint() }}。若路径不符，请 IT 在部署时配置
            <code>VITE_AGENT_LAUNCHER_ROOT</code>。
          </p>
          <p class="step-hint">
            合并脚本依次检测/启动紫鸟 WebDriver（<code>16851</code>）与 Agent 健康端口（<code>18765</code>）。
          </p>
        </el-collapse-item>
      </el-collapse>

      <el-card shadow="never" class="card-block">
        <template #header>已注册助手</template>
        <el-table v-if="nodes.length" :data="nodes" stripe size="small">
          <el-table-column prop="name" label="名称" min-width="140" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.online ? 'success' : 'info'" size="small">
                {{ row.online ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_heartbeat_at" label="最近心跳" min-width="160" />
          <el-table-column label="紫鸟" width="90">
            <template #default="{ row }">
              <el-tag :type="row.ziniao_online ? 'success' : 'warning'" size="small">
                {{ row.ziniao_online ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="下载并运行 Amazon 同步助手后，这里会显示记录" :image-size="72" />
      </el-card>

      <el-card shadow="never" class="card-block">
        <template #header>SP-API（规划中）</template>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="阶段">{{ spApi.phase || 'P4' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag type="info" size="small">{{ spApi.enabled ? '已启用' : '未启用' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="说明">{{ spApi.message || '—' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </PageScroll>
</template>

<style scoped>
.agent-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-tags,
.register-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.step-card,
.card-block {
  border-radius: 8px;
}

.step-title {
  font-weight: 600;
}

.step-list {
  margin: 0 0 16px 18px;
  padding: 0;
  line-height: 1.8;
}

.step-lead,
.step-hint {
  margin: 0 0 12px;
  line-height: 1.7;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.tech-collapse {
  border: none;
  background: transparent;
}
</style>
