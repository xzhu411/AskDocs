import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { BookOpen, AlertCircle, CheckCircle, FolderOpen, Trash2, X, ExternalLink, Loader, Square } from 'lucide-react'
import {
  clearUploadedFiles,
  deleteUploadedFile,
  getUploadedFileUrl,
  listUploadedFiles,
  queryDocuments,
  RAGResponse,
  UploadedFileInfo,
  healthCheck,
} from './api'
import { FileUpload } from './FileUpload'
import { QueryInput } from './QueryInput'
import { Answer } from './Answer'
import { Container, Card, Button, Badge } from './components'
import './App.css'

const SUCCESS_MESSAGE_KEY = 'askmydocs_success_message'

interface ProgressState {
  visible: boolean
  percent: number
  label: string
  detail: string
  tone: 'blue' | 'green' | 'red'
}

const readStoredSuccessMessage = () => {
  if (typeof window === 'undefined') {
    return null
  }

  return (
    window.localStorage.getItem(SUCCESS_MESSAGE_KEY) ||
    window.sessionStorage.getItem(SUCCESS_MESSAGE_KEY)
  )
}

const storeSuccessMessage = (message: string | null) => {
  if (typeof window === 'undefined') {
    return
  }

  if (message) {
    window.localStorage.setItem(SUCCESS_MESSAGE_KEY, message)
    window.sessionStorage.setItem(SUCCESS_MESSAGE_KEY, message)
  } else {
    window.localStorage.removeItem(SUCCESS_MESSAGE_KEY)
    window.sessionStorage.removeItem(SUCCESS_MESSAGE_KEY)
  }
}

const createProgressState = (): ProgressState => ({
  visible: false,
  percent: 0,
  label: '',
  detail: '',
  tone: 'blue',
})

const mergeProgressState = (
  current: ProgressState | undefined,
  next: Partial<ProgressState>
): ProgressState => ({
  ...createProgressState(),
  ...(current ?? {}),
  ...next,
})

function App() {
  const [responses, setResponses] = useState<RAGResponse[]>([])
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(readStoredSuccessMessage)
  const [ready, setReady] = useState(false)
  const [filesOpen, setFilesOpen] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFileInfo[]>([])
  const [queryLoading, setQueryLoading] = useState(false)
  const [fileActionLoading, setFileActionLoading] = useState<string | null>(null)
  const [progress, setProgress] = useState<ProgressState>(createProgressState)
  const queryControllerRef = useRef<AbortController | null>(null)
  const queryProgressIntervalRef = useRef<number | null>(null)

  const loadUploadedFiles = async () => {
    try {
      const files = await listUploadedFiles()
      setUploadedFiles(files)
    } catch (err) {
      console.error('Failed to load uploaded files', err)
    }
  }

  useEffect(() => {
    const storedMessage = readStoredSuccessMessage()
    if (!successMessage && storedMessage) {
      setSuccessMessage(storedMessage)
    }
  }, [successMessage])

  useEffect(() => {
    storeSuccessMessage(successMessage)
  }, [successMessage])

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await healthCheck()
        setReady(true)
        await loadUploadedFiles()
      } catch (err) {
        setError('Backend service is not available. Please start the backend server.')
      }
    }
    bootstrap()
  }, [])

  useEffect(() => () => {
    if (queryProgressIntervalRef.current !== null) {
      window.clearInterval(queryProgressIntervalRef.current)
    }
    queryControllerRef.current?.abort()
  }, [])

  const startQueryProgress = () => {
    if (queryProgressIntervalRef.current !== null) {
      window.clearInterval(queryProgressIntervalRef.current)
    }

    setProgress({
      visible: true,
      percent: 8,
      label: 'Starting question',
      detail: 'Preparing retrieval and answer generation...',
      tone: 'blue',
    })

    const stages = [
      { percent: 18, label: 'Retrieving documents', detail: 'Searching the uploaded files for relevant sections.' },
      { percent: 34, label: 'Ranking evidence', detail: 'Comparing the best chunks for your question.' },
      { percent: 56, label: 'Drafting answer', detail: 'Generating the answer with the local model.' },
      { percent: 74, label: 'Collecting citations', detail: 'Linking the answer back to source text.' },
      { percent: 88, label: 'Finalizing response', detail: 'Formatting the result for display.' },
    ]

    let index = 0
    queryProgressIntervalRef.current = window.setInterval(() => {
      if (index >= stages.length) {
        return
      }
      const stage = stages[index]
      if (!stage) {
        return
      }
      setProgress((current) => {
        const safeCurrent = current ?? createProgressState()
        return safeCurrent.percent >= stage.percent
          ? safeCurrent
          : mergeProgressState(safeCurrent, { ...stage, visible: true, tone: 'blue' })
      })
      index += 1
    }, 1200)
  }

  const stopQueryProgress = (next?: Partial<ProgressState>) => {
    if (queryProgressIntervalRef.current !== null) {
      window.clearInterval(queryProgressIntervalRef.current)
      queryProgressIntervalRef.current = null
    }

    if (next) {
      setProgress((current) => mergeProgressState(current, { ...next, visible: true }))
      return
    }

    setProgress(createProgressState())
  }

  const handleQuery = async (query: string) => {
    setError(null)
    setQueryLoading(true)
    startQueryProgress()

    const controller = new AbortController()
    queryControllerRef.current = controller

    try {
      const response = await queryDocuments(query, controller.signal)
      setResponses((current) => [response, ...current])
      stopQueryProgress({
        percent: 100,
        label: 'Answer ready',
        detail: 'The response and citations are ready below.',
        tone: 'green',
      })
      window.setTimeout(() => setProgress(createProgressState()), 1200)
    } catch (err) {
      if (axios.isCancel(err) || (err instanceof Error && err.name === 'CanceledError')) {
        stopQueryProgress({
          percent: 0,
          label: 'Question stopped',
          detail: 'The current generation was cancelled.',
          tone: 'red',
        })
        window.setTimeout(() => setProgress(createProgressState()), 1500)
        return
      }

      const message =
        axios.isAxiosError(err)
          ? err.response?.data?.detail || err.message
          : err instanceof Error
            ? err.message
            : 'Unknown error'
      stopQueryProgress({
        percent: 0,
        label: 'Query failed',
        detail: message,
        tone: 'red',
      })
      setError(`Error: ${message}`)
    } finally {
      queryControllerRef.current = null
      setQueryLoading(false)
    }
  }

  const handleCancelQuery = () => {
    queryControllerRef.current?.abort()
  }

  const handleUploadProgress = (percent: number, label: string) => {
    setProgress({
      visible: true,
      percent,
      label,
      detail: percent < 75 ? 'Sending the file to the backend...' : 'Extracting text and indexing chunks...',
      tone: percent >= 100 ? 'green' : 'blue',
    })
  }

  const handleUploadSuccess = async (message: string, filename: string) => {
    setError(null)
    const fullMessage = `✓ ${message}`
    storeSuccessMessage(fullMessage)
    setSuccessMessage(fullMessage)
    setProgress({
      visible: true,
      percent: 100,
      label: 'Upload complete',
      detail: `${filename} is ready for questions.`,
      tone: 'green',
    })
    await loadUploadedFiles()
    window.setTimeout(() => setProgress(createProgressState()), 1200)
  }

  const handleUploadError = (message: string) => {
    storeSuccessMessage(null)
    setSuccessMessage(null)
    setProgress({
      visible: true,
      percent: 0,
      label: 'Upload failed',
      detail: message,
      tone: 'red',
    })
    setError(message)
    setTimeout(() => {
      setError(null)
      setProgress(createProgressState())
    }, 5000)
  }

  const handleDeleteFile = async (filename: string) => {
    setFileActionLoading(filename)
    setError(null)
    try {
      const result = await deleteUploadedFile(filename)
      const message = result?.message ?? `Deleted ${filename}`
      storeSuccessMessage(message)
      setSuccessMessage(message)
      setResponses([])
      await loadUploadedFiles()
    } catch (err) {
      const message =
        axios.isAxiosError(err)
          ? err.response?.data?.detail || err.message
          : err instanceof Error
            ? err.message
            : 'Unknown error'
      setError(`Error: ${message}`)
    } finally {
      setFileActionLoading(null)
    }
  }

  const handleClearFiles = async () => {
    setFileActionLoading('__all__')
    setError(null)
    try {
      const result = await clearUploadedFiles()
      const message = result?.message ?? 'Cleared uploaded files'
      storeSuccessMessage(message)
      setSuccessMessage(message)
      setResponses([])
      await loadUploadedFiles()
    } catch (err) {
      const message =
        axios.isAxiosError(err)
          ? err.response?.data?.detail || err.message
          : err instanceof Error
            ? err.message
            : 'Unknown error'
      setError(`Error: ${message}`)
    } finally {
      setFileActionLoading(null)
    }
  }

  const showInlineProgress = progress.visible

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Container>
        <div className="mb-8 flex items-start justify-between gap-6">
          <div>
            <div className="mb-2 flex items-center gap-3">
              <BookOpen className="h-8 w-8 text-blue-600" />
              <h1 className="text-4xl font-bold text-gray-900">AskMyDocs</h1>
            </div>
            <p className="text-gray-600">Chat with your documents powered by RAG AI</p>
          </div>

          <Button
            onClick={() => setFilesOpen((current) => !current)}
            variant="secondary"
            className="bg-white text-slate-700"
          >
            <span className="flex items-center gap-2">
              <FolderOpen className="h-5 w-5" />
              Browse Files
            </span>
          </Button>
        </div>

        {!ready && (
          <Card className="mb-6 border-l-4 border-red-500 bg-red-50">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-800">Connecting to backend...</p>
            </div>
          </Card>
        )}

        {error && (
          <Card className="mb-6 border-l-4 border-red-500 bg-red-50">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </Card>
        )}

        {successMessage && (
          <Card className="mb-6 border-l-4 border-green-500 bg-green-50">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <p className="text-green-800">{successMessage}</p>
              </div>
              <button
                type="button"
                onClick={() => {
                  storeSuccessMessage(null)
                  setSuccessMessage(null)
                }}
                className="text-green-700 transition hover:text-green-900"
                aria-label="Dismiss success message"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </Card>
        )}

        {filesOpen && (
          <Card className="mb-6 bg-slate-50">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Uploaded Files</p>
                <p className="mt-1 text-lg font-bold text-slate-900">Browse current documents</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge>{uploadedFiles.length}</Badge>
                <Button
                  onClick={handleClearFiles}
                  variant="secondary"
                  disabled={uploadedFiles.length === 0 || fileActionLoading !== null}
                  className="bg-white text-slate-700"
                >
                  <span className="flex items-center gap-2">
                    <Trash2 className="h-4 w-4" />
                    {fileActionLoading === '__all__' ? 'Clearing...' : 'Clear All'}
                  </span>
                </Button>
              </div>
            </div>
            {uploadedFiles.length === 0 ? (
              <p className="text-sm text-slate-600">No uploaded files yet.</p>
            ) : (
              <div className="space-y-3">
                {uploadedFiles.map((file) => (
                  <div key={file.name} className="flex items-center justify-between gap-4 rounded-lg border border-slate-200 bg-white px-4 py-3">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-bold text-slate-900">{file.name}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {file.file_type.toUpperCase()} · {(file.size / 1024).toFixed(1)} KB · {new Date(file.uploaded_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <a
                        href={getUploadedFileUrl(file.name)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
                      >
                        Open
                        <ExternalLink className="h-4 w-4" />
                      </a>
                      <Button
                        onClick={() => void handleDeleteFile(file.name)}
                        variant="secondary"
                        disabled={fileActionLoading !== null}
                        className="bg-red-50 text-red-700 hover:bg-red-100"
                      >
                        <span className="flex items-center gap-2">
                          <Trash2 className="h-4 w-4" />
                          {fileActionLoading === file.name ? 'Deleting...' : 'Delete'}
                        </span>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        <FileUpload
          onSuccess={handleUploadSuccess}
          onError={handleUploadError}
          onProgress={handleUploadProgress}
        />

        <Card className="mb-6">
          <QueryInput
            onSubmit={handleQuery}
            disabled={!ready}
            loading={queryLoading}
          />

          {showInlineProgress && (
            <div className="mt-4 border-t border-slate-200 pt-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    {progress.percent < 100 && progress.tone === 'blue' ? (
                      <Loader className="h-4 w-4 animate-spin text-blue-600" />
                    ) : progress.tone === 'green' ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                    <p className="text-sm font-semibold text-slate-900">{progress.label}</p>
                    <Badge>{progress.percent}%</Badge>
                  </div>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        progress.tone === 'blue'
                          ? 'bg-blue-500'
                          : progress.tone === 'green'
                            ? 'bg-green-500'
                            : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.max(progress.percent, 2)}%` }}
                    />
                  </div>
                  <p className="mt-2 text-xs text-slate-600">{progress.detail}</p>
                </div>
                {queryLoading && (
                  <Button
                    onClick={handleCancelQuery}
                    variant="secondary"
                    className="bg-red-100 text-red-700 hover:bg-red-200"
                  >
                    <span className="flex items-center gap-2">
                      <Square className="h-4 w-4" />
                      Stop
                    </span>
                  </Button>
                )}
              </div>
            </div>
          )}
        </Card>

        <div className="space-y-6">
          {responses.map((response, index) => (
            <Answer
              key={`${response.query}-${index}`}
              query={response.query}
              answer={response.answer}
              citations={response.citations}
              documents={response.documents}
              confidence={response.confidence}
              grounded={response.grounded}
              evidenceNote={response.evidence_note}
              processingTime={response.processing_time}
            />
          ))}
        </div>

        {responses.length === 0 && ready && (
          <Card className="py-12 text-center text-gray-500">
            <p>Upload documents and ask questions to get started!</p>
          </Card>
        )}
      </Container>
    </div>
  )
}

export default App
