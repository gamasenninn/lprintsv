
<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  //import {VAceEditor} from 'vue3-ace-editor'
  //import 'ace-builds/src-noconflict/mode-json'
  //import 'ace-builds/src-noconflict/theme-monokai'
  //import 'ace-builds/src-min-noconflict/ext-language_tools'
  //import workerJsonUrl from 'ace-builds/src-noconflict/worker-json?url';

  //const VaceEditor = ref([])

  //const content = ref('Hello world')
/*
  const editorInit = ()=>{
    console.log('ace init')
  }

  const editorOptions = {
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
    enableSnippets: true,
    highlightActiveLine: true,
    showPrintMargin: false,
    fontSize: '14px'
  }
*/
  //import ace from 'ace-builds'
  //import 'ace-builds/webpack-resolver'
  //import axios from 'axios'
/*
  const printData = ref([])
  const DEBUG = true
  interface Selected{
    scode: string,
    status: string,
    id: number
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
*/
  //onMounted(() => {

    //var editor = ace.edit("editor");
    ////editor.$blockScrolling = Infinity;
    //editor.setTheme("ace/theme/monokai");
    //editor.setFontSize(14);
    //editor.getSession().setMode("ace/mode/json");
    //editor.getSession().setUseWrapMode(true);
    //editor.getSession().setTabSize(2);

  //})

  /*
  const printLabel = async () =>{
    const PRINT_SERVER_URL:string|undefined = process.env.PRINT_SERVER_URL
    alert("now printng.......")
    if(selected.value.length > 0){
      selected.value.forEach( async selData =>{
        selData.status = "printed"
        console.log('selected:', selData.scode,selData.id)
        const put_url = `${PRINT_SERVER_URL}${selData.id}`
        console.log("url:",put_url)
        const response = await axios.put(put_url,selData)
      });
    }
    showMessage.value = false
  }
  */

</script>

<template>
  <q-page class="q-pa-md" >
    <h5 class="q-mt-none">Print Script Editor BBB</h5>
    <q-btn color="primary" label="Refresh" class="q-mb-md"/>
    <!--
    <v-ace-editor 
        v-model:value="content"
        @init="editorInit"
        lang="json"
        mode="json"
        theme="monokai"
        :options="editorOptions"
        style="height: 300px" />

    -->
  </q-page>
</template>
