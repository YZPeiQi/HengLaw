import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomePage.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginPage.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterPage.vue')
    },
    {
      path: '/consultation',
      name: 'consultation',
      component: () => import('@/views/ConsultationPage.vue')
    },
    {
      path: '/case-search',
      name: 'case-search',
      component: () => import('@/views/CaseSearchPage.vue')
    },
    {
      path: '/contract-review',
      name: 'contract-review',
      component: () => import('@/views/ContractReviewPage.vue')
    },
    {
      path: '/document-generate',
      name: 'document-generate',
      component: () => import('@/views/DocumentGeneratePage.vue')
    },
    {
      path: '/template-search',
      name: 'template-search',
      component: () => import('@/views/TemplateSearchPage.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfilePage.vue')
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (!token && to.name !== 'home' && to.name !== 'login' && to.name !== 'register' && to.name !== 'template-search') {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
