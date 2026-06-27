import { parseScripture, type ScriptureKnowledge, type Testament } from "./scripture";
import { cleanMarkdown, countWords, estimateReadingTimeMinutes, generateFallbackDescription } from "./text";
import { inferTopics } from "./topics";

interface PostDataLike {
  articleId?: string;
  title?: string;
  description?: string;
  date?: Date | string;
  author?: string;
  category?: string;
  tags?: string[];
  scripture?: string;
}

export interface PostLike {
  slug?: string;
  body?: string;
  data: PostDataLike;
}

export interface PostKnowledge {
  slug: string;
  articleId: string;
  title: string;
  description: string;
  fallbackDescription: string;
  date?: Date | string;
  author: string;
  category: string;
  tags: string[];
  scripture: string;
  scriptureKnowledge: ScriptureKnowledge;
  bibleBooks: string[];
  testament: Testament;
  topics: string[];
  wordCount: number;
  readingTimeMinutes: number;
}

function isUsableDescription(description: string): boolean {
  const value = description.trim();
  return value.length >= 20 && !/(待补|TODO|TBD)/i.test(value);
}

export function buildPostKnowledge(post: PostLike, _allPosts?: PostLike[]): PostKnowledge {
  const data = post.data ?? {};
  const body = post.body ?? "";
  const fallbackDescription = generateFallbackDescription(body);
  const description = data.description && isUsableDescription(data.description) ? data.description : fallbackDescription;
  const scripture = data.scripture ?? "";
  const scriptureKnowledge = parseScripture(scripture);
  const plainText = cleanMarkdown(body);

  return {
    slug: post.slug ?? "",
    articleId: data.articleId ?? "",
    title: data.title ?? "",
    description,
    fallbackDescription,
    date: data.date,
    author: data.author ?? "",
    category: data.category ?? "",
    tags: data.tags ?? [],
    scripture,
    scriptureKnowledge,
    bibleBooks: scriptureKnowledge.books,
    testament: scriptureKnowledge.testament,
    topics: inferTopics({
      title: data.title,
      description,
      scripture,
      tags: data.tags,
      body
    }),
    wordCount: countWords(plainText),
    readingTimeMinutes: estimateReadingTimeMinutes(plainText)
  };
}
