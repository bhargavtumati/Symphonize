import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

interface IntegrationCardProps {
  name: string
  href: string
  icon?: React.ReactNode
}

export function IntegrationCard({ name, href, icon }: IntegrationCardProps) {
  return (
    <Link href={href} className="block h-full">
      <Card className="hover:shadow-md transition-shadow h-full border-none">
        <CardContent className="flex flex-col items-center justify-center p-4 h-full">
          <div className="w-full aspect-square bg-gray-100 rounded-md flex items-center justify-center mb-4">
            {icon || (
              <span className="text-4xl text-gray-400">{name.charAt(0)}</span>
            )}
          </div>
          <div className="text-center font-bold">{name}</div>
        </CardContent>
      </Card>
    </Link>
  )
}

