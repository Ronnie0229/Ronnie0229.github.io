const statusText = document.querySelector("[data-stats-status]");
const summary = document.querySelector("[data-stats-summary]");
const popularList = document.querySelector("[data-popular-list]");
const trendChart = document.querySelector("[data-trend-chart]");

const number = (value) => Number(value || 0).toLocaleString("zh-CN");

async function loadStats() {
  try {
    const [statsResponse, postsResponse] = await Promise.all([
      fetch("/admin/api/stats", { cache: "no-store" }),
      fetch("/admin/posts.json", { cache: "no-store" })
    ]);
    const statsType = statsResponse.headers.get("content-type") || "";
    if (!statsType.includes("application/json")) {
      throw new Error("数据概览需要在已部署的网站后台查看");
    }
    const stats = await statsResponse.json();
    if (!statsResponse.ok) throw new Error(stats.error || "读取失败");
    const posts = postsResponse.ok ? await postsResponse.json() : [];
    const titles = Object.fromEntries(posts.map((post) => [post.slug, post.title]));

    statusText.textContent = "数据已更新";
    const cards = [
      ["累计阅读", stats.totals.totalViews],
      ["公开留言", stats.totals.visibleComments],
      ["待审核留言", stats.totals.hiddenComments]
    ];
    summary.replaceChildren(
      ...cards.map(([label, value]) => {
        const card = document.createElement("article");
        card.innerHTML = `<span>${label}</span><strong>${number(value)}</strong>`;
        return card;
      })
    );

    popularList.replaceChildren();
    stats.popular.forEach((item) => {
      const row = document.createElement("li");
      const link = document.createElement("a");
      link.href = `/posts/${encodeURIComponent(item.postSlug)}/`;
      link.textContent = titles[item.postSlug] || item.postSlug;
      const count = document.createElement("strong");
      count.textContent = `${number(item.viewCount)} 次`;
      row.append(link, count);
      popularList.append(row);
    });

    const max = Math.max(...stats.trend.map((item) => Number(item.viewCount)), 1);
    trendChart.replaceChildren();
    stats.trend.forEach((item) => {
      const bar = document.createElement("div");
      bar.className = "trend-bar";
      bar.style.setProperty("--bar-height", `${Math.max((Number(item.viewCount) / max) * 100, 3)}%`);
      bar.title = `${item.viewDate}：${number(item.viewCount)} 次`;
      bar.innerHTML = `<span></span><small>${item.viewDate.slice(5)}</small>`;
      trendChart.append(bar);
    });
  } catch (error) {
    statusText.textContent = error.message || "暂时无法读取数据";
  }
}

loadStats();
