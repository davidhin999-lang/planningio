import axios from 'axios'
import { auth } from './firebase'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
})

api.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser
    if (user) {
      try {
        const token = await user.getIdToken()
        config.headers.Authorization = `Bearer ${token}`
      } catch {
        // Token refresh failed — let the request proceed without auth header.
        // The backend will return 401 which the caller handles.
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default api
