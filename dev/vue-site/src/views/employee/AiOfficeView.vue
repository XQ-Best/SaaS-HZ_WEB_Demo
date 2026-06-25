<script setup>
import AiChatPanel from '@/components/ai/AiChatPanel.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
</script>

<template>
  <PageScroll>
    <template #header>
      <PageHeader
        title="AI 办公助手"
        description="Listing 优化、差评回复、任务优先级 — 员工端个人视角"
      />
    </template>

    <el-row :gutter="16" class="ai-row">
      <el-col :xs="24" :lg="16">
        <AiChatPanel scope="employee" />
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never">
          <template #header>员工 AI 工具（规划）</template>
          <el-space direction="vertical" fill style="width: 100%">
            <el-button plain style="width: 100%">Listing 标题优化</el-button>
            <el-button plain style="width: 100%">差评回复草稿</el-button>
            <el-button plain style="width: 100%">广告关键词建议</el-button>
            <el-button plain style="width: 100%">今日任务优先级</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </PageScroll>
</template>

<style scoped>
.ai-row {
  min-height: 480px;
}
</style>
