function cleanMarkdown(markdown) {
  return String(markdown || "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/[\*_~|>#-]/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

function isUsableDescription(description) {
  const value = String(description || "").trim();
  if (value.length < 20) return false;
  const exactPlaceholder = /^(TODO|TBD|pending|placeholder|description|summary)$/i.test(value);
  const chinesePlaceholder = /(\u5f85\u8865|\u5f85\u586b|\u9700\u8981\u8865)/u.test(value);
  return !(exactPlaceholder || chinesePlaceholder);
}

function trimTrailingPunctuation(text) {
  return text.replace(/[\u3002\uff01\uff1f\uff0c,\u3001\uff1b;\uff1a:\s]+$/u, "");
}

function generateFallbackDescription(markdownOrText, maxLength = 150) {
  const cleaned = cleanMarkdown(markdownOrText);
  if (!cleaned) return "";
  if (cleaned.length <= maxLength) return trimTrailingPunctuation(cleaned);

  const slice = cleaned.slice(0, maxLength + 1);
  const punctuationIndex = Math.max(
    slice.lastIndexOf("\u3002"),
    slice.lastIndexOf("\uff01"),
    slice.lastIndexOf("\uff1f"),
    slice.lastIndexOf(";"),
    slice.lastIndexOf("\uff1b")
  );

  if (punctuationIndex >= Math.floor(maxLength * 0.5)) {
    return trimTrailingPunctuation(slice.slice(0, punctuationIndex + 1));
  }

  return `${trimTrailingPunctuation(cleaned.slice(0, maxLength))}...`;
}

function createArticleId() {
  if (globalThis.crypto?.randomUUID) return `post-${globalThis.crypto.randomUUID()}`;
  return `post-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

CMS.registerEventListener({
  name: "preSave",
  handler: ({ entry }) => {
    const data = entry.get("data");
    let nextData = data;

    const currentId = String(data.get("articleId") || "").trim();
    if (!currentId || currentId === "pending") {
      nextData = nextData.set("articleId", createArticleId());
    }

    const currentDescription = data.get("description");
    if (!isUsableDescription(currentDescription)) {
      const fallbackDescription = generateFallbackDescription(data.get("body"));
      if (fallbackDescription) {
        nextData = nextData.set("description", fallbackDescription);
      }
    }

    return nextData;
  }
});
