const apiUrl = "/admin/api/comments";
const pageSize = 30;
const form = document.querySelector("[data-filter-form]");
const list = document.querySelector("[data-comment-list]");
const statusText = document.querySelector("[data-status]");
const previousButton = document.querySelector("[data-previous]");
const nextButton = document.querySelector("[data-next]");
const pageText = document.querySelector("[data-page]");
let currentPage = 1;
let total = 0;
let postTitles = {};

const formatDate = (value) =>
  new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(new Date(value));

async function request(url, options) {
  const response = await fetch(url, {
    cache: "no-store",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {})
    }
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "操作失败");
  return data;
}

function createButton(label, className, handler) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
}

function renderComment(comment) {
  const article = document.createElement("article");
  article.className = "admin-comment";

  const header = document.createElement("div");
  header.className = "admin-comment-header";
  const title = document.createElement("strong");
  title.textContent = comment.authorName;
  const badge = document.createElement("span");
  badge.className = `status-badge ${comment.status}`;
  badge.textContent = comment.status === "visible" ? "公开" : "已隐藏";
  header.append(title, badge);

  const meta = document.createElement("p");
  meta.className = "admin-comment-meta";
  const articleTitle = postTitles[comment.postSlug] || comment.postSlug;
  meta.textContent = `${articleTitle} · ${formatDate(comment.createdAt)} · #${comment.id}`;
  if (comment.parentId) meta.textContent += ` · 回复 #${comment.parentId}`;

  const content = document.createElement("p");
  content.className = "admin-comment-content";
  content.textContent = comment.content;

  const actions = document.createElement("div");
  actions.className = "admin-comment-actions";
  const articleLink = document.createElement("a");
  articleLink.href = `/posts/${encodeURIComponent(comment.postSlug)}/#comments`;
  articleLink.target = "_blank";
  articleLink.rel = "noopener";
  articleLink.textContent = "查看文章";
  actions.append(articleLink);

  if (comment.status === "visible") {
    actions.append(createButton("隐藏留言", "secondary", () => changeStatus(comment.id, "hide")));
  } else {
    actions.append(createButton("恢复留言", "secondary", () => changeStatus(comment.id, "restore")));
  }
  actions.append(createButton("永久删除", "danger", () => deleteComment(comment.id)));

  article.append(header, meta, content, actions);
  return article;
}

function updatePagination() {
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  pageText.textContent = `第 ${currentPage} / ${pageCount} 页`;
  previousButton.disabled = currentPage <= 1;
  nextButton.disabled = currentPage >= pageCount;
}

async function loadComments() {
  statusText.textContent = "正在读取留言...";
  list.replaceChildren();
  const data = new FormData(form);
  const params = new URLSearchParams({
    q: String(data.get("q") || ""),
    status: String(data.get("status") || "all"),
    limit: String(pageSize),
    offset: String((currentPage - 1) * pageSize)
  });

  try {
    const result = await request(`${apiUrl}?${params}`);
    total = result.total;
    statusText.textContent = `共 ${total.toLocaleString("zh-CN")} 条留言`;
    if (!result.comments.length) {
      const empty = document.createElement("p");
      empty.className = "admin-empty";
      empty.textContent = "没有符合条件的留言。";
      list.append(empty);
    } else {
      result.comments.forEach((comment) => list.append(renderComment(comment)));
    }
    updatePagination();
  } catch (error) {
    statusText.textContent = error instanceof Error ? error.message : "读取失败";
  }
}

async function changeStatus(id, action) {
  const label = action === "hide" ? "隐藏" : "恢复";
  if (!window.confirm(`${label}这条留言及其全部回复吗？`)) return;

  try {
    await request(apiUrl, {
      method: "PATCH",
      body: JSON.stringify({ id, action })
    });
    await loadComments();
  } catch (error) {
    window.alert(error instanceof Error ? error.message : "操作失败");
  }
}

async function deleteComment(id) {
  const confirmation = window.prompt(
    "永久删除后无法恢复，并会删除该留言下的全部回复。\n请输入“删除”继续："
  );
  if (confirmation !== "删除") return;

  try {
    await request(apiUrl, {
      method: "DELETE",
      body: JSON.stringify({ id, confirmation })
    });
    await loadComments();
  } catch (error) {
    window.alert(error instanceof Error ? error.message : "删除失败");
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  currentPage = 1;
  loadComments();
});
previousButton.addEventListener("click", () => {
  currentPage -= 1;
  loadComments();
});
nextButton.addEventListener("click", () => {
  currentPage += 1;
  loadComments();
});

fetch("/admin/posts.json", { cache: "no-store" })
  .then((response) => response.json())
  .then((posts) => {
    postTitles = Object.fromEntries(posts.map((post) => [post.slug, post.title]));
  })
  .catch(() => {})
  .finally(loadComments);
