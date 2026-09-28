// HyperFrames Studio 로 에피소드 합본(index.html: 씬 + 나레이션) 미리보기
//   npm run preview -- <slug> [--stop]
import { episodePaths } from "./lib/paths.js";
import { slugArg, hasFlag } from "./lib/episode.js";
import { HF_BIN, run } from "./lib/proc.js";

const P = episodePaths(slugArg());
await run(HF_BIN, ["preview", ...(hasFlag("stop") ? ["--stop"] : ["--background"])], { cwd: P.dir });
