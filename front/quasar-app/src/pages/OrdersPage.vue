
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import axios from 'axios'
  import {get_config} from './print_conf.js'

  const config = get_config()
  console.log('config',config)

  const printData = ref([])

  const skipText = ref('0')
  const limitText = ref('100')
  const gteText = ref('1')
  const scodeText = ref('')
  const placeText = ref('')

  const statusSyncDb = ref(false)
  const statusSyncLocation = ref(false)
  const DEBUG = false
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
  const showSyncDbMessage = ref(false)
  const showSyncLocationMessage = ref(false)
  //const PRINT_SERVER_URL:string|undefined = process.env.PRINT_SERVER_URL
  //const QR_URL:string|undefined = process.env.QR_URL
  const PRINT_SERVER_URL:string|undefined = 'http://ymain2:8000'
  const QR_URL:string|undefined = 'https://hikousen-rs.com/close'

  const printList = async ()=>{
    //const PRINT_SERVER_URL:string|undefined = process.env.PRINT_SERVER_URL
    if (PRINT_SERVER_URL === undefined) {
      console.warn('PRINT_SERVER_URL is not defined')
      return
    }
    const response = await axios.get(
      `${PRINT_SERVER_URL}/orders?skip=${skipText.value}&limit=${limitText.value}&gte=${gteText.value}&scode=${scodeText.value}&place=${placeText.value}`)
    printData.value = response.data
  }

  onMounted(() => {
    printList()
    console.log('ENV:',PRINT_SERVER_URL,QR_URL)
  })

  const columns=[
        {name: 'scode',label:'仕切No' ,field:'scode',sortable:true},
        {name: 'title',label:'タイトル' ,field:'title'},
        {name: 'receiptDate',label:'日付' ,field:'receiptDate'},
        {name: 'stockQty',label:'在庫数' ,field:'stockQty'},
        {name: 'person',label:'担当' ,field:'person'},
        {name: 'ownwer',label:'発行者' ,field: row=>row.owner.name},
        {name: 'place',label:'場所' ,field: 'place',sortable:true},
        {name: 'status',label:'状態' ,field: 'status',sortable:true},
      ]

  const printLabel = async () =>{
    //const newConfig = {...config }  
    const newConfig = {
        ...config,
        data: config.data.map(item => ({...item})) // Deep copy of config.data
     };  
    if(selected.value.length > 0){
      selected.value.forEach( async (selData,i) =>{
        selData.status = 'printed'
        console.log('selected:', selData.scode,selData.id,selData.title)
        console.log('selData:', selData)
        if(i >= newConfig.data.length) {
          newConfig.data.push({});
        }

        newConfig.data[i].scode = selData.scode 
        newConfig.data[i].title = selData.title
        newConfig.data[i].datePerson = `${selData.receiptDate} ${selData.person}`
        newConfig.data[i].qrData = `${QR_URL}?skey=${selData.scode}`
        console.log('QR:',newConfig.data[i].qrData)

      });
      
      const put_url = `${PRINT_SERVER_URL}/tpclmaker`
      const response = await axios.post(put_url, newConfig)
      console.log(response)
      // Status 更新
      if (response.status == 200){
        selected.value.forEach( async selData =>{
          const put_url2 = `${PRINT_SERVER_URL}/orders/${selData.id}`
          const response2 = await axios.put(put_url2, {status:selData.status})
          console.log(response2)
        })
      }
      
    }

    showMessage.value = false
  }

  const syncDataBase = async () =>{
    statusSyncDb.value = true
    console.log('Sync DB start......')
    const put_url = `${PRINT_SERVER_URL}/convert/fromDB`
    const response = await axios.post(put_url,'test')
    statusSyncDb.value = false
    showSyncDbMessage.value = false

  }
  const syncLocation = async () =>{
    statusSyncLocation.value = true
    console.log('Sync Location info start......')
    const put_url = `${PRINT_SERVER_URL}/convert/update_location`
    const response = await axios.post(put_url,'test')
    statusSyncLocation.value = false
    showSyncLocationMessage.value = false

  }

</script>

<template>
  <q-page class="q-pa-md" >
    <h5 class="q-mt-none">Label Print </h5>
    <div class="q-pa-md">
      <q-btn color="primary" icon="replay" label="Refresh" @click="printList"/>
      <div class="row">
        <div class="col">
          <q-input v-model="skipText" label="Skip Value(Offset)" />
        </div>
        <div class="col">
          <q-input v-model="limitText" label="limit Value(number)" />
        </div>
        <div class="col">
          <q-input v-model="gteText" label="stock qty >=" />
        </div>
        <div class="col">
          <q-input v-model="scodeText" label="scode(contain)"  stack-label/>
        </div>
        <div class="col">
          <q-input v-model="placeText" label="place(contain)"  stack-label/>
        </div>
        <div class="col-2">
        </div>
      </div>
    </div>
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
    <q-btn color="primary" class = "q-mt-md" icon="print" label="Print Label" @click="showMessage=true"/>
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
    <q-btn color="primary" class = "q-mt-md q-ml-md" icon="sync" label="Sync DataBase" @click="showSyncDbMessage=true"/>
    <q-spinner-audio v-if="statusSyncDb" class = "q-mt-md" color="primary" size="2em" />
    <q-dialog v-model="showSyncDbMessage">
      <q-card>
        <q-card-section>
          <div class="text-h6">Alert</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          データベースを同期します。
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary"  @click="syncDataBase" />
        </q-card-actions>
      </q-card>
    </q-dialog> 
    <q-btn color="primary" class = "q-mt-md q-ml-md" icon="sync" label="Sync Location" @click="showSyncLocationMessage=true"/>
    <q-spinner-audio v-if="statusSyncLocation" class = "q-mt-md" color="primary" size="2em" />
    <q-dialog v-model="showSyncLocationMessage">
      <q-card>
        <q-card-section>
          <div class="text-h6">Alert</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          位置情報を更新します。
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary"  @click="syncLocation" />
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
