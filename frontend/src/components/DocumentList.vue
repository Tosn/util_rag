<script setup>
// 已上传文档列表
defineProps({
  documents: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

function sizeLabel(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-empty v-if="!documents.length" description="还没有文档,先上传一份吧" />
    <a-list v-else :bordered="false" size="small">
      <a-list-item v-for="d in documents" :key="d.id">
        <a-list-item-meta :title="d.filename">
          <template #description>
            {{ d.chunk_count }} 个片段 · {{ sizeLabel(d.size) }}
          </template>
        </a-list-item-meta>
      </a-list-item>
    </a-list>
  </a-spin>
</template>
