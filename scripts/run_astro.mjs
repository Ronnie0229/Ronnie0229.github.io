import { spawnSync } from "node:child_process";
import path from "node:path";

const command = process.argv[2];
const forwardedArgs = process.argv.slice(3);
if (!["dev", "build", "preview"].includes(command)) {
  console.error("Usage: node scripts/run_astro.mjs <dev|build|preview>");
  process.exit(2);
}

const astroCli = path.resolve("node_modules", "astro", "astro.js");
const result = spawnSync(process.execPath, [astroCli, command, ...forwardedArgs], {
  stdio: "inherit",
  env: {
    ...process.env,
    ASTRO_TELEMETRY_DISABLED: "1",
  },
});

if (result.error) {
  throw result.error;
}
process.exit(result.status ?? 1);
