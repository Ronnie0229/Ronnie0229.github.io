import { BIBLE_BOOKS, NEW_TESTAMENT_BOOKS, OLD_TESTAMENT_BOOKS } from "../../data/bible";

export type Testament = "old" | "new" | "mixed" | "unknown";

export interface ScriptureReference {
  raw: string;
  book: string;
  chapterStart?: number;
  verseStart?: number;
  chapterEnd?: number;
  verseEnd?: number;
}

export interface ScriptureKnowledge {
  raw: string;
  books: string[];
  testament: Testament;
  references: ScriptureReference[];
}

const oldBooks = new Set<string>(OLD_TESTAMENT_BOOKS);
const newBooks = new Set<string>(NEW_TESTAMENT_BOOKS);

function getTestamentForBooks(books: string[]): Testament {
  const hasOld = books.some((book) => oldBooks.has(book));
  const hasNew = books.some((book) => newBooks.has(book));

  if (hasOld && hasNew) return "mixed";
  if (hasOld) return "old";
  if (hasNew) return "new";
  return "unknown";
}

function uniqueBooks(scripture: string): string[] {
  return BIBLE_BOOKS.filter((book) => scripture.includes(book));
}

function parseRange(rawRange: string): Omit<ScriptureReference, "raw" | "book"> {
  const range = rawRange.trim().replace(/[，。；;]$/u, "");
  const match = /^(\d+)(?::(\d+))?(?:-(?:(\d+):)?(\d+))?$/.exec(range);

  if (!match) return {};

  const chapterStart = Number(match[1]);
  const verseStart = match[2] ? Number(match[2]) : undefined;
  const chapterEnd = match[3] ? Number(match[3]) : undefined;
  const verseEnd = match[4] ? Number(match[4]) : undefined;

  return {
    chapterStart,
    verseStart,
    chapterEnd: chapterEnd ?? (verseEnd ? chapterStart : undefined),
    verseEnd
  };
}

function parseBookReferences(scripture: string, book: string): ScriptureReference[] {
  const escapedBook = book.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(`${escapedBook}\\s*([^${BIBLE_BOOKS.join("").replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}]*)`, "g");
  const references: ScriptureReference[] = [];
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(scripture)) !== null) {
    const segment = match[0].trim();
    const rangeText = (match[1] ?? "").trim();
    const firstRange = rangeText.split(/[、,，；;]/u).map((part) => part.trim()).find(Boolean) ?? "";

    references.push({
      raw: segment || book,
      book,
      ...parseRange(firstRange)
    });
  }

  return references;
}

export function parseScripture(scripture: string): ScriptureKnowledge {
  const raw = scripture ?? "";
  const books = uniqueBooks(raw);
  const references = books.flatMap((book) => parseBookReferences(raw, book));

  return {
    raw,
    books,
    testament: getTestamentForBooks(books),
    references: references.length > 0 ? references : books.map((book) => ({ raw: book, book }))
  };
}
