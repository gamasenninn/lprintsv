<script setup lang="ts">
  import { ref,onMounted } from 'vue'
  import {Ace} from 'ace-builds'
  import { VAceEditor } from 'vue3-ace-editor'
  import 'ace-builds/src-noconflict/mode-json'
  import 'ace-builds/src-noconflict/theme-monokai'

  const content = ref('hello ace')
  const editor = ref<Ace.Editor>()

  const editorInit = (e: Ace.Editor)=>{
    editor.value = e
  }

  onMounted(() => {
    console.log('------')
  })

</script>

<template>
  <q-page class="q-pa-lg">
    <h5 class="q-mt-none">Print Script Editor</h5>
    <q-btn color="primary" label="Github list" class="q-mb-md"/>
    <v-ace-editor
    v-model:value="content"
    @init="editorInit"
    lang="json"
    mode="json"
    theme="monokai"
    style="height: 300px" />
  </q-page>
</template>
  
