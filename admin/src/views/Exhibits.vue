<template>
  <div>
    <div class="page-header">
      <h2>Exhibits</h2>
      <el-button type="primary" @click="showAddDialog">Add Exhibit</el-button>
    </div>
    
    <el-table :data="exhibits" style="width: 100%">
      <el-table-column prop="id" label="ID" width="50" />
      <el-table-column prop="name" label="Name" />
      <el-table-column prop="category" label="Category" />
      <el-table-column prop="era" label="Era" />
      <el-table-column label="Featured">
        <template #default="scope">
          <el-tag :type="scope.row.is_featured ? 'success' : 'info'">{{ scope.row.is_featured ? 'Yes' : 'No' }}</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="Add Exhibit">
      <el-form :model="form" label-width="100px">
        <el-form-item label="Name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="form.category">
            <el-option label="Documents" value="文献资料" />
            <el-option label="Posters" value="电影海报" />
            <el-option label="Props" value="道具" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea"></el-input>
        </el-form-item>
        <el-form-item label="Era">
          <el-input v-model="form.era"></el-input>
        </el-form-item>
        <el-form-item label="Featured">
          <el-switch v-model="form.is_featured"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitExhibit">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const exhibits = ref([])
const dialogVisible = ref(false)
const form = reactive({
  name: '',
  description: '',
  category: '',
  era: '',
  is_featured: false,
  image_url: ''
})

const fetchExhibits = async () => {
  try {
    const res = await api.get('/exhibits/')
    exhibits.value = res.data.exhibits
  } catch (error) {
    ElMessage.error('Failed to fetch exhibits')
  }
}

const showAddDialog = () => {
  dialogVisible.value = true
}

const submitExhibit = async () => {
  try {
    await api.post('/exhibits/', form)
    ElMessage.success('Exhibit added')
    dialogVisible.value = false
    fetchExhibits()
  } catch (error) {
    ElMessage.error('Failed to add exhibit')
  }
}

onMounted(fetchExhibits)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
