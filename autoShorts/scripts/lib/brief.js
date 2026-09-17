// 입력 페이지 공용: 첨부 파일 목록, refs/reference.md 생성
import fs from "node:fs";
import path from "node:path";
import { episodePaths } from "./paths.js";

export const REFERENCE_MARKER = "<!-- autoshorts:intake";
const DIRS = { reference: "refs", asset: "media" };

/** refs/(레퍼런스 캡처) + media/(영상에 쓸 자료) 실제 파일 목록에 brief.files 의 메모를 붙인다 */
export function listFiles(ep) {
  const P = episodePaths(ep.slug);
  const notes = new Map(ep.brief.files.map((f) => [f.path, f.note]));
  return Object.entries(DIRS).flatMap(([use, dir]) => {
    const abs = path.join(P.dir, dir);
    if (!fs.existsSync(abs)) return [];
    return fs
      .readdirSync(abs)
      .filter((name) => !name.startsWith(".") && !name.startsWith("reference.md"))
      .sort()
      .map((name) => {
        const rel = `${dir}/${name}`;
        return { path: rel, use, note: notes.get(rel) ?? "", size: fs.statSync(path.join(abs, name)).size };
      });
  });
}

export function uploadDir(ep, use) {
  if (!DIRS[use]) throw new Error(`알 수 없는 용도: ${use}`);
  return path.join(episodePaths(ep.slug).dir, DIRS[use]);
}

export function referenceMarkdown(ep) {
  const r = ep.reference;
  const files = listFiles(ep).filter((f) => f.use === "reference");
  return [
    `${REFERENCE_MARKER} — npm run intake -- ${ep.slug} 에서 저장할 때마다 다시 씀. 원본은 episode.json reference -->`,
    "# 레퍼런스",
    "",
    `- URL: ${r.url}`,
    `- 조회수/반응: ${r.reaction}`,
    "",
    "## 전사 (자막/나레이션 그대로)",
    "",
    r.transcript,
    "",
    "## 장면 흐름 메모 (초 단위)",
    "",
    r.sceneFlow,
    "",
    "## 캡처",
    "",
    ...(files.length ? files.map((f) => `- ${f.path}${f.note ? ` — ${f.note}` : ""}`) : ["(없음)"]),
    "",
  ].join("\n");
}

/** 직접 적어 둔 reference.md(마커 없음, 내용 있음)는 덮어쓰기 전에 한 번 백업 */
export function writeReferenceMd(ep) {
  const P = episodePaths(ep.slug);
  fs.mkdirSync(P.refs, { recursive: true });
  const file = path.join(P.refs, "reference.md");
  if (fs.existsSync(file)) {
    const cur = fs.readFileSync(file, "utf8");
    const blank = !cur.replace(/^#.*$|^- [^:]+:\s*$/gm, "").trim();
    if (!cur.startsWith(REFERENCE_MARKER) && !blank && !fs.existsSync(`${file}.bak`)) fs.copyFileSync(file, `${file}.bak`);
  }
  fs.writeFileSync(file, referenceMarkdown(ep));
}
