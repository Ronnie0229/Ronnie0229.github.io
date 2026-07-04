export const CATEGORY_ROUTES = {
  sermons: {
    label: "教会讲道",
    category: "教会讲道",
    path: "/posts/category/sermons/",
    title: "教会讲道 | Ronnie",
    eyebrow: "教会讲道",
    heading: "听见与研读",
    description: "收录被归类为教会讲道的内容，整理文章信息，方便安静阅读与回顾。"
  },
  "spiritual-growth": {
    label: "灵命成长",
    category: "灵命成长",
    path: "/posts/category/spiritual-growth/",
    title: "灵命成长 | Ronnie",
    eyebrow: "灵命成长",
    heading: "信仰与生活",
    description: "收录个人分享、见证与信仰生活的整理，帮助日常处境中学习并活出真理。"
  }
} as const;

export type CategorySlug = keyof typeof CATEGORY_ROUTES;

export const CATEGORY_ROUTE_LIST = Object.entries(CATEGORY_ROUTES).map(
  ([slug, route]) => ({
    slug: slug as CategorySlug,
    ...route
  })
);

export function getCategoryRouteByCategory(category: string) {
  return CATEGORY_ROUTE_LIST.find((route) => route.category === category) ?? null;
}
