<script setup>
import { nextTick, ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import MessageBubble from './MessageBubble.vue'
import { chatStream } from '../api/client'

defineProps({
  hasDocuments: { type: Boolean, default: false },
})

const messages = ref([]) // { role, content, sources, streaming }
const input = ref('')
const sending = ref(false)
const conversationId = ref(null)
const listRef = ref(null)

function scrollToBottom() {
  nextTick(() => {
    const el = listRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function send() {
  const question = input.value.trim()
  if (!question || sending.value) return
  input.value = ''
  sending.value = true

  messages.value.push({ role: 'user', content: question })
  const assistant = { role: 'assistant', content: '', sources: [], streaming: true }
  messages.value.push(assistant)
  scrollToBottom()

  await chatStream(
    { question, conversationId: conversationId.value },
    {
      onMeta: (m) => {
        conversationId.value = m.conversation_id
      },
      onToken: (text) => {
        assistant.content += text
        scrollToBottom()
      },
      onSources: (list) => {
        assistant.sources = list
      },
      onError: (msg) => {
        assistant.streaming = false
        if (!assistant.content) assistant.content = `⚠️ ${msg}`
        Message.error(msg)
      },
      onDone: () => {
        assistant.streaming = false
        scrollToBottom()
      },
    },
  )
  assistant.streaming = false
  sending.value = false
}
</script>

<template>
  <div class="chat">
    <div ref="listRef" class="messages">
      <a-empty
        v-if="!messages.length"
        :description="
          hasDocuments
            ? '开始提问吧,答案会标注来源'
            : '先在左侧上传文档,再来提问'
        "
      />
      <MessageBubble v-for="(m, i) in messages" :key="i" :message="m" />
    </div>
    <div class="composer">
      <a-input
        v-model="input"
        placeholder="基于已上传文档提问…"
        :disabled="sending"
        allow-clear
        @press-enter="send"
      />
      <a-button type="primary" :loading="sending" @click="send">发送</a-button>
    </div>
  </div>
</template>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
.composer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e5e6eb;
  background: #fff;
}
</style>
