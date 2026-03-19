import { FC, useState } from 'react'
import { AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, FileText, Quote } from 'lucide-react'
import { Citation as CitationType, DocumentRef } from './api'
import { Card, Badge, Button } from './components'

interface AnswerProps {
  query: string
  answer: string
  citations: CitationType[]
  documents: DocumentRef[]
  confidence: number
  grounded: boolean
  evidenceNote: string
  processingTime: number
}

export const Answer: FC<AnswerProps> = ({
  query,
  answer,
  citations,
  documents,
  confidence,
  grounded,
  evidenceNote,
  processingTime,
}) => {
  const [collapsed, setCollapsed] = useState(false)
  const confidencePercentage = Math.round(confidence * 100)
  const confidenceVariant =
    confidencePercentage >= 70 ? 'success' : confidencePercentage >= 35 ? 'warning' : 'default'

  return (
    <Card className="overflow-hidden p-0">
      <div className="flex items-start justify-between gap-4 border-b border-slate-200 bg-slate-50 px-5 py-4">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Question</p>
          <p className="mt-2 text-base font-bold text-slate-900">{query}</p>
        </div>
        <Button
          onClick={() => setCollapsed((current) => !current)}
          variant="secondary"
          className="shrink-0 bg-white"
        >
          {collapsed ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
        </Button>
      </div>

      {!collapsed && (
        <div>
          <div className="bg-white px-5 py-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Answer</p>
            <p className="mt-3 whitespace-pre-wrap text-base leading-7 text-slate-900">{answer}</p>
          </div>

          <div className="border-t border-slate-200 bg-slate-50 px-5 py-4">
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
              <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 font-bold ${
                grounded
                  ? 'bg-green-100 text-green-700'
                  : 'bg-amber-100 text-amber-700'
              }`}>
                {grounded ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5" />
                )}
                {grounded ? 'Document-backed' : 'Evidence limited'}
              </span>
              <span className="font-bold text-slate-700">Confidence</span>
              <Badge variant={confidenceVariant}>{confidencePercentage}%</Badge>
              <span className="font-bold text-slate-700">Time</span>
              <span>{processingTime.toFixed(2)}s</span>
              <span className="font-bold text-slate-700">Sources</span>
              <span>{documents.length}</span>
            </div>
            {evidenceNote && (
              <p className="mt-3 text-xs leading-6 text-slate-600">{evidenceNote}</p>
            )}
          </div>

          {citations.length > 0 && (
            <div className="border-t border-slate-200 bg-blue-50 px-5 py-4">
              <div className="flex items-center gap-2">
                <Quote className="h-4 w-4 text-blue-700" />
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">Citations</p>
              </div>
              <div className="mt-3 space-y-3">
                {citations.map((citation) => (
                  <div key={`${citation.index}-${citation.source}`} className="rounded-lg border border-blue-100 bg-white px-4 py-3">
                    <p className="text-sm font-bold text-slate-900">
                      [{citation.index}] {citation.source}
                    </p>
                    {citation.snippet && (
                      <p className="mt-1 text-xs leading-6 text-slate-600">{citation.snippet}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {documents.length > 0 && (
            <div className="border-t border-slate-200 bg-slate-100 px-5 py-4">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-slate-700" />
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-700">Retrieved Sources</p>
              </div>
              <div className="mt-3 space-y-3">
                {documents.map((doc) => (
                  <div key={doc.id} className="rounded-lg border border-slate-200 bg-white px-4 py-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-bold text-slate-900">{doc.metadata.source}</p>
                        <p className="mt-1 text-xs leading-6 text-slate-600">{doc.content}</p>
                      </div>
                      <Badge>{doc.metadata.file_type}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
