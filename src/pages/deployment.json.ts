export const prerender = true;

export function GET() {
  const commit =
    process.env.CF_PAGES_COMMIT_SHA ||
    process.env.COMMIT_REF ||
    "local";

  return new Response(
    JSON.stringify({
      commit,
      builtAt: new Date().toISOString()
    }),
    {
      headers: {
        "Content-Type": "application/json; charset=UTF-8",
        "Cache-Control": "no-store"
      }
    }
  );
}
