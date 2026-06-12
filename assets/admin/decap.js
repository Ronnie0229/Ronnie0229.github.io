CMS.registerEventListener({
  name: "preSave",
  handler: ({ entry }) => {
    const data = entry.get("data");
    const currentId = data.get("articleId");
    if (currentId && currentId !== "pending") return data;

    const articleId = `post-${crypto.randomUUID()}`;
    return data.set("articleId", articleId);
  }
});
