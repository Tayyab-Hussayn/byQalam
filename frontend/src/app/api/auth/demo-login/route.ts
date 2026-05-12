import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE = "qalam_session";

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const next = String(formData.get("next") || "/dashboard");
  const redirectUrl = new URL(next.startsWith("/") ? next : "/dashboard", request.url);

  const response = NextResponse.redirect(redirectUrl, { status: 303 });
  response.cookies.set(SESSION_COOKIE, "demo-session", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24,
  });

  return response;
}
