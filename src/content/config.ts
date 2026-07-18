import { defineCollection, z } from "astro:content";

const posts = defineCollection({
  schema: z.object({
    articleId: z.string(),
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    publishedAt: z.coerce.date().optional(),
    tags: z.array(z.string()).default([]),
    category: z.string().default("教会讲道"),
    scripture: z.string().default(""),
    author: z.string().default(""),
    reviewed: z.boolean().default(false),
    draft: z.boolean().default(false),
    source: z.string().default("")
  })
});

export const collections = { posts };
