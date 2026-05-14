import RegisterClient from "./RegisterClient";

export const metadata = {
  title: "Sign up - Qalam",
  description: "Create your Qalam account.",
};

export default async function RegisterPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const { next } = await searchParams;
  const nextPath = next?.startsWith("/") ? next : "/dashboard";
  return <RegisterClient nextPath={nextPath} />;
}