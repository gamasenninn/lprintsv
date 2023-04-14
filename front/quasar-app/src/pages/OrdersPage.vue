
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import axios from 'axios'
  import {get_config} from './print_conf.js'

  const config = get_config()
  console.log("config",config)
  const printData = ref([])
  const DEBUG = true
  interface Selected{
    scode: string,
    status: string,
    id: number,
    title: string,
    receiptDate: Date,
    person: string
    //その必要ならば型定義を増やしていくこと
  }
  const selected = ref<Selected[]>([])
  const showMessage = ref(false)

  const printList = async ()=>{
    const PRINT_SERVER_URL:string|undefined = process.env.PRINT_SERVER_URL
    if (PRINT_SERVER_URL === undefined) {
      console.warn('PRINT_SERVER_URL is not defined')
      return
    }
    const response = await axios.get(PRINT_SERVER_URL)
    printData.value = response.data
  }

  onMounted(() => {
    printList()
  })

  const columns=[
        {name: 'scode',label:'仕切No' ,field:'scode',sortable:true},
        {name: 'title',label:'タイトル' ,field:'title'},
        {name: 'receiptDate',label:'日付' ,field:'receiptDate'},
        {name: 'person',label:'担当' ,field:'person'},
        {name: 'ownwer',label:'発行者' ,field: row=>row.owner.name},
        {name: 'status',label:'状態' ,field: 'status'},
      ]

  const newConfig = {...config }    
  const printLabel = async () =>{
    const PRINT_SERVER_URL:string|undefined = process.env.PRINT_SERVER_URL
    //alert('now printng.......')
    if(selected.value.length > 0){
      selected.value.forEach( async selData =>{
        selData.status = 'printed'
        console.log('selected:', selData.scode,selData.id,selData.title)
        console.log('selData:', selData)
        //const put_url = `${PRINT_SERVER_URL}${selData.id}`
        //console.log('url:',put_url)
        //const response = await axios.put(put_url,selData)

        newConfig.data[0].scode = selData.scode 
        newConfig.data[0].title = selData.title
        newConfig.data[0].datePerson = `${selData.receiptDate} ${selData.person}`
        newConfig.data[0].qrData = 'https://www.google.com/search?q=%E9%A3%9B%E8%A1%8C%E8%88%B9'

        const put_url = 'http://localhost:8000/tpclmaker'
        const response = await axios.post(put_url, newConfig)
        console.log(response)
        const put_url2 = `http://localhost:8000/orders/${selData.id}`
        const response2 = await axios.put(put_url2, {status:selData.status})
        console.log(response2)

      });
    }
    showMessage.value = false
  }

</script>

<template>
  <q-page class="q-pa-md" >
    <h5 class="q-mt-none">Label Print </h5>
    <q-btn color="primary" label="Refresh" @click="printList"/>
    <q-table 
      title="Lable List" 
      :rows="printData" 
      :columns="columns"
      row-key="scode" 
      no-data-label="データがありません"
      class="q-mt-md"
      selection="multiple"
      v-model:selected="selected"
    >
    </q-table>
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
    <div v-if="DEBUG">
      <div>
        {{ selected }}
      </div>
      <ul class="q-mt-md">
        <li v-for="data in printData" :key="data.scode">{{ data }}</li>
      </ul>
    </div>

  </q-page>
</template>
