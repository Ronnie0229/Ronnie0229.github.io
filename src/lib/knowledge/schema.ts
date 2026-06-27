export type JsonLdValue = string | number | boolean | null | JsonLdObject | JsonLdValue[];
export interface JsonLdObject {
  [key: string]: JsonLdValue;
}

export interface ThingInput {
  name: string;
  description?: string;
  url?: string | URL;
}


export interface CollectionPageSchemaInput {
  name: string;
  description?: string;
  url: string | URL;
  items?: Array<{ name: string; url: string }>;
}

export interface BibleBookPageGraphInput extends CollectionPageSchemaInput {
  siteUrl: string | URL;
  logoUrl: string | URL;
  breadcrumbs?: Array<{ name: string; url: string }>;
}

export interface SiteSchemaInput {
  siteUrl: string | URL;
  searchUrl: string;
  logoUrl: string | URL;
  name: string;
  alternateName?: string;
  description?: string;
  language?: string;
}

export interface PersonSchemaInput {
  siteUrl: string | URL;
  logoUrl: string | URL;
  name: string;
}

export interface BlogPostingSchemaInput {
  canonicalUrl: string | URL;
  siteUrl: string | URL;
  image: string | URL;
  title: string;
  description: string;
  publishedTime: Date;
  author?: string;
  language?: string;
  keywords?: string[];
}

export interface SiteGraphInput extends SiteSchemaInput {
  canonicalUrl: string | URL;
  image: string | URL;
  title: string;
  pageDescription: string;
  type: "website" | "article";
  publishedTime?: Date;
  author?: string;
  keywords?: string[];
}

function asString(value: string | URL): string {
  return value.toString();
}

export function createThing({ name, description, url }: ThingInput): JsonLdObject {
  return removeEmptyValues({
    "@type": "Thing",
    name,
    description,
    url: url ? asString(url) : undefined
  });
}

export function createWebSiteSchema(input: SiteSchemaInput): JsonLdObject {
  const siteUrl = asString(input.siteUrl);

  return removeEmptyValues({
    "@type": "WebSite",
    "@id": `${siteUrl}#website`,
    url: siteUrl,
    name: input.name,
    alternateName: input.alternateName,
    description: input.description,
    inLanguage: input.language ?? "zh-CN",
    publisher: { "@id": `${siteUrl}#person` },
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: input.searchUrl
      },
      "query-input": "required name=search_term_string"
    }
  });
}

export function createPersonSchema(input: PersonSchemaInput): JsonLdObject {
  const siteUrl = asString(input.siteUrl);

  return removeEmptyValues({
    "@type": "Person",
    "@id": `${siteUrl}#person`,
    name: input.name,
    url: siteUrl,
    image: asString(input.logoUrl)
  });
}

export function createBlogPostingSchema(input: BlogPostingSchemaInput): JsonLdObject {
  const siteUrl = asString(input.siteUrl);
  const canonicalUrl = asString(input.canonicalUrl);

  return removeEmptyValues({
    "@type": "BlogPosting",
    "@id": `${canonicalUrl}#article`,
    headline: input.title.replace(/\s+\|\s+Ronnie$/, ""),
    description: input.description,
    image: asString(input.image),
    datePublished: input.publishedTime.toISOString(),
    dateModified: input.publishedTime.toISOString(),
    author: {
      "@type": "Person",
      name: input.author || "Ronnie",
      url: siteUrl
    },
    publisher: { "@id": `${siteUrl}#person` },
    mainEntityOfPage: canonicalUrl,
    inLanguage: input.language ?? "zh-CN",
    keywords: input.keywords?.length ? input.keywords.join(", ") : undefined
  });
}

export function createSiteGraph(input: SiteGraphInput): JsonLdObject {
  const graph = [
    createWebSiteSchema(input),
    createPersonSchema({
      siteUrl: input.siteUrl,
      logoUrl: input.logoUrl,
      name: "Ronnie"
    })
  ];

  if (input.type === "article" && input.publishedTime) {
    graph.push(
      createBlogPostingSchema({
        canonicalUrl: input.canonicalUrl,
        siteUrl: input.siteUrl,
        image: input.image,
        title: input.title,
        description: input.pageDescription,
        publishedTime: input.publishedTime,
        author: input.author,
        language: input.language,
        keywords: input.keywords
      })
    );
  }

  return {
    "@context": "https://schema.org",
    "@graph": graph
  };
}


export function createCollectionPageSchema(input: CollectionPageSchemaInput): JsonLdObject {
  return removeEmptyValues({
    "@type": "CollectionPage",
    name: input.name,
    description: input.description,
    url: asString(input.url),
    mainEntity: input.items?.length ? createItemList(input.items) : undefined
  });
}

export function createBibleBookPageGraph(input: BibleBookPageGraphInput): JsonLdObject {
  const graph = [
    createPersonSchema({
      siteUrl: input.siteUrl,
      logoUrl: input.logoUrl,
      name: "Ronnie"
    }),
    createCollectionPageSchema(input)
  ];

  if (input.breadcrumbs?.length) {
    graph.push(createBreadcrumbList(input.breadcrumbs));
  }

  return {
    "@context": "https://schema.org",
    "@graph": graph
  };
}

export function createBreadcrumbList(items: Array<{ name: string; url: string }>): JsonLdObject {
  return {
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url
    }))
  };
}

export function createItemList(items: Array<{ name: string; url: string }>): JsonLdObject {
  return {
    "@type": "ItemList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      url: item.url
    }))
  };
}

export function removeEmptyValues<T extends JsonLdObject>(value: T): T {
  return Object.fromEntries(
    Object.entries(value).filter(([, entry]) => {
      if (entry === undefined || entry === null || entry === "") return false;
      if (Array.isArray(entry) && entry.length === 0) return false;
      return true;
    })
  ) as T;
}
