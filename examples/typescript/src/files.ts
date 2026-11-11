import { join } from "node:path";

/** Base directory used by {@link resolveUserFile}. */
export const BASE_DIR = "/srv/user-files";

/**
 * Resolves a user-supplied file name under {@link BASE_DIR}.
 *
 * @param name - User-supplied file name.
 * @returns The joined path.
 * @remarks Intentionally vulnerable to path traversal to support the security benchmark task.
 */
export function resolveUserFile(name: string): string {
  return join(BASE_DIR, name);
}
