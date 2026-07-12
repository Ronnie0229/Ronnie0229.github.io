(() => {
  const storageKey = "ronniecross-theme";
  const navItems = [
    ["管理首页", "/admin/"],
    ["文章管理", "/admin/editor.html"],
    ["留言管理", "/admin/comments.html"],
    ["数据概览", "/admin/stats.html"],
    ["邮件订阅", "/admin/subscribers.html"],
    ["返回网站", "/"]
  ];

  const readSavedTheme = () => {
    try {
      const savedTheme = window.localStorage.getItem(storageKey);
      return savedTheme === "dark" || savedTheme === "light" ? savedTheme : null;
    } catch {
      return null;
    }
  };

  const setThemeColor = (theme) => {
    const themeColor = document.querySelector('meta[name="theme-color"]');
    themeColor?.setAttribute("content", theme === "dark" ? "#061625" : "#f7f9fc");
  };

  const applyTheme = (theme, mode = "manual", persist = false) => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.themeMode = mode;
    setThemeColor(theme);
    if (persist) {
      try {
        window.localStorage.setItem(storageKey, theme);
      } catch {
        // Theme switching still works for the current page without storage.
      }
    }
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      const nextTheme = theme === "dark" ? "light" : "dark";
      const label = theme === "dark" ? "切换到浅色模式" : "切换到深色模式";
      button.dataset.nextTheme = nextTheme;
      button.setAttribute("aria-label", label);
      button.setAttribute("title", label);
      const text = button.querySelector("[data-theme-label]");
      if (text) text.textContent = label;
    });
  };

  const currentTheme = () => {
    const savedTheme = readSavedTheme();
    if (savedTheme) return { theme: savedTheme, mode: "manual" };
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    return { theme: prefersDark ? "dark" : "light", mode: "system" };
  };

  const createLogo = () => {
    const lockup = document.createElement("span");
    lockup.className = "admin-logo-lockup";
    lockup.innerHTML = `
      <span class="admin-logo-picture" aria-hidden="true">
        <img class="admin-logo-image admin-logo-image-dark" src="/images/ronniecross-logo-theme-dark-transparent.png" alt="" loading="eager">
        <img class="admin-logo-image admin-logo-image-light" src="/images/ronniecross-logo-theme-light-transparent.png" alt="" loading="eager">
      </span>
      <span class="admin-logo-text">道路，真理，生命</span>
      <span class="admin-logo-subtitle">Admin</span>
    `;
    return lockup;
  };

  const createThemeButton = () => {
    const button = document.createElement("button");
    button.className = "admin-theme-toggle";
    button.type = "button";
    button.dataset.themeToggle = "";
    button.innerHTML = `
      <svg class="admin-theme-icon admin-theme-icon-moon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M20.3 15.4A8.4 8.4 0 0 1 8.6 3.7 8.6 8.6 0 1 0 20.3 15.4Z"></path>
      </svg>
      <svg class="admin-theme-icon admin-theme-icon-sun" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="4"></circle>
        <path d="M12 2v3M12 19v3M4.9 4.9 7 7M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1"></path>
      </svg>
      <span class="sr-only" data-theme-label>切换深浅模式</span>
    `;
    button.addEventListener("click", () => {
      applyTheme(button.dataset.nextTheme || "dark", "manual", true);
    });
    return button;
  };

  const createMenuButton = () => {
    const button = document.createElement("button");
    button.className = "admin-menu-toggle";
    button.type = "button";
    button.setAttribute("aria-controls", "admin-site-menu");
    button.setAttribute("aria-expanded", "false");
    button.dataset.adminMenuToggle = "";
    button.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
      <span class="sr-only">打开导航菜单</span>
    `;
    return button;
  };

  const createHeroLogo = () => {
    const logo = document.createElement("div");
    logo.className = "admin-hero-logo";
    logo.setAttribute("aria-hidden", "true");
    logo.innerHTML = `
      <img class="admin-hero-logo-image admin-hero-logo-dark" src="/images/ronniecross-logo-theme-dark-transparent.png" alt="">
      <img class="admin-hero-logo-image admin-hero-logo-light" src="/images/ronniecross-logo-theme-light-transparent.png" alt="">
    `;
    return logo;
  };

  const buildTopbar = () => {
    if (document.querySelector(".admin-site-header")) return;
    const shell = document.querySelector(".admin-shell");
    const hero = document.querySelector(".admin-header");
    if (!shell || !hero) return;

    const topbar = document.createElement("header");
    topbar.className = "admin-site-header";

    const brand = document.createElement("a");
    brand.className = "admin-brand";
    brand.href = "/admin/";
    brand.setAttribute("aria-label", "RonnieCross Admin 管理首页");
    brand.append(createLogo());

    const menu = document.createElement("div");
    menu.className = "admin-site-menu";
    menu.id = "admin-site-menu";
    menu.dataset.adminSiteMenu = "";

    const nav = document.createElement("nav");
    nav.className = "admin-site-nav";
    nav.setAttribute("aria-label", "后台导航");
    const path = window.location.pathname;
    navItems.forEach(([label, href]) => {
      const link = document.createElement("a");
      link.href = href;
      link.textContent = label;
      if (
        (href === "/admin/" && (path === "/admin/" || path === "/admin/index.html")) ||
        (href !== "/admin/" && href !== "/" && path.endsWith(href))
      ) {
        link.setAttribute("aria-current", "page");
      }
      nav.append(link);
    });
    menu.append(nav);

    const menuButton = createMenuButton();
    menuButton.addEventListener("click", () => {
      const isOpen = menu.classList.toggle("is-open");
      menuButton.setAttribute("aria-expanded", String(isOpen));
    });

    const actions = document.createElement("div");
    actions.className = "admin-header-actions";
    actions.append(menu, createThemeButton(), menuButton);

    topbar.append(brand, actions);
    shell.insertBefore(topbar, shell.firstChild);

    document.querySelectorAll(".admin-header").forEach((header) => {
      if (!header.querySelector(".admin-hero-logo")) {
        header.insertBefore(createHeroLogo(), header.firstChild);
      }
    });
  };

  buildTopbar();
  const { theme, mode } = currentTheme();
  applyTheme(theme, mode);

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
    if (readSavedTheme()) return;
    applyTheme(event.matches ? "dark" : "light", "system");
  });
})();
