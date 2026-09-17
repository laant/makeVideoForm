import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
export const TEMPLATES = path.join(ROOT, "templates");
export const SFX_DIR = path.join(ROOT, "assets", "sfx");
export const EPISODES = path.join(ROOT, "episodes");

export function episodePaths(slug) {
  const dir = path.join(EPISODES, slug);
  return {
    dir,
    json: path.join(dir, "episode.json"),
    refs: path.join(dir, "refs"),
    media: path.join(dir, "media"),
    audio: path.join(dir, "audio"),
    narration: path.join(dir, "audio", "narration.mp3"),
    scenes: path.join(dir, "scenes"),
    vendor: path.join(dir, "vendor"),
    renders: path.join(dir, "renders"),
    check: path.join(dir, "renders", "check"),
    cards: path.join(dir, "cards"),
    final: path.join(dir, "final.mp4"),
    uploadLog: path.join(dir, "upload-log.json"),
  };
}
