import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE = "qalam_session";

export async function POST(request: NextRequest) {
  try {
    const { accessToken } = await request.json();

    if (!accessToken || typeof accessToken !== "string") {
      return NextResponse.json(
        { error: "Access token is required" },
        { status: 400 }
      );
    }

    const response = NextResponse.json({ ok: true });
    response.cookies.set(SESSION_COOKIE, accessToken, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 7, // 7 days - match Supabase token expiry
    });

    return response;
  } catch {
    return NextResponse.json(
      { error: "Failed to sync session" },
      { status: 500 }
    );
  }
}
