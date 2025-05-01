import { Button } from "@/components/ui/button"
import { Check, Copy } from 'lucide-react'

interface CodeSnippetProps {
  code:string | JSX.Element;
  onCopy: () => void
  hasCopied: boolean
}

export function CodeSnippet({ code, onCopy, hasCopied }: CodeSnippetProps) {
  return (
    <div className="relative">
      <pre className="p-3 rounded-lg bg-muted font-mono text-xs whitespace-pre-wrap break-all h-[259px] w-full overflow-auto">
        {code}
      </pre>
      <Button
        size="sm"
        variant="ghost"
        className="absolute bottom-1 right-1"
        onClick={onCopy}
      >
        {hasCopied ? (
          <div className="flex items-center space-x-1">
            <Check className="h-3 w-3" />
            <span>Copied</span>
          </div>
        ) : (
          <div className="flex items-center space-x-1">
            <Copy className="h-3 w-3" />
            <span>Copy</span>
          </div>
        )}
      </Button>
    </div>
  )
}

