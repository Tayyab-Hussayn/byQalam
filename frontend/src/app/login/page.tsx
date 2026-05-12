import LoginClient from "./LoginClient";

export const metadata = {
  title: "Log in - Qalam",
  description: "Log in to the Qalam dashboard.",
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const { next } = await searchParams;
  const nextPath = next?.startsWith("/") ? next : "/dashboard";
  return <LoginClient nextPath={nextPath} />;
}
