import { join } from "node:path";

export const BASE_DIR = "/srv/user-files";

// Intentionally vulnerable for the security benchmark task.
export function resolveUserFile(name: string): string {
  return join(BASE_DIR, name);
}
