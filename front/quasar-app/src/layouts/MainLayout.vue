<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Label Printer server Ver. 0.0.0
        </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label header>
          Applications
        </q-item-label>
        <LocalLink
          v-for="link in localLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
      <q-list>
        <q-item-label header>
          Essential Links
        </q-item-label>
        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>
    <q-page-container>
        <router-view v-slot="{Component}">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import EssentialLink from 'components/EssentialLink.vue';
import LocalLink from 'src/components/LocalLink.vue';

const localLinksList = [
  {
    title: 'Label Print',
    caption: 'check & printing ......',
    icon: 'print',
    link: '/ordersPage'
  },
  {
    title: 'Print Script Editot',
    caption: 'Edit for print script ......',
    icon: 'print',
    link: '/pedit'
  },
  {
    title: 'Github users',
    caption: 'test for axuis  ......',
    icon: 'code',
    link: '/axios2'
  },
  {
    title: 'GPT TEST',
    caption: 'GPT-3 API test  ......',
    icon: 'code',
    link: '/chat'
  },
]

const linksList = [
  {
    title: 'swagger',
    caption: 'API DOCS',
    icon: 'school',
    link: 'http://localhost:8000/docs'
  },
  {
    title: 'tpcl editor',
    caption: 'TPCL script maker',
    icon: 'school',
    link: 'http://localhost:8000/tpcledit'
  },
  {
    title: 'Docs',
    caption: 'quasar.dev',
    icon: 'school',
    link: 'https://quasar.dev'
  },
  {
    title: 'Github',
    caption: 'github.com/quasarframework',
    icon: 'code',
    link: 'https://github.com/quasarframework'
  },
  {
    title: 'Discord Chat Channel',
    caption: 'chat.quasar.dev',
    icon: 'chat',
    link: 'https://chat.quasar.dev'
  },
  {
    title: 'Forum',
    caption: 'forum.quasar.dev',
    icon: 'record_voice_over',
    link: 'https://forum.quasar.dev'
  },
  {
    title: 'Quasar Awesome',
    caption: 'Community Quasar projects',
    icon: 'favorite',
    link: 'https://awesome.quasar.dev'
  }
];

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink,
    LocalLink
  },

  setup () {
    const leftDrawerOpen = ref(false)

    return {
      essentialLinks: linksList,
      localLinks: localLinksList,
      leftDrawerOpen,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value
      }
    }
  }
});
</script>
