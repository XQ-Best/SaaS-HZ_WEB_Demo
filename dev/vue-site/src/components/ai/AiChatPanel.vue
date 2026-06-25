<script setup>
import { computed, ref } from 'vue'
import { AI_EMPLOYEE_PROMPTS, AI_MOCK_REPLIES, AI_QUICK_PROMPTS } from '@/constants/mock'

const props = defineProps({
  scope: { type: String, default: 'boss' },
})

const quickPrompts = computed(() =>
  props.scope === 'employee' ? AI_EMPLOYEE_PROMPTS : AI_QUICK_PROMPTS,
)

const input = ref('')
const loading = ref(false)
const messages = ref([
  {
    role: 'assistant',
    content: props.scope === 'boss'
      ? '你好，我是 CrossHub AI 助手。我可以帮你汇总运营数据、分析预警、生成报告。Demo 模式下使用模拟数据回复。'
      : '你好，我是你的 AI 工作助手。我可以帮你处理 Listing 优化、差评回复草稿、任务优先级建议。',
  },
])

function pickReply(text) {
  if (text.includes('汇总') || text.includes('摘要')) return AI_MOCK_REPLIES.summary
  if (text.includes('库存') || text.includes('补货')) return AI_MOCK_REPLIES.inventory
  if (text.includes('滞销')) return AI_MOCK_REPLIES.slow
  if (text.includes('竞店') || text.includes('上新')) return AI_MOCK_REPLIES.competitor
  if (text.includes('标题') || text.includes('Listing') || text.includes('卖点')) return AI_MOCK_REPLIES.listing
  if (text.includes('亏损')) return AI_MOCK_REPLIES.loss
  return AI_MOCK_REPLIES.default
}

async function sendMessage(text) {
  const content = (text || input.value).trim()
  if (!content || loading.value) return

  messages.value.push({ role: 'user', content })
  input.value = ''
  loading.value = true

  await new Promise((r) => setTimeout(r, 800))

  messages.value.push({ role: 'assistant', content: pickReply(content) })
  loading.value = false
}
</script>

<template>
  <el-card shadow="never" class="chat-card">
    <template #header>
      <div class="chat-header">
        <span>AI 对话</span>
        <el-tag size="small" type="info">Demo · Mock 回复</el-tag>
      </div>
    </template>

    <el-scrollbar height="360px" class="chat-body">
      <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.role">
        <el-tag size="small" :type="msg.role === 'user' ? 'primary' : 'success'" effect="plain">
          {{ msg.role === 'user' ? '你' : 'AI' }}
        </el-tag>
        <p>{{ msg.content }}</p>
      </div>
      <div v-if="loading" class="message assistant">
        <el-tag size="small" type="success" effect="plain">AI</el-tag>
        <el-skeleton :rows="2" animated />
      </div>
    </el-scrollbar>

    <div class="quick-prompts">
      <el-button
        v-for="item in quickPrompts"
        :key="item.label"
        size="small"
        round
        @click="sendMessage(item.prompt)"
      >
        {{ item.label }}
      </el-button>
    </div>

    <div class="chat-input">
      <el-input
        v-model="input"
        type="textarea"
        :rows="2"
        placeholder="输入问题，例如：帮我分析今日 Temu 库存预警"
        @keydown.enter.exact.prevent="sendMessage()"
      />
      <el-button type="primary" :loading="loading" @click="sendMessage()">发送</el-button>
    </div>
  </el-card>
</template>

<style scoped>
.chat-card {
  height: 100%;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-body {
  margin-bottom: 12px;
}

.message {
  margin-bottom: 16px;
}

.message p {
  margin-top: 8px;
  line-height: 1.6;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.chat-input {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: end;
}
</style>
