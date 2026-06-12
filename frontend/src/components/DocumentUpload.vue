<script setup>
import { Message } from '@arco-design/web-vue'
import { uploadDocument } from '../api/client'

const emit = defineEmits(['uploaded'])

// a-upload 自定义请求:走我们带进度的封装
function customRequest(option) {
  const { fileItem, onProgress, onSuccess, onError } = option
  uploadDocument(fileItem.file, (percent) => onProgress(percent / 100))
    .then((doc) => {
      Message.success(`「${doc.filename}」已入库（${doc.chunk_count} 个片段）`)
      onSuccess(doc)
      emit('uploaded')
    })
    .catch((err) => {
      Message.error(err.message || '上传失败')
      onError(err)
    })
  return { abort() {} }
}
</script>

<template>
  <a-upload
    draggable
    :custom-request="customRequest"
    :show-file-list="false"
    accept=".pdf,.txt,.md,.markdown"
    tip="支持 PDF / TXT / Markdown,单文件拖拽上传"
  />
</template>
