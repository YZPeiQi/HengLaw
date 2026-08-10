import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const reqUrl = error?.config?.url || ''
    const isTemplateApi = typeof reqUrl === 'string' && reqUrl.startsWith('/template/')

    if (!isTemplateApi && (error.response?.status === 401 || error.response?.status === 403)) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  register: (data: { username: string; password: string; email?: string }) =>
    api.post('/auth/register', data)
}

export const consultationApi = {
  ask: (data: { question: string; category?: string; model?: string }) =>
    api.post('/consultation/ask', data),
  getHistory: () => api.get('/consultation/history')
}

export const caseApi = {
  analyze: (data: { caseName: string; caseType: string; caseDescription: string }) =>
    api.post('/case/analyze', data),
  search: (params: { keyword?: string; caseType?: string; page?: number; size?: number }) =>
    api.get('/case/search', { params }),
  add: (data: any) =>
    api.post('/case/add', data)
}

export const contractApi = {
  upload: (formData: FormData) =>
    api.post('/contract/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  review: (data: { contractName: string; contractType: string; content: string; reviewMode?: string }) =>
    api.post('/contract/review', data),
  list: () => api.get('/contract/list')
}

export const documentApi = {
  generate: (data: { docType: string; title?: string; partyA?: string; partyB?: string; caseDescription?: string; claim?: string }) =>
    api.post('/document/generate', data),
  list: () => api.get('/document/list')
}

export const templateApi = {
  search: (params: { keyword: string; limit?: number }) =>
    api.get('/template/search', { params }),
  prewarm: (data: { ids: string[]; limit?: number }) =>
    api.post('/template/prewarm', data),
  preview: (id: string) => api.get(`/template/preview/${id}`),
  pdfPreviewUrl: (id: string) => `/api/template/pdf/${id}`,
  downloadUrl: (id: string) => `/api/template/download/${id}`
}

export default api
