import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: 'http://localhost:3000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('Response Error:', error.response?.status, error.message)
    
    // 统一错误处理
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('未授权，请登录')
          break
        case 403:
          console.error('拒绝访问')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器错误')
          break
        default:
          console.error('请求失败:', error.message)
      }
    }
    
    return Promise.reject(error)
  }
)

// 封装GET请求
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  try {
    const response = await request.get<ApiResponse<T>>(url, config)
    return response.data
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.message || error.message
    }
  }
}

// 封装POST请求
export async function post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  try {
    const response = await request.post<ApiResponse<T>>(url, data, config)
    return response.data
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.message || error.message
    }
  }
}

// 封装PUT请求
export async function put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  try {
    const response = await request.put<ApiResponse<T>>(url, data, config)
    return response.data
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.message || error.message
    }
  }
}

// 封装DELETE请求
export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  try {
    const response = await request.delete<ApiResponse<T>>(url, config)
    return response.data
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.message || error.message
    }
  }
}

export default request