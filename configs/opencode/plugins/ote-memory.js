/**
 * Opt-in OpenCode plugin that injects the bounded project memory preamble.
 *
 * Enabled only when `.ote/memory/plugin.enabled` exists. Runs `ote memory preamble`
 * locally; no network access and no telemetry.
 */
import { execFile } from "node:child_process";
import { access } from "node:fs/promises";
import { join } from "node:path";
import { promisify } from "node:util";

import { Plugin } from "@opencode/plugin";

const run = promisify(execFile);

export default Plugin.define({
  id: "ote.memory",
  async setup(context) {
    const directory = context.location.directory;
    try {
      await access(join(directory, ".ote/memory/plugin.enabled"));
    } catch {
      return;
    }
    const cache = new Map();
    await context.session.hook("context", async (event) => {
      let text = cache.get(event.sessionID);
      if (text === undefined) {
        try {
          const result = await run("ote", ["memory", "preamble", "--budget", "1200"], {
            cwd: directory,
            timeout: 5000,
            maxBuffer: 200000,
          });
          text = result.stdout.trim();
        } catch {
          return;
        }
        cache.set(event.sessionID, text);
      }
      if (text) {
        event.system.push({ type: "text", text });
      }
    });
  },
});
