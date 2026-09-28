// tts → scenes → render → assemble → verify 한 번에 (업로드는 별도)
//   npm run make -- <slug> [--mock] [--draft] [--force]
import path from "node:path";
import { ROOT } from "./lib/paths.js";
import { slugArg } from "./lib/episode.js";
import { run } from "./lib/proc.js";

const slug = slugArg();
const flags = process.argv.slice(2).filter((a) => a.startsWith("--"));
const pass = (allowed) => flags.filter((f) => allowed.includes(f));

const steps = [
  ["gen-sfx.js", []],
  ["tts.js", pass(["--mock", "--force"])],
  ["build-scenes.js", pass(["--force"])],
  ["render.js", pass(["--draft", "--force"])],
  ["assemble.js", []],
  ["verify.js", []],
];
for (const [script, extra] of steps) {
  console.log(`\n━━ ${script} ━━`);
  await run(process.execPath, [path.join(ROOT, "scripts", script), ...(script === "gen-sfx.js" ? [] : [slug]), ...extra]);
}
