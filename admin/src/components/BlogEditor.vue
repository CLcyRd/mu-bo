<template>
  <div class="blog-editor" v-loading="loading">
    <el-form ref="formRef" :model="formData" :rules="rules" label-position="top">
      <el-form-item label="资讯标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="请输入资讯标题"
          maxlength="100"
          show-word-limit
          clearable
        />
      </el-form-item>

      <el-form-item label="资讯封面">
        <div class="cover-field">
          <img :src="formData.cover" class="cover-preview" alt="资讯封面" @error="handleCoverError" />
          <div class="cover-actions">
            <el-upload
              accept="image/*"
              :auto-upload="false"
              :show-file-list="false"
              :disabled="coverUploading"
              :on-change="handleCoverChange"
            >
              <el-button type="primary" plain :loading="coverUploading">选择封面</el-button>
            </el-upload>
            <el-button :disabled="coverUploading" @click="resetCover">恢复默认封面</el-button>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="资讯正文" prop="content">
        <div class="editor-container">
          <Toolbar
            style="border-bottom: 1px solid #ccc"
            :editor="editorRef"
            :defaultConfig="toolbarConfig"
            :mode="mode === 'edit' ? 'default' : 'default'" 
          />
          <Editor
            style="height: 500px; overflow-y: hidden;"
            v-model="formData.content"
            :defaultConfig="editorConfig"
            mode="default"
            @onCreated="handleCreated"
            @onChange="handleChange"
          />
        </div>
      </el-form-item>

      <div class="form-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="loading">保存草稿</el-button>
        <el-button type="success" @click="handlePublish" :loading="loading">发布资讯</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
/**
 * BlogEditor.vue - 资讯博客编辑器组件
 * 
 * 功能描述：
 * - 支持资讯标题输入（最大100字符，必填）
 * - 集成 WangEditor 富文本编辑器（支持格式化、图片上传、链接等）
 * - 支持新增/编辑模式切换
 * - 表单校验（标题和内容不能为空）
 * - 响应式设计，适配移动端
 * - 提供保存、发布、取消事件回调
 * 
 * Props:
 * - mode: 'create' | 'edit' (默认 'create') - 编辑器模式
 * - initialData: { title: string, content: string } (默认 { title: '', content: '' }) - 初始数据，用于编辑模式回显
 * - loading: boolean (默认 false) - 加载状态，用于控制保存/发布按钮和遮罩层
 * 
 * Emits:
 * - save: (data: { title: string, content: string }) => void - 点击保存草稿时触发
 * - publish: (data: { title: string, content: string }) => void - 点击发布资讯时触发
 * - cancel: () => void - 点击取消时触发
 * - error: (message: string) => void - 编辑器内部错误时触发
 * 
 * Usage Example:
 * <BlogEditor 
 *   mode="create" 
 *   :loading="isSubmitting"
 *   @save="handleSaveDraft" 
 *   @publish="handlePublishPost" 
 *   @cancel="goBack"
 * />
 */

import '@wangeditor/editor/dist/css/style.css'
import { onBeforeUnmount, ref, shallowRef, reactive, watch } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { ElMessage, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import api from '../api'
import defaultCover from '../assets/default_cover.png'

// 定义组件 Props
interface Props {
  mode?: 'create' | 'edit'
  initialData?: {
    title: string
    content: string
    cover?: string
  }
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
  initialData: () => ({ title: '', content: '', cover: defaultCover }),
  loading: false
})

// 定义组件 Emits
const emit = defineEmits<{
  (e: 'save', data: { title: string; content: string; cover: string }): void
  (e: 'publish', data: { title: string; content: string; cover: string }): void
  (e: 'cancel'): void
  (e: 'error', message: string): void
}>()

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef<IDomEditor>()

// 表单数据
const formData = reactive({
  title: '',
  content: '',
  cover: defaultCover
})
const coverUploading = ref(false)

// 表单引用
const formRef = ref<FormInstance>()

// 表单校验规则
const rules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入资讯标题', trigger: 'blur' },
    { min: 1, max: 100, message: '标题长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入资讯正文', trigger: 'blur' },
    { 
      validator: (rule: any, value: string, callback: any) => {
        // 自定义校验：检查编辑器内容是否为空（去除HTML标签后的纯文本）
        if (editorRef.value && editorRef.value.isEmpty()) {
          callback(new Error('资讯正文不能为空'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
})

// 工具栏配置
const toolbarConfig: Partial<IToolbarConfig> = {
  // 可以根据需要排除某些菜单
  // excludeKeys: []
}

// 编辑器配置
const editorConfig: Partial<IEditorConfig> = {
  placeholder: '请输入资讯正文内容...',
  MENU_CONF: {
    uploadImage: {
      // 图片上传配置
      // server: '/api/upload', // 后端上传接口地址
      // fieldName: 'file',
      // maxFileSize: 5 * 1024 * 1024, // 5M
      // allowedFileTypes: ['image/*'],
      // meta: { token: 'xxx' }, // 携带 token
      
      // 自定义上传（演示用）
      async customUpload(file: File, insertFn: any) {
        const formData = new FormData()
        formData.append('file', file)
        const response = await api.post('/consultations/upload-image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        if (response.data?.code !== 0 || !response.data?.data?.url) {
          throw new Error(response.data?.message || '图片上传失败')
        }
        insertFn(response.data.data.url, file.name, response.data.data.url)
        ElMessage.success('图片上传成功')
      }
    }
  }
}

// 监听 initialData 变化，用于编辑模式回显
watch(() => props.initialData, (newVal) => {
  if (newVal) {
    formData.title = newVal.title
    formData.content = newVal.content
    if (!newVal.cover || newVal.cover.startsWith('blob:') || newVal.cover.startsWith('file:')) {
      formData.cover = defaultCover
      return
    }
    formData.cover = newVal.cover
  }
}, { immediate: true, deep: true })

// 组件销毁时，及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

const handleCreated = (editor: any) => {
  editorRef.value = editor // 记录 editor 实例
}

const handleChange = (editor: any) => {
  // 手动触发校验，因为 v-model 有时不会立即触发 el-form 的 change
  if (!editor.isEmpty()) {
    formRef.value?.clearValidate('content')
  }
}

const handleCoverChange = async (file: UploadFile) => {
  const raw = file.raw
  if (!raw) return
  if (!raw.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  coverUploading.value = true
  try {
    const uploadFormData = new FormData()
    uploadFormData.append('file', raw)
    const response = await api.post('/consultations/upload-image', uploadFormData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    if (response.data?.code !== 0 || !response.data?.data?.url) {
      throw new Error(response.data?.message || '封面上传失败')
    }
    formData.cover = response.data.data.url
    ElMessage.success('封面上传成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '封面上传失败'
    ElMessage.error(message)
    emit('error', message)
  } finally {
    coverUploading.value = false
  }
}

const resetCover = () => {
  formData.cover = defaultCover
}

const handleCoverError = () => {
  formData.cover = defaultCover
}

const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    emit('save', { ...formData })
  } catch (error) {
    ElMessage.warning('请完善表单信息')
  }
}

const handlePublish = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    if (editorRef.value?.isEmpty()) {
      ElMessage.warning('正文内容不能为空')
      return
    }
    emit('publish', { ...formData })
  } catch (error) {
    ElMessage.warning('请完善表单信息')
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.blog-editor {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  z-index: 100; /* 防止被其他元素遮挡 */
}

.cover-field {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.cover-preview {
  width: 300px;
  height: 168px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #dcdfe6;
  background: #f5f7fa;
}

.cover-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .blog-editor {
    padding: 16px;
  }
  
  .form-actions {
    flex-direction: column-reverse; /* 按钮竖排，保存发布在上方更合理，或者保持原样 */
  }
  
  .form-actions button {
    width: 100%;
    margin-left: 0 !important;
    margin-bottom: 8px;
  }

  .cover-field {
    flex-direction: column;
    width: 100%;
  }

  .cover-preview {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 9;
  }
}
</style>
