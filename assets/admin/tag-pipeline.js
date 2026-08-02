(function initializeTagPipeline(global) {
  "use strict";

  const INVALID_TAG_CHARACTERS = /[,，、;；:：\n\r\t\[\]{}<>/\\|"']/u;

  class TagPipelineError extends Error {
    constructor(code, message) {
      super(message);
      this.name = "TagPipelineError";
      this.code = code;
    }
  }

  function normalizeText(value) {
    return String(value ?? "").normalize("NFKC").replace(/\s+/gu, " ").trim();
  }

  function lookupKey(value) {
    return normalizeText(value).toLowerCase();
  }

  function requireList(value, field) {
    if (!Array.isArray(value)) {
      throw new TagPipelineError("RULES_INVALID", `Tag rules field must be a list: ${field}`);
    }
    return value;
  }

  function validateRules(rules) {
    if (!rules || typeof rules !== "object" || Array.isArray(rules) || rules.schema_version !== "1.0") {
      throw new TagPipelineError("RULES_INVALID", "Unsupported or missing tag rules schema_version.");
    }
    if (!normalizeText(rules.rules_version)) {
      throw new TagPipelineError("RULES_INVALID", "Tag rules_version is required.");
    }
    if (!rules.limits || typeof rules.limits !== "object") {
      throw new TagPipelineError("RULES_INVALID", "Tag rules limits object is required.");
    }
    if (rules.limits.min_tags !== 2 || rules.limits.max_tags !== 6) {
      throw new TagPipelineError("RULES_INVALID", "Tag rules must enforce the approved 2-6 range.");
    }
    if (!Number.isInteger(rules.limits.max_tag_length) || rules.limits.max_tag_length < 1) {
      throw new TagPipelineError("RULES_INVALID", "Tag max_tag_length must be a positive integer.");
    }
    requireList(rules.generic_tags, "generic_tags");
    requireList(rules.ambiguous_tags, "ambiguous_tags");
    requireList(rules.admin_presets, "admin_presets");
    const books = requireList(rules.books, "books");
    const tags = requireList(rules.tags, "tags");
    const canonicals = new Set();
    const aliases = new Set();
    for (const [groupName, entries] of [["books", books], ["tags", tags]]) {
      for (const entry of entries) {
        if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
          throw new TagPipelineError("RULES_INVALID", `Invalid ${groupName} entry.`);
        }
        const canonical = normalizeText(entry.canonical);
        if (!canonical || canonicals.has(canonical)) {
          throw new TagPipelineError("RULES_INVALID", `Missing or duplicate canonical tag: ${canonical}`);
        }
        canonicals.add(canonical);
        for (const alias of [canonical, ...requireList(entry.aliases ?? [], `${canonical}.aliases`)]) {
          const key = lookupKey(alias);
          if (!key || aliases.has(key)) {
            throw new TagPipelineError("RULES_INVALID", `Duplicate tag alias: ${alias}`);
          }
          aliases.add(key);
        }
        if (groupName === "tags") {
          if (!["person", "place", "event", "theme"].includes(entry.kind)) {
            throw new TagPipelineError("RULES_INVALID", `Invalid tag kind for ${canonical}.`);
          }
          requireList(entry.inference_terms ?? [], `${canonical}.inference_terms`);
        }
      }
    }
  }

  function aliasMap(rules) {
    const aliases = new Map();
    for (const entry of rules.books) {
      const canonical = normalizeText(entry.canonical);
      for (const value of [canonical, ...(entry.aliases ?? [])]) {
        aliases.set(lookupKey(value), canonical);
      }
    }
    for (const entry of rules.tags) {
      const canonical = normalizeText(entry.canonical);
      for (const value of [canonical, ...(entry.aliases ?? [])]) {
        aliases.set(lookupKey(value), canonical);
      }
    }
    return aliases;
  }

  function scriptureBooks(scripture, rules) {
    const haystack = lookupKey(scripture);
    const matches = [];
    rules.books.forEach((entry, order) => {
      const canonical = normalizeText(entry.canonical);
      for (const value of [canonical, ...(entry.aliases ?? [])]) {
        const term = lookupKey(value);
        if (!term) continue;
        let from = 0;
        while (from <= haystack.length) {
          const start = haystack.indexOf(term, from);
          if (start < 0) break;
          const end = start + term.length;
          if (/^\.?\s*第?\s*\d/u.test(haystack.slice(end))) {
            matches.push({ start, end, length: term.length, order, canonical });
          }
          from = start + Math.max(term.length, 1);
        }
      }
    });
    matches.sort((left, right) => left.start - right.start || right.length - left.length || left.order - right.order);
    const selected = [];
    const seen = new Set();
    for (const match of matches) {
      if (seen.has(match.canonical)) continue;
      const overlaps = selected.some((used) => match.start < used.end && match.end > used.start);
      if (overlaps) continue;
      selected.push(match);
      seen.add(match.canonical);
    }
    selected.sort((left, right) => left.start - right.start);
    return selected.map((match) => match.canonical);
  }

  function ruleTags(title, subtitle, rules) {
    const haystack = lookupKey([title, subtitle].filter(Boolean).join(" "));
    if (!haystack) return [];
    return rules.tags
      .filter((entry) => (entry.inference_terms ?? []).some((term) => {
        const key = lookupKey(term);
        return key && haystack.includes(key);
      }))
      .map((entry) => normalizeText(entry.canonical));
  }

  function validateTag(tag, rules) {
    if (!tag) throw new TagPipelineError("TAG_EMPTY", "标签不能为空。");
    if (Array.from(tag).length > rules.limits.max_tag_length) {
      throw new TagPipelineError("TAG_TOO_LONG", `标签过长（最多 ${rules.limits.max_tag_length} 个字符）：${tag}`);
    }
    if (INVALID_TAG_CHARACTERS.test(tag)) {
      throw new TagPipelineError("TAG_INVALID_CHARACTER", `标签包含非法字符：${tag}`);
    }
  }

  function buildTags(input, rules) {
    validateRules(rules);
    const aliases = aliasMap(rules);
    const generic = new Set(rules.generic_tags.map(lookupKey));
    const ambiguous = new Set(rules.ambiguous_tags.map(lookupKey));
    const books = new Set(rules.books.map((entry) => normalizeText(entry.canonical)));
    const context = new Set(
      [input.category, input.author]
        .filter((value) => normalizeText(value))
        .map((value) => lookupKey(aliases.get(lookupKey(value)) ?? normalizeText(value)))
    );
    const candidates = [
      ...scriptureBooks(input.scripture ?? "", rules).map((tag) => [tag, "scripture"]),
      ...ruleTags(input.title ?? "", input.subtitle ?? "", rules).map((tag) => [tag, "rule"])
    ];

    for (const rawTag of input.manual_tags ?? []) {
      const normalized = normalizeText(rawTag);
      if (!normalized) throw new TagPipelineError("TAG_EMPTY", "人工标签不能为空。");
      const key = lookupKey(normalized);
      if (ambiguous.has(key)) {
        throw new TagPipelineError("TAG_AMBIGUOUS", `标签“${normalized}”存在人物、民族或国家歧义，请改用明确标签。`);
      }
      candidates.push([aliases.get(key) ?? normalized, "manual"]);
    }

    const tags = [];
    const evidence = [];
    const seen = new Set();
    for (const [rawTag, source] of candidates) {
      const normalized = normalizeText(rawTag);
      const canonical = aliases.get(lookupKey(normalized)) ?? normalized;
      validateTag(canonical, rules);
      const key = lookupKey(canonical);
      if (generic.has(key)) {
        throw new TagPipelineError("TAG_GENERIC", `请移除通用标签：${canonical}。改用核心人物、地点、事件或主题标签。`);
      }
      if (seen.has(key)) continue;
      seen.add(key);
      tags.push(canonical);
      evidence.push({ tag: canonical, source });
    }

    const preciseNonBook = tags.filter((tag) => !books.has(tag) && !context.has(lookupKey(tag)));
    const contextTags = tags.filter((tag) => context.has(lookupKey(tag)));
    if (contextTags.length && !preciseNonBook.length) {
      throw new TagPipelineError("TAG_CONTEXT_ONLY", "标签不能只由书卷、分类、内容类型或作者/讲员构成。请补充精准主题标签。");
    }
    if (tags.length < rules.limits.min_tags) {
      throw new TagPipelineError(
        "TAG_COUNT_TOO_LOW",
        `无法生成足够精准的标签：当前 ${tags.length} 个，至少需要 ${rules.limits.min_tags} 个。请补充人物、地点、事件或主题标签。`
      );
    }
    if (tags.length > rules.limits.max_tags) {
      throw new TagPipelineError(
        "TAG_COUNT_TOO_HIGH",
        `标签规范化后共有 ${tags.length} 个，最多允许 ${rules.limits.max_tags} 个：${tags.join("、")}。请减少人工标签。`
      );
    }
    return { tags, evidence, rules_version: normalizeText(rules.rules_version) };
  }

  global.RonnieTagPipeline = Object.freeze({
    TagPipelineError,
    buildTags,
    normalizeText,
    validateRules
  });
})(globalThis);
