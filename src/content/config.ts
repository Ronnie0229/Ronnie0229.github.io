import { defineCollection, z } from "astro:content";

const posts = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    category: z.string().default("圣经学习"),
    scripture: z.string().default(""),
    author: z.string().default(""),
    reviewed: z.boolean().default(false),
    source: z.string().default("")
  })
});

export const collections = { posts };
