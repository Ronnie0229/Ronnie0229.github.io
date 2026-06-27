import { buildPostKnowledge, type PostKnowledge, type PostLike } from "./posts";

export interface RelatedPostScore<TPost = unknown> {
  post: TPost;
  score: number;
}

function overlapScore(left: string[], right: string[], points: number): number {
  const rightSet = new Set(right);
  return left.filter((item) => rightSet.has(item)).length * points;
}

export function scoreRelatedPost(currentKnowledge: PostKnowledge, candidateKnowledge: PostKnowledge): number {
  if (currentKnowledge.slug === candidateKnowledge.slug) return 0;

  let score = 0;
  score += overlapScore(currentKnowledge.bibleBooks, candidateKnowledge.bibleBooks, 100);
  score += overlapScore(currentKnowledge.topics, candidateKnowledge.topics, 50);
  score += overlapScore(currentKnowledge.tags, candidateKnowledge.tags, 10);

  if (currentKnowledge.category && currentKnowledge.category === candidateKnowledge.category) score += 20;
  if (currentKnowledge.testament !== "unknown" && currentKnowledge.testament === candidateKnowledge.testament) score += 5;

  return score;
}

function getPostDateValue(post: { data?: { date?: Date | string } }): number {
  const date = post.data?.date;
  if (!date) return 0;
  return date instanceof Date ? date.valueOf() : new Date(date).valueOf();
}

export function getRelatedPosts<TPost extends PostLike>(
  currentPost: TPost,
  allPosts: TPost[],
  limit = 3,
  buildKnowledge: (post: TPost, allPosts?: TPost[]) => PostKnowledge = buildPostKnowledge
): TPost[] {
  const currentKnowledge = buildKnowledge(currentPost, allPosts);

  return allPosts
    .map((post) => ({ post, score: scoreRelatedPost(currentKnowledge, buildKnowledge(post, allPosts)) }))
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || getPostDateValue(b.post) - getPostDateValue(a.post))
    .slice(0, limit)
    .map(({ post }) => post);
}
