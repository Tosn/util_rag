<script setup>
// 展示一条 AI 回答命中的来源片段(📎 来源,可折叠)
defineProps({
  sources: { type: Array, default: () => [] },
})

function locLabel(s) {
  const parts = [s.doc_name || '未知文档']
  if (s.page != null) parts.push(`第 ${s.page} 页`)
  else if (s.chunk_index != null) parts.push(`片段 ${s.chunk_index}`)
  return parts.join(' · ')
}
</script>

<template>
  <a-collapse v-if="sources.length" :bordered="false" class="source-collapse">
    <a-collapse-item :header="`📎 来源（${sources.length}）`" key="src">
      <div v-for="(s, i) in sources" :key="i" class="source-item">
        <div class="source-loc">{{ locLabel(s) }}</div>
        <div class="source-snippet">{{ s.snippet }}</div>
      </div>
    </a-collapse-item>
  </a-collapse>
</template>

<style scoped>
.source-collapse {
  margin-top: 8px;
  background: transparent;
}
.source-item {
  padding: 8px 0;
  border-bottom: 1px dashed #e5e6eb;
}
.source-item:last-child {
  border-bottom: none;
}
.source-loc {
  font-size: 12px;
  color: #86909c;
  margin-bottom: 4px;
}
.source-snippet {
  font-size: 13px;
  color: #4e5969;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
