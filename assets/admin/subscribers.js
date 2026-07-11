const statusElement = document.querySelector("[data-status]");
const summaryElement = document.querySelector("[data-summary]");
const tableWrap = document.querySelector("[data-table-wrap]");
const listElement = document.querySelector("[data-subscriber-list]");

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function statusLabel(status) {
  if (status === "confirmed") return "已确认";
  if (status === "pending") return "待确认";
  if (status === "unsubscribed") return "已退订";
  return status || "未知";
}

function renderSummary(counts) {
  const items = [
    ["全部", counts.total],
    ["已确认", counts.confirmed],
    ["待确认", counts.pending],
    ["已退订", counts.unsubscribed]
  ];
  summaryElement.replaceChildren(
    ...items.map(([label, value]) => {
      const card = document.createElement("article");
      card.className = "admin-card subscriber-summary-card";
      const text = document.createElement("div");
      const heading = document.createElement("h2");
      const detail = document.createElement("p");
      heading.textContent = String(value ?? 0);
      detail.textContent = label;
      text.append(heading, detail);
      card.append(text);
      return card;
    })
  );
}

function renderSubscribers(subscribers) {
  listElement.replaceChildren();
  subscribers.forEach((subscriber) => {
    const row = document.createElement("tr");
    const statusTime = subscriber.status === "unsubscribed"
      ? subscriber.unsubscribedAt
      : subscriber.confirmedAt;
    [
      subscriber.email,
      statusLabel(subscriber.status),
      formatDate(subscriber.createdAt),
      formatDate(statusTime),
      formatDate(subscriber.lastSentAt)
    ].forEach((value, index) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      if (index === 1) cell.dataset.status = subscriber.status || "unknown";
      row.append(cell);
    });
    listElement.append(row);
  });
}

async function loadSubscribers() {
  try {
    const response = await fetch("/api/admin/email/subscribers", {
      headers: { Accept: "application/json" },
      cache: "no-store"
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "暂时无法读取订阅邮箱。");
    }
    renderSummary(data.counts || {});
    renderSubscribers(data.subscribers || []);
    tableWrap.hidden = false;
    statusElement.textContent = data.subscribers?.length
      ? `共 ${data.subscribers.length} 个订阅邮箱。`
      : "目前还没有订阅邮箱。";
  } catch (error) {
    statusElement.textContent = error.message || "暂时无法读取订阅邮箱。";
    statusElement.dataset.state = "error";
  }
}

loadSubscribers();
