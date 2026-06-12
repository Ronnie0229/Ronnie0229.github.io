const REPO = "Ronnie0229/Ronnie0229.github.io";
const BRANCH = "main";
const POSTS_FOLDER = "src/content/posts";
const UPLOADS_FOLDER = "assets/uploads";

const authPanel = document.querySelector("[data-auth-panel]");
const manager = document.querySelector("[data-manager]");
const editor = document.querySelector("[data-editor]");
const list = document.querySelector("[data-article-list]");
const listStatus = document.querySelector("[data-list-status]");
const searchInput = document.querySelector("[data-search]");
const filterSelect = document.querySelector("[data-filter]");
const form = document.querySelector("[data-article-form]");
const bodyInput = document.querySelector("[data-body]");
const preview = document.querySelector("[data-preview]");
const editorMessage = document.querySelector("[data-editor-message]");
const imageInput = document.querySelector("[data-image-input]");
const pagination = document.querySelector("[data-pagination]");

let token = "";
let posts = [];
let currentPage = 1;
let currentPost = null;
let currentSha = "";
let currentPath = "";
let currentFrontmatter = {};
let currentView = "edit";

function setEditorMessage(message = "", state = "") {
  editorMessage.textContent = message;
  if (state) {
    editorMessage.dataset.state = state;
  } else {
    delete editorMessage.dataset.state;
  }
}

function revealEditorMessage() {
  editorMessage.scrollIntoView({ behavior: "smooth", block: "center" });
}

function getToken() {
  try {
    const user = JSON.parse(localStorage.getItem("decap-cms-user") || "null");
    return user?.backendName === "github" ? user.token || "" : "";
  } catch {
    return "";
  }
}

function encodeBase64(value) {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function decodeBase64(value) {
  const binary = atob(value.replace(/\n/g, ""));
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function github(path, options = {}) {
  const response = await fetch(`https://api.github.com${path}`, {
    ...options,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28",
      ...(options.headers || {})
    }
  });
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("decap-cms-user");
      throw new Error("GitHub 登录已失效，请重新连接。");
    }
    if (response.status === 409) {
      throw new Error("这篇文章已在其他地方修改，请返回列表后重新打开。");
    }
    throw new Error(data?.message || "GitHub 操作失败，请稍后重试。");
  }
  return data;
}

async function findGithubFile(path) {
  const response = await fetch(
    `https://api.github.com/repos/${REPO}/contents/${encodePath(path)}?ref=${BRANCH}`,
    {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "X-GitHub-Api-Version": "2022-11-28"
      }
    }
  );
  if (response.status === 404) return null;

  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("decap-cms-user");
      throw new Error("GitHub 登录已失效，请重新连接。");
    }
    throw new Error(data?.message || "检查文章文件失败，请稍后重试。");
  }
  return data;
}

function parseValue(value) {
  const trimmed = value.trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed === "null") return null;
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("[") && trimmed.endsWith("]"))
  ) {
    try {
      return JSON.parse(trimmed);
    } catch {
      return trimmed.slice(1, -1);
    }
  }
  if (trimmed.startsWith("'") && trimmed.endsWith("'")) {
    return trimmed.slice(1, -1).replace(/''/g, "'");
  }
  return trimmed;
}

function parseMarkdown(raw) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: raw };

  const data = {};
  for (const line of match[1].split(/\r?\n/)) {
    const field = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/);
    if (field) data[field[1]] = parseValue(field[2]);
  }
  return { data, body: match[2] };
}

function yamlValue(value) {
  if (Array.isArray(value)) return JSON.stringify(value);
  if (typeof value === "boolean") return String(value);
  if (value === null || value === undefined) return '""';
  return JSON.stringify(String(value));
}

function serializeMarkdown(data, body) {
  const order = [
    "articleId",
    "title",
    "description",
    "date",
    "tags",
    "category",
    "scripture",
    "author",
    "reviewed",
    "draft",
    "source"
  ];
  const keys = [...order, ...Object.keys(data).filter((key) => !order.includes(key))];
  const lines = keys
    .filter((key) => data[key] !== undefined)
    .map((key) => `${key}: ${yamlValue(data[key])}`);
  return `---\n${lines.join("\n")}\n---\n\n${body.trim()}\n`;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderMarkdown(value) {
  return value
    .split(/\n{2,}/)
    .map((block) => {
      const text = escapeHtml(block.trim())
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\[(.+?)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2">$1</a>');
      if (text.startsWith("### ")) return `<h3>${text.slice(4)}</h3>`;
      if (text.startsWith("## ")) return `<h2>${text.slice(3)}</h2>`;
      if (text.startsWith("# ")) return `<h1>${text.slice(2)}</h1>`;
      if (text.startsWith("&gt; ")) return `<blockquote>${text.slice(5)}</blockquote>`;
      return `<p>${text.replace(/\n/g, "<br>")}</p>`;
    })
    .join("");
}

function formatDate(value) {
  if (!value) return "未填写日期";
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).format(new Date(`${String(value).slice(0, 10)}T00:00:00`));
}

function encodePath(path) {
  return path.split("/").map(encodeURIComponent).join("/");
}

function renderPosts() {
  const query = searchInput.value.trim().toLowerCase();
  const filter = filterSelect.value;
  const filtered = posts.filter((post) => {
    const matchesQuery =
      !query ||
      post.title.toLowerCase().includes(query) ||
      String(post.scripture || "").toLowerCase().includes(query);
    const matchesFilter =
      filter === "all" ||
      (filter === "draft" ? post.draft : post.category === filter);
    return matchesQuery && matchesFilter;
  });

  const pageCount = Math.max(1, Math.ceil(filtered.length / 20));
  currentPage = Math.min(currentPage, pageCount);
  const pagePosts = filtered.slice((currentPage - 1) * 20, currentPage * 20);

  list.replaceChildren();
  pagination.replaceChildren();
  listStatus.textContent = filtered.length
    ? `共 ${filtered.length} 篇文章 · 第 ${currentPage} / ${pageCount} 页`
    : "共 0 篇文章";
  if (!filtered.length) {
    const empty = document.createElement("p");
    empty.className = "admin-empty";
    empty.textContent = "没有找到符合条件的文章。";
    list.append(empty);
    return;
  }

  pagePosts.forEach((post) => {
    const article = document.createElement("article");
    article.className = "article-row";
    article.id = `article-${post.articleId || post.slug}`;

    const content = document.createElement("button");
    content.type = "button";
    content.className = "article-row-main";
    content.addEventListener("click", () => openPost(post));

    const meta = document.createElement("span");
    meta.className = "article-row-meta";
    meta.textContent = `${formatDate(post.date)} · ${post.category || "未分类"}`;

    const title = document.createElement("strong");
    title.textContent = post.title;

    const scripture = document.createElement("span");
    scripture.className = "article-row-scripture";
    scripture.textContent = post.scripture || "点击打开并编辑文章";

    const badges = document.createElement("span");
    badges.className = "article-row-badges";
    if (post.draft) {
      const draft = document.createElement("span");
      draft.className = "status-badge hidden";
      draft.textContent = "草稿";
      badges.append(draft);
    }

    const action = document.createElement("span");
    action.className = "article-row-action";
    action.textContent = "编辑";

    content.append(meta, title, scripture, badges, action);
    article.append(content);
    list.append(article);
  });

  if (pageCount > 1) {
    const previous = document.createElement("button");
    previous.type = "button";
    previous.textContent = "上一页";
    previous.disabled = currentPage === 1;
    previous.addEventListener("click", () => {
      currentPage -= 1;
      renderPosts();
      manager.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    const pageLabel = document.createElement("span");
    pageLabel.textContent = `${currentPage} / ${pageCount}`;

    const next = document.createElement("button");
    next.type = "button";
    next.textContent = "下一页";
    next.disabled = currentPage === pageCount;
    next.addEventListener("click", () => {
      currentPage += 1;
      renderPosts();
      manager.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    pagination.append(previous, pageLabel, next);
  }
}

async function loadPosts() {
  listStatus.textContent = "正在读取文章...";
  try {
    const response = await fetch("/admin/posts.json", { cache: "no-store" });
    if (!response.ok) throw new Error("无法读取文章列表。");
    posts = await response.json();
    renderPosts();
  } catch (error) {
    listStatus.textContent = error.message || "读取文章失败。";
  }
}

function showManager() {
  editor.hidden = true;
  manager.hidden = false;
  renderPosts();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  form.reset();
  form.elements.author.value = "Ronnie";
  form.elements.category.value = "灵命成长";
  form.elements.date.value = new Date().toISOString().slice(0, 10);
  currentPost = null;
  currentSha = "";
  currentPath = "";
  currentFrontmatter = { articleId: `post-${crypto.randomUUID()}` };
  setEditorMessage();
  document.querySelector("[data-delete]").hidden = true;
  document.querySelector("[data-editor-mode]").textContent = "新建文章";
  document.querySelector("[data-editor-title]").textContent = "填写文章内容";
  document.querySelector("[data-save-draft]").textContent = "保存草稿";
  setView("edit");
}

function showEditor() {
  manager.hidden = true;
  editor.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function newPost() {
  resetForm();
  showEditor();
  form.elements.title.focus();
}

async function openPost(post) {
  listStatus.textContent = "正在打开文章...";
  try {
    const fileName = post.id || `${post.slug}.md`;
    const path = `${POSTS_FOLDER}/${fileName}`;
    const data = await github(
      `/repos/${REPO}/contents/${encodePath(path)}?ref=${BRANCH}`
    );
    const parsed = parseMarkdown(decodeBase64(data.content));

    currentPost = post;
    currentSha = data.sha;
    currentPath = path;
    currentFrontmatter = parsed.data;
    form.elements.title.value = parsed.data.title || "";
    form.elements.description.value = parsed.data.description || "";
    form.elements.date.value = String(parsed.data.date || "").slice(0, 10);
    form.elements.category.value = parsed.data.category || "灵命成长";
    form.elements.scripture.value = parsed.data.scripture || "";
    form.elements.tags.value = Array.isArray(parsed.data.tags)
      ? parsed.data.tags.join(", ")
      : parsed.data.tags || "";
    form.elements.author.value = parsed.data.author || "Ronnie";
    form.elements.reviewed.checked = Boolean(parsed.data.reviewed);
    form.elements.source.value = parsed.data.source || "";
    bodyInput.value = parsed.body.trim();
    document.querySelector("[data-delete]").hidden = false;
    document.querySelector("[data-editor-mode]").textContent = parsed.data.draft
      ? "编辑草稿"
      : "编辑文章";
    document.querySelector("[data-editor-title]").textContent =
      parsed.data.title || "编辑文章";
    document.querySelector("[data-save-draft]").textContent = parsed.data.draft
      ? "保存草稿"
      : "转为草稿";
    setEditorMessage();
    showEditor();
    setView("edit");
  } catch (error) {
    listStatus.textContent = error.message || "打开文章失败。";
  }
}

function slugify(value) {
  const slug = value
    .trim()
    .replace(/[\\/:*?"<>|｜]/g, "")
    .replace(/[，。！？；、\s]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 90);
  return slug || `article-${crypto.randomUUID().slice(0, 8)}`;
}

function formData(draft) {
  const tags = form.elements.tags.value
    .split(/[,，]/)
    .map((tag) => tag.trim())
    .filter(Boolean);
  return {
    ...currentFrontmatter,
    articleId:
      currentFrontmatter.articleId || `post-${crypto.randomUUID()}`,
    title: form.elements.title.value.trim(),
    description: form.elements.description.value.trim(),
    date: form.elements.date.value,
    tags,
    category: form.elements.category.value,
    scripture: form.elements.scripture.value.trim(),
    author: form.elements.author.value.trim() || "Ronnie",
    reviewed: form.elements.reviewed.checked,
    draft,
    source: form.elements.source.value.trim()
  };
}

async function savePost(draft) {
  if (!form.reportValidity()) return;
  if (
    draft &&
    currentPost &&
    !currentPost.draft &&
    !window.confirm("保存为草稿后，这篇文章会暂时从网站撤下。确定继续吗？")
  ) {
    return;
  }
  if (!draft && !bodyInput.value.trim()) {
    setEditorMessage("发布文章前请填写正文。", "error");
    bodyInput.focus();
    revealEditorMessage();
    return;
  }
  const data = formData(draft);
  const isNew = !currentPath;
  let path =
    currentPath ||
    `${POSTS_FOLDER}/${data.date}-${slugify(data.title)}.md`;
  let targetSha = currentSha;
  const raw = serializeMarkdown(data, bodyInput.value);
  setEditorMessage(
    draft ? "正在保存草稿，请稍候..." : "正在提交文章，请稍候...",
    "saving"
  );
  setSaving(true);

  try {
    if (isNew) {
      const existing = await findGithubFile(path);
      if (existing) {
        const existingArticle = parseMarkdown(decodeBase64(existing.content));
        if (existingArticle.data.articleId === data.articleId) {
          targetSha = existing.sha;
        } else {
          const suffix = data.articleId.replace(/^post-/, "").slice(0, 8);
          path = `${POSTS_FOLDER}/${data.date}-${slugify(data.title)}-${suffix}.md`;
          const uniqueExisting = await findGithubFile(path);
          if (uniqueExisting) {
            const uniqueArticle = parseMarkdown(
              decodeBase64(uniqueExisting.content)
            );
            if (uniqueArticle.data.articleId === data.articleId) {
              targetSha = uniqueExisting.sha;
            } else {
              throw new Error("文章文件名发生冲突，请稍微修改标题后再保存。");
            }
          }
        }
      }
    }

    const payload = {
      message: `${isNew ? "Create" : "Update"} article: ${data.title}`,
      content: encodeBase64(raw),
      branch: BRANCH
    };
    if (targetSha) payload.sha = targetSha;

    const result = await github(
      `/repos/${REPO}/contents/${encodePath(path)}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }
    );
    currentPath = path;
    currentSha = result.content.sha;
    currentFrontmatter = data;
    setEditorMessage(
      draft
        ? "草稿保存成功"
        : "文章提交成功，Cloudflare 正在自动发布。",
      "success"
    );
    revealEditorMessage();

    const updated = {
      ...(currentPost || {}),
      id: path.slice(`${POSTS_FOLDER}/`.length),
      articleId: data.articleId,
      title: data.title,
      date: data.date,
      category: data.category,
      scripture: data.scripture,
      draft
    };
    posts = posts.filter((post) => post.articleId !== updated.articleId);
    posts.push(updated);
    posts.sort(
      (a, b) =>
        new Date(b.date).valueOf() - new Date(a.date).valueOf() ||
        a.title.localeCompare(b.title, "zh-CN")
    );
    currentPost = updated;
    document.querySelector("[data-delete]").hidden = false;
    document.querySelector("[data-editor-mode]").textContent = draft
      ? "编辑草稿"
      : "编辑文章";
    document.querySelector("[data-editor-title]").textContent = data.title;
    document.querySelector("[data-save-draft]").textContent = draft
      ? "保存草稿"
      : "转为草稿";
    renderPosts();
  } catch (error) {
    setEditorMessage(
      error.message || "保存失败，请稍后重试。",
      "error"
    );
    revealEditorMessage();
  } finally {
    setSaving(false);
  }
}

function setSaving(saving) {
  form.querySelectorAll("button").forEach((button) => {
    button.disabled = saving;
  });
}

function setView(view) {
  currentView = view;
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  bodyInput.hidden = view === "preview";
  preview.hidden = view !== "preview";
  document.querySelector(".compact-toolbar").hidden = view === "preview";
  if (view === "preview") {
    preview.innerHTML = renderMarkdown(bodyInput.value);
  }
}

function insertText(prefix, suffix = "") {
  const start = bodyInput.selectionStart;
  const end = bodyInput.selectionEnd;
  const selected = bodyInput.value.slice(start, end);
  bodyInput.setRangeText(`${prefix}${selected}${suffix}`, start, end, "end");
  bodyInput.focus();
}

async function uploadImage(file) {
  if (!file) return;
  const safeName = file.name
    .normalize("NFKC")
    .replace(/[^\p{L}\p{N}._-]+/gu, "-")
    .replace(/-+/g, "-");
  const path = `${UPLOADS_FOLDER}/${Date.now()}-${safeName}`;
  setEditorMessage("正在上传图片，请稍候...", "saving");
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = "";
    bytes.forEach((byte) => {
      binary += String.fromCharCode(byte);
    });
    await github(`/repos/${REPO}/contents/${encodePath(path)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `Upload image: ${file.name}`,
        content: btoa(binary),
        branch: BRANCH
      })
    });
    insertText(`![图片说明](/uploads/${path.split("/").pop()})`);
    setEditorMessage("图片上传成功，已插入正文。", "success");
    revealEditorMessage();
  } catch (error) {
    setEditorMessage(error.message || "图片上传失败。", "error");
    revealEditorMessage();
  } finally {
    imageInput.value = "";
  }
}

async function deletePost() {
  if (!currentPath || !currentSha) return;
  const confirmation = window.prompt(
    "删除后文章会从 GitHub 移除。请输入“删除”确认："
  );
  if (confirmation !== "删除") return;
  setEditorMessage("正在删除文章，请稍候...", "saving");
  setSaving(true);
  try {
    await github(`/repos/${REPO}/contents/${encodePath(currentPath)}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `Delete article: ${form.elements.title.value.trim()}`,
        sha: currentSha,
        branch: BRANCH
      })
    });
    posts = posts.filter(
      (post) => post.articleId !== currentFrontmatter.articleId
    );
    renderPosts();
    showManager();
  } catch (error) {
    setEditorMessage(error.message || "删除失败。", "error");
    revealEditorMessage();
  } finally {
    setSaving(false);
  }
}

document.querySelector("[data-new]").addEventListener("click", newPost);
document.querySelector("[data-back]").addEventListener("click", showManager);
document.querySelector("[data-cancel]").addEventListener("click", showManager);
document.querySelector("[data-save-draft]").addEventListener("click", () => {
  savePost(true);
});
document.querySelector("[data-delete]").addEventListener("click", deletePost);
searchInput.addEventListener("input", () => {
  currentPage = 1;
  renderPosts();
});
filterSelect.addEventListener("change", () => {
  currentPage = 1;
  renderPosts();
});
form.addEventListener("submit", (event) => {
  event.preventDefault();
  savePost(false);
});
document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});
document.querySelectorAll("[data-insert]").forEach((button) => {
  button.addEventListener("click", () => insertText(button.dataset.insert));
});
document.querySelector("[data-wrap]").addEventListener("click", () => {
  insertText("**", "**");
});
document.querySelector("[data-link]").addEventListener("click", () => {
  insertText("[链接文字](", ")");
});
document.querySelector("[data-image]").addEventListener("click", () => {
  imageInput.click();
});
imageInput.addEventListener("change", () => uploadImage(imageInput.files[0]));

token = getToken();
if (token) {
  authPanel.hidden = true;
  manager.hidden = false;
  loadPosts();
} else {
  authPanel.hidden = false;
}
