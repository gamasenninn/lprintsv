
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import axios from 'axios'

  const PRINT_SERVER_URL:string|undefined = process.env.PRINT_SERVER_URL

  const logData = ref([])
  const getLog = async (logType:string)=>{
    const response = await axios.get(PRINT_SERVER_URL+'/'+logType)
    console.log(response.data)

    logData.value = response.data
    console.log(logData.value)
  }

  //onMounted(() => {
  //  getLog()
  //})
</script>

<template>
  <q-page class="q-pa-lg">
    <h5 class="q-mt-none">Log Viewer</h5>
    <q-btn class="q-mr-md" color="primary" label="send log" @click="getLog('slog')"/>
    <q-btn class="q-mr-md" color="primary" label="recv log" @click="getLog('rlog')"/>
    <q-space class="q-mb-md"/>
    <div>
    <ul class="custom-ul">
      <li v-for="(item, index) in logData" :key="index">{{ item }}</li>
    </ul>
  </div>
</q-page> 
</template>
  
<style>
.custom-ul li {
  margin-bottom: 4px; /* 任意の値を設定 */
  list-style-type: none;
  padding-left: 1em; /* リストアイテムの左側の余白を調整 */
  text-indent: -3em; /* リストアイテムのテキストを左にずらす */
}
</style>
