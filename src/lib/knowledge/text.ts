const DEFAULT_DESCRIPTION_LENGTH = 150;
const WORDS_PER_MINUTE = 350;

export function cleanMarkdown(markdown: string): string {
  return (markdown ?? "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/[*_~|>#-]/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

export function countWords(text: string): number {
  const cleaned = cleanMarkdown(text);
  if (!cleaned) return 0;

  const cjkMatches = cleaned.match(/[\u3400-\u9fff]/g) ?? [];
  const latinMatches = cleaned
    .replace(/[\u3400-\u9fff]/g, " ")
    .match(/[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*/g) ?? [];

  return cjkMatches.length + latinMatches.length;
}

export function estimateReadingTimeMinutes(text: string): number {
  const words = countWords(text);
  return Math.max(1, Math.ceil(words / WORDS_PER_MINUTE));
}

function trimTrailingPunctuation(text: string): string {
  return text.replace(/[，,、；;：:\s]+$/u, "");
}

export function generateFallbackDescription(markdownOrText: string, maxLength = DEFAULT_DESCRIPTION_LENGTH): string {
  const cleaned = cleanMarkdown(markdownOrText);
  if (!cleaned) return "";
  if (cleaned.length <= maxLength) return trimTrailingPunctuation(cleaned);

  const slice = cleaned.slice(0, maxLength + 1);
  const punctuationIndex = Math.max(
    slice.lastIndexOf("。"),
    slice.lastIndexOf("！"),
    slice.lastIndexOf("？"),
    slice.lastIndexOf(";"),
    slice.lastIndexOf("；")
  );

  if (punctuationIndex >= Math.floor(maxLength * 0.5)) {
    return trimTrailingPunctuation(slice.slice(0, punctuationIndex + 1));
  }

  return `${trimTrailingPunctuation(cleaned.slice(0, maxLength))}...`;
}
