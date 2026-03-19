import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Citation {
  index: number
  source: string
  snippet: string
}

export interface DocumentRef {
  id: string
  content: string
  metadata: {
    source: string
    file_type: string
  }
  score: number
}

export interface RAGResponse {
  query: string
  answer: string
  citations: Citation[]
  documents: DocumentRef[]
  confidence: number
  grounded: boolean
  evidence_note: string
  processing_time: number
}

export interface UploadedFileInfo {
  name: string
  size: number
  file_type: string
  uploaded_at: string
}

export const queryDocuments = async (query: string, signal?: AbortSignal): Promise<RAGResponse> => {
  const response = await api.post<RAGResponse>('/query', {
    query,
    k: 5,
    top_k: 3,
  }, {
    signal,
  })
  return response.data
}

export const uploadFile = async (
  file: File,
  options?: { signal?: AbortSignal; onUploadProgress?: (progressEvent: { loaded: number; total?: number }) => void }
) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    signal: options?.signal,
    onUploadProgress: options?.onUploadProgress,
  })
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export const listUploadedFiles = async (): Promise<UploadedFileInfo[]> => {
  const response = await api.get<UploadedFileInfo[]>('/files')
  return response.data
}

export const deleteUploadedFile = async (filename: string) => {
  const response = await api.delete(`/files/${encodeURIComponent(filename)}`)
  return response.data
}

export const clearUploadedFiles = async () => {
  const response = await api.delete('/files')
  return response.data
}

export const getUploadedFileUrl = (filename: string) => (
  `${API_BASE_URL}/files/${encodeURIComponent(filename)}`
)
