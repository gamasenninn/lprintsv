<script setup lang="ts">
  import { ref } from 'vue'
  import axios from 'axios'
  const gitData = ref([])
  const getGithub = async ()=>{
    await axios.get('https://api.github.com/users')
        .then((response) =>{
            gitData.value = response.data
            console.log(gitData.value)
          })
  }
</script>

<template>
    <q-page class="q-pa-lg">
      <h5 class="q-mt-none">Axios Test</h5>
      <q-btn color="primary" label="Github list" @click="getGithub"/>
      <q-table 
        title="Github List" 
        :rows="gitData" 
        :columns=" [
          {name: 'login',label:'ログインID' ,field:'login',sortable:true},
          {name: 'node_id',label:'ノードID' ,field:'node_id'},
          {name: 'repos_url',label:'リポジトリURL' ,field:'repos_url'},
        ]"
        row-key="login" 
        no-data-label="データがありません"
        class="q-mt-md"
      >
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="login" :props="props">{{ props.row.login }}</q-td>
          <q-td key="node_id" :props="props">{{ props.row.node_id }}</q-td>
          <q-td key="repos_url" :props="props">{{ props.row.repos_url }}</q-td>
        </q-tr>
      </template>
      </q-table>
    </q-page> 
  </template>
  
