import { spawn, spawnSync } from "node:child_process";
import path from "node:path";
import { ROOT } from "./paths.js";

export const HF_BIN = path.join(ROOT, "node_modules", ".bin", "hyperframes");

/** stdout/stderr를 그대로 보여주며 실행. 실패 시 throw */
export function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: opts.capture ? ["ignore", "pipe", "pipe"] : "inherit", ...opts });
    let out = "";
    let err = "";
    child.stdout?.on("data", (d) => (out += d));
    child.stderr?.on("data", (d) => (err += d));
    child.on("error", reject);
    child.on("close", (code) =>
      code === 0 ? resolve({ out, err }) : reject(new Error(`${cmd} ${args.join(" ")} → exit ${code}\n${err.slice(-2000)}`)),
    );
  });
}

export function ffprobeJson(file) {
  const r = spawnSync("ffprobe", ["-v", "error", "-print_format", "json", "-show_format", "-show_streams", file], {
    encoding: "utf8",
  });
  if (r.status !== 0) throw new Error(`ffprobe 실패: ${file}\n${r.stderr}`);
  return JSON.parse(r.stdout);
}

export function mediaDuration(file) {
  return Number(ffprobeJson(file).format.duration);
}

export const round3 = (n) => Math.round(n * 1000) / 1000;
