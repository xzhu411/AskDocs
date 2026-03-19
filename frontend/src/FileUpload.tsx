import { useState, useRef, FC } from 'react'
import axios from 'axios'
import { Upload, Loader } from 'lucide-react'
import { uploadFile } from './api'
import { Card } from './components'

interface FileUploadProps {
  onSuccess: (message: string, filename: string) => void
  onError: (message: string) => void
  onProgress?: (percent: number, label: string) => void
}

export const FileUpload: FC<FileUploadProps> = ({ onSuccess, onError, onProgress }) => {
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)
    try {
      onProgress?.(5, 'Preparing upload...')
      const response = await uploadFile(file, {
        onUploadProgress: (event) => {
          if (!event.total) {
            onProgress?.(35, 'Uploading file...')
            return
          }

          const uploadPercent = Math.round((event.loaded / event.total) * 70)
          onProgress?.(Math.min(uploadPercent, 70), 'Uploading file...')
        },
      })
      onProgress?.(85, 'Processing document...')
      onSuccess(
        `Processed: ${response.total_chunks} chunks from ${response.documents_processed} document(s)`,
        file.name,
      )
      onProgress?.(100, 'Upload complete')
    } catch (error) {
      const message =
        axios.isAxiosError(error)
          ? error.response?.data?.detail || error.message
          : error instanceof Error
            ? error.message
            : 'Unknown error'
      onProgress?.(0, 'Upload failed')
      onError(`✗ Upload failed: ${message}`)
    } finally {
      setLoading(false)
      if (fileInputRef.current) {
          fileInputRef.current.value = ''
      }
    }
  }

  return (
    <Card className="mb-6">
      <div className="flex items-center gap-3">
        <label className="flex-1 cursor-pointer">
          <div className="flex items-center gap-2">
            {loading ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <Upload className="w-5 h-5" />
            )}
            <span className="text-gray-700">
              {loading ? 'Processing...' : 'Upload document (.md, .txt, .pdf)'}
            </span>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".md,.txt,.pdf"
            onChange={handleFileSelect}
            disabled={loading}
            className="hidden"
          />
        </label>
      </div>
    </Card>
  )
}
