const COUNTER_URL = "https://api.counterapi.dev/v1/ronniecross-com/site-visits";

export async function onRequestGet({ request }) {
  const url = new URL(request.url);
  const increment = url.searchParams.get("increment") === "1";

  try {
    const response = await fetch(increment ? `${COUNTER_URL}/up` : COUNTER_URL, {
      headers: { Accept: "application/json" }
    });

    if (!response.ok) {
      return Response.json({ error: "Counter service unavailable" }, { status: 502 });
    }

    const data = await response.json();

    return Response.json(
      { count: data.count },
      {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "no-store"
        }
      }
    );
  } catch {
    return Response.json({ error: "Counter service unavailable" }, { status: 502 });
  }
}
