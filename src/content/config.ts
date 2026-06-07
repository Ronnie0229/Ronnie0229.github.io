import { defineCollection, z } from "astro:content";

const posts = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([])
  })
});

export const collections = { posts };
