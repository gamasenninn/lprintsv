
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import axios from 'axios'

  const gitData = ref([])
  const DEBUG = false

  const getGithub = async ()=>{
    const response = await axios.get('http://localhost:8000/orders/')
    gitData.value = response.data
  }
  onMounted(() => {
    getGithub()
  })
</script>

<template>
  <q-page class="q-pa-md" >
    <h5 class="q-mt-none">Axios Test</h5>
    <q-btn color="primary" label="Refresh" @click="getGithub"/>
    <q-table 
      title="Lable List" 
      :rows="gitData" 
      :columns=" [
        {name: 'scode',label:'仕切No' ,field:'scode',sortable:true},
        {name: 'title',label:'タイトル' ,field:'title'},
        {name: 'receiptDate',label:'日付' ,field:'receiptDate'},
        {name: 'person',label:'担当' ,field:'person'},
        {name: 'ownwer',label:'発行者' ,field:'owner'},
      ]"
      row-key="scode" 
      no-data-label="データがありません"
      class="q-mt-md"
    >
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="scode" :props="props">{{ props.row.scode }}</q-td>
        <q-td key="title" :props="props">{{ props.row.title }}</q-td>
        <q-td key="receiptDate" :props="props">{{ props.row.receiptDate }}</q-td>
        <q-td key="person" :props="props">{{ props.row.person }}</q-td>
        <q-td key="ownwer" :props="props">{{ props.row.owner.name }}</q-td>
      </q-tr>
    </template>
    </q-table>
    <div>
      <ul v-if="DEBUG" class="q-mt-md">
        <li v-for="data in gitData" :key="data.scode">{{ data }}</li>
      </ul>
    </div>
  </q-page> 
</template>
