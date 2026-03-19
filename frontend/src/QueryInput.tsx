import { FC, useState } from 'react'
import { Send, Loader } from 'lucide-react'
import { Button } from './components'

interface QueryInputProps {
  onSubmit: (query: string) => Promise<void>
  disabled?: boolean
  loading?: boolean
}

export const QueryInput: FC<QueryInputProps> = ({ onSubmit, disabled = false, loading = false }) => {
  const [query, setQuery] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading || disabled) return

    try {
      await onSubmit(query)
      setQuery('')
    } finally {}
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question about your documents..."
        disabled={loading || disabled}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
      />
      <Button
        type="submit"
        disabled={!query.trim() || loading || disabled}
      >
        {loading ? (
          <Loader className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
      </Button>
    </form>
  )
}
