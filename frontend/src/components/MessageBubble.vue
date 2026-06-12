<script setup>
import SourceCollapse from './SourceCollapse.vue'

// 一条消息:{ role: 'user'|'assistant', content, sources, streaming }
defineProps({
  message: { type: Object, required: true },
})
</script>

<template>
  <div class="row" :class="message.role">
    <div class="bubble">
      <div class="content">
        <template v-if="message.content">{{ message.content }}</template>
        <span v-else-if="message.streaming" class="typing">思考中…</span>
      </div>
      <span v-if="message.streaming && message.content" class="cursor">▋</span>
      <SourceCollapse
        v-if="message.role === 'assistant' && message.sources && message.sources.length"
        :sources="message.sources"
      />
    </div>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  margin-bottom: 16px;
}
.row.user {
  justify-content: flex-end;
}
.row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.7;
}
.user .bubble {
  background: #165dff;
  color: #fff;
}
.assistant .bubble {
  background: #fff;
  border: 1px solid #e5e6eb;
  color: #1d2129;
}
.content {
  white-space: pre-wrap;
  word-break: break-word;
}
.typing {
  color: #86909c;
}
.cursor {
  color: #165dff;
  animation: blink 1s steps(2) infinite;
}
@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}
</style>
