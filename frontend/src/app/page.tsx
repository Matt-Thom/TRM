import { redirect } from "next/navigation";

export default function Home() {
  // TODO(TASK-1.08): Check auth state and redirect accordingly
  redirect("/login");
}
