import { formatDistanceToNow, parseISO } from 'date-fns'

export function formatRelativeDate(dateString: string) {
  const date = parseISO(dateString)
  const distance = formatDistanceToNow(date, { addSuffix: true })
  
  // Convert "about X hours ago" to "X hours ago"
  return distance.replace('about ', '')
}

