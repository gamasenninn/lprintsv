import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: '/axios', component: () => import('pages/AxiosPage.vue') },
      { path: '/axios2', component: () => import('pages/AxiosPage2.vue') },
      { path: '/ordersPage', component: () => import('pages/OrdersPage.vue') },
      { path: '/chat', component: () => import('pages/chatGPT.vue') },
      { path: '/pedit', component: () => import('pages/TestReload.vue') },
      { path: '/test', component: () => import('pages/TestReload.vue') },
      { path: '/logViewer', component: () => import('pages/LogViewer.vue') },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
