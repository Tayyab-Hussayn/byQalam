import { NextResponse } from "next/server";
import type { ClientErrorEvent } from "@/lib/error-reporting";

export async function POST(request: Request) {
  let payload: ClientErrorEvent | null = null;

  try {
    payload = (await request.json()) as ClientErrorEvent;
  } catch {
    payload = null;
  }

  if (payload) {
    console.error("[client-error]", JSON.stringify(payload));
  } else {
    console.error("[client-error]", "invalid payload");
  }

  return NextResponse.json({ ok: true });
}
