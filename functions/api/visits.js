const COUNTER_URL = "https://api.counterapi.dev/v1/ronniecross-com/site-visits";

function emptyNoindex(status = 204) {
  return new Response(null, {
    status,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}

export async function onRequestGet({ request }) {
  const url = new URL(request.url);
  const increment = url.searchParams.get("increment") === "1";

  if (!increment && !url.searchParams.toString()) {
    return emptyNoindex();
  }

  try {
    const response = await fetch(increment ? `${COUNTER_URL}/up` : COUNTER_URL, {
      headers: { Accept: "application/json" }
    });

    if (!response.ok) {
      return Response.json(
        { error: "Counter service unavailable" },
        { status: 502, headers: { "X-Robots-Tag": "noindex, nofollow" } }
      );
    }

    const data = await response.json();

    return Response.json(
      { count: data.count },
      {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "no-store",
          "X-Robots-Tag": "noindex, nofollow"
        }
      }
    );
  } catch {
    return Response.json(
      { error: "Counter service unavailable" },
      { status: 502, headers: { "X-Robots-Tag": "noindex, nofollow" } }
    );
  }
}

export function onRequestHead() {
  return emptyNoindex();
}
