
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import axios from 'axios'

  const gitData = ref([])

  const getGithub = async ()=>{
    const response = await axios.get('http://localhost:8000/orders/')
    gitData.value = response.data
    console.log(gitData)
    return gitData
  }
  onMounted(() => {
    getGithub()
  })
</script>

<template>
  <q-page class="q-pa-lg">
    <h5 class="q-mt-none">Axios Test</h5>
    <q-btn color="primary" label="Github list" @click="getGithub"/>
    <q-table 
      title="Github List" 
      :rows="gitData" 
      :columns=" [
        {name: 'scode',label:'仕切No' ,field:'scode',sortable:true},
        {name: 'title',label:'タイトル' ,field:'title'},
      ]"
      row-key="scode" 
      no-data-label="データがありません"
      class="q-mt-md"
    >
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="scode" :props="props">{{ props.row.scode }}</q-td>
        <q-td key="title" :props="props">{{ props.row.title }}</q-td>
      </q-tr>
    </template>
    </q-table>
  </q-page> 
  <div>
    <ul>
      <li v-for="data in gitData" :key="data.scode">{{ data }}</li>
    </ul>
  </div>
</template>
