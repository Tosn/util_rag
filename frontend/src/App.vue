<script setup>
import { computed, onMounted, ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import DocumentUpload from './components/DocumentUpload.vue'
import DocumentList from './components/DocumentList.vue'
import ChatPanel from './components/ChatPanel.vue'
import { listDocuments } from './api/client'

const documents = ref([])
const loadingDocs = ref(false)
const hasDocuments = computed(() => documents.value.length > 0)

async function refreshDocuments() {
  loadingDocs.value = true
  try {
    documents.value = await listDocuments()
  } catch (err) {
    Message.error(err.message || '获取文档列表失败')
  } finally {
    loadingDocs.value = false
  }
}

onMounted(refreshDocuments)
</script>

<template>
  <div class="layout">
    <header class="topbar">
      <span class="logo">📄 AI 文档问答</span>
      <span class="subtitle">上传文档,AI 基于内容回答并标注来源</span>
    </header>
    <div class="body">
      <aside class="sidebar">
        <div class="section-title">上传文档</div>
        <DocumentUpload @uploaded="refreshDocuments" />
        <div class="section-title" style="margin-top: 20px">
          已上传（{{ documents.length }}）
        </div>
        <DocumentList :documents="documents" :loading="loadingDocs" />
      </aside>
      <main class="main">
        <ChatPanel :has-documents="hasDocuments" />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.topbar {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 14px 24px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
}
.logo {
  font-size: 18px;
  font-weight: 600;
}
.subtitle {
  font-size: 13px;
  color: #86909c;
}
.body {
  flex: 1;
  display: flex;
  min-height: 0;
}
.sidebar {
  width: 320px;
  padding: 20px;
  background: #fff;
  border-right: 1px solid #e5e6eb;
  overflow-y: auto;
}
.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #4e5969;
  margin-bottom: 10px;
}
.main {
  flex: 1;
  min-width: 0;
}
</style>
