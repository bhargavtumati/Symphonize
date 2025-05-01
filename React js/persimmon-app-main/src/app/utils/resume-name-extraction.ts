/**
 * Extracts filenames from URLs in messages
 * @param messages Array of messages containing URLs
 * @returns Array of extracted filenames
 */
export function extractFilenames(messages: string[]): string[] {
  return messages
    .map((message) => {
      const match = message.match(/raw\/[a-f0-9-]+_(.+)$/)
      return match ? match[1] : null
    })
    .filter((filename): filename is string => filename !== null)
}


export function cleanHTMLContent(content: string, fileName: string): string {
  const lowerFileName = fileName.trim().toLowerCase(); // Normalize filename

  // Remove entire <a> tag if it contains the file name
  let cleanedValue = content.replace(/<a[^>]*>.*?<\/a>/gi, (match) => {
    return match.toLowerCase().includes(lowerFileName) ? "" : match;
  });

  // Remove standalone occurrences of the file name (even if part of a sentence)
  cleanedValue = cleanedValue.replace(new RegExp(fileName, "gi"), "").trim();
  return cleanedValue;
}