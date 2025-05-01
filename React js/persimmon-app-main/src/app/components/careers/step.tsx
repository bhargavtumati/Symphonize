import { ReactNode } from 'react'

interface StepProps {
  number: number
  title: string
  description?: string
  content?: ReactNode
}

export function Step({ number, title, description, content }: StepProps) {
  return (
    <div className="space-y-2">
      <div className="space-y-2">
        <div className="font-bold text-primary">Step {number}</div>
        <h2 className="text-lg font-semibold text-black">{title}</h2>
        {description && <p className="text-sm text-slate-500 mt-1">{description}</p>}
      </div>
      {content && <div className="mt-2 text-slate-500">{content}</div>}
    </div>
  )
}

