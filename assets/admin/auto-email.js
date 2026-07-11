(() => {
  const QUEUE_KEY = "ronniecross-pending-email-posts";
  const originalFetch = window.fetch.bind(window);
  let flushTimer = 0;
  let flushing = false;

  function readQueue() {
    try {
      const value = JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
      return Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
    } catch {
      return [];
    }
  }

  function writeQueue(slugs) {
    try {
      localStorage.setItem(QUEUE_KEY, JSON.stringify(Array.from(new Set(slugs))));
    } catch {
      // 本机存储不可用时不影响文章发布，只会跳过自动邮件。
    }
  }

  function slugFromGithubRequest(url, options) {
    if ((options?.method || "GET").toUpperCase() !== "PUT") return "";
    const marker = "/contents/src/content/posts/";
    const index = String(url).indexOf(marker);
    if (index < 0) return "";

    try {
      const payload = JSON.parse(options.body || "{}");
      const raw = decodeURIComponent(escape(atob(String(payload.content || ""))));
      if (/^draft:\s*true\s*$/m.test(raw)) return "";
    } catch {
      return "";
    }

    const encodedPath = String(url).slice(index + marker.length).split("?")[0];
    return decodeURIComponent(encodedPath).replace(/\.md$/i, "");
  }

  function enqueue(slug) {
    if (!slug) return;
    writeQueue([...readQueue(), slug]);
  }

  function showMailStatus(message, state) {
    const element = document.querySelector("[data-operation-status]");
    if (!element) return;
    element.hidden = false;
    element.textContent = message;
    if (state) element.dataset.state = state;
  }

  async function flushQueue() {
    if (flushing) return;
    const slugs = readQueue();
    if (!slugs.length) return;
    flushing = true;

    try {
      const response = await originalFetch("/api/admin/email/auto-send", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ slugs })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) {
        throw new Error(data.error || "自动邮件发送失败。");
      }

      writeQueue([]);
      if (data.postCount > 0) {
        showMailStatus(
          `${data.postCount} 篇文章已发布，提醒邮件已自动发送给 ${data.successCount} 个订阅邮箱${data.failedCount ? `，失败 ${data.failedCount} 个` : ""}。`,
          data.failedCount ? "warning" : "success"
        );
      }
    } catch (error) {
      showMailStatus(`文章已发布，但提醒邮件尚未发送：${error.message || "请稍后重新打开文章管理页面。"}`, "error");
    } finally {
      flushing = false;
    }
  }

  function scheduleFlush(delay = 12000) {
    window.clearTimeout(flushTimer);
    flushTimer = window.setTimeout(flushQueue, delay);
  }

  window.fetch = async function wrappedFetch(input, options = {}) {
    const url = typeof input === "string" ? input : input.url;
    const pendingSlug = slugFromGithubRequest(url, options);
    const response = await originalFetch(input, options);

    if (pendingSlug && response.ok) enqueue(pendingSlug);

    if (String(url).includes("/deployment.json") && response.ok) {
      try {
        const requestedCommit = new URL(url, window.location.origin).searchParams.get("commit");
        const deployment = await response.clone().json();
        if (requestedCommit && deployment.commit === requestedCommit) scheduleFlush();
      } catch {
        // 部署检查响应格式异常时，保留队列供下次进入后台重试。
      }
    }

    return response;
  };

  if (readQueue().length) scheduleFlush(2500);
})();
