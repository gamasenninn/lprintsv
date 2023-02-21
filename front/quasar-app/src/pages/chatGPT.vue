
<script setup lang="ts">
  import { ref } from 'vue'
  import axios from 'axios'

  const textToSpeech = new SpeechSynthesisUtterance();
  textToSpeech.lang = 'ja-JP'

  const message = ref('')
  const answer = ref('')
  message.value = ''
  const YOUR_API_KEY = process.env.OPENAI_API_KEY
  const sendToChatGPT = async () => {
      const response = await axios.post(
          'https://api.openai.com/v1/completions',
          {
              model: 'text-davinci-003',
              prompt: message.value,
              max_tokens: 1024,
              temperature: 0.5,
          },
          {
          headers: {
              Authorization: `Bearer ${YOUR_API_KEY}`,
              'Content-Type': 'application/json',
          },
          }
      );

      const chatGPTResponse = response.data.choices[0].text;
      console.log(chatGPTResponse)
      answer.value = chatGPTResponse     
      // chatGPTResponse を音声出力する処理を書く
      textToSpeech.text = chatGPTResponse
      speechSynthesis.speak(textToSpeech);
  }
  const startSpeechRecognition=  ()=> {
      const recognition = new window.webkitSpeechRecognition()
      recognition.lang = 'ja-JP'
      recognition.interimResults = false
      recognition.maxAlternatives = 1

      recognition.onresult = (event:any) => {
        message.value = event.results[0][0].transcript
      }
      recognition.start()
    }
</script>

<template>
  <q-page class="q-pa-md" >
    <h5 class="q-mt-none">Axios Test</h5>
    <div class="q-pa-md" style="max-width: 300px">
      <q-input
        v-model="message"
        type="text"
      />
      <q-icon name="mic" size="2em" class="cursor-pointer" @click="startSpeechRecognition" />
    </div>
    <q-btn color="primary" class="q-pa-md" label="Refresh" @click="sendToChatGPT"/>
    <div class="q-pa-md" >
      <pre>{{ answer }}</pre>
    </div>
  </q-page>
</template>
