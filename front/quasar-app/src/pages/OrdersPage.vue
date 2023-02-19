
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import axios from 'axios'

  const gitData = ref([])
  const DEBUG = false
  const selected = ref([])
  const showMessage = ref(false)

  const getGithub = async ()=>{
    const response = await axios.get('http://localhost:8000/orders/')
    gitData.value = response.data
  }
  onMounted(() => {
    getGithub()
  })

  const columns=[
        {name: 'scode',label:'仕切No' ,field:'scode',sortable:true},
        {name: 'title',label:'タイトル' ,field:'title'},
        {name: 'receiptDate',label:'日付' ,field:'receiptDate'},
        {name: 'person',label:'担当' ,field:'person'},
        {name: 'ownwer',label:'発行者' ,field: row=>row.owner.name},
      ]

  const printLabel = () =>{
    alert("now printng.......")
    showMessage.value = false

  }

</script>

<template>
  <q-page class="q-pa-md" >
    <h5 class="q-mt-none">Axios Test</h5>
    <q-btn color="primary" label="Refresh" @click="getGithub"/>
    <q-table 
      title="Lable List" 
      :rows="gitData" 
      :columns="columns"
      row-key="scode" 
      no-data-label="データがありません"
      class="q-mt-md"
      selection="multiple"
      v-model:selected="selected"
    >
    </q-table>
    <div v-if="DEBUG">
      <div>
        {{ selected }}
      </div>
      <ul class="q-mt-md">
        <li v-for="data in gitData" :key="data.scode">{{ data }}</li>
      </ul>
    </div>
    <q-btn color="primary" class = "q-mt-md" label="Print Label" @click="showMessage=true"/>
    <q-dialog v-model="showMessage">
      <q-card>
        <q-card-section>
          <div class="text-h6">Alert</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          ラベルをプリントします。
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary"  @click="printLabel" />
        </q-card-actions>
      </q-card>
    </q-dialog> 
  </q-page>
</template>
