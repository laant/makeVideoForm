// 제작 의도 입력 페이지 (로컬). 주제·방향·레퍼런스·대본 초안·자료·업로드 문구를 한 번에 적어 episode.json 에 저장
//   npm run intake -- <slug> [--no-open]
// "입력 완료"를 누르면 서버가 종료된다. 그다음 Claude 에서 /shorts-new <slug>
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { spawn } from "node:child_process";
import { pipeline } from "node:stream/promises";
import { ROOT, episodePaths } from "./lib/paths.js";
import { EpisodeSchema, loadEpisode, saveEpisode, slugArg, hasFlag } from "./lib/episode.js";
import { listFiles, uploadDir, writeReferenceMd } from "./lib/brief.js";

const slug = slugArg();
const P = episodePaths(slug);
loadEpisode(slug); // 없거나 스키마 오류면 여기서 중단
const PAGE = path.join(ROOT, "templates", "intake.html");
const MAX_UPLOAD = 500 * 1024 * 1024;
const TYPES = {
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
  ".svg": "image/svg+xml", ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
  ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
};

const send = (res, status, body, type = "application/json; charset=utf-8") => {
  res.writeHead(status, { "Content-Type": type, "Cache-Control": "no-store" });
  res.end(type.startsWith("application/json") ? JSON.stringify(body) : body);
};

async function readJson(req) {
  let size = 0;
  const chunks = [];
  for await (const c of req) {
    size += c.length;
    if (size > 10 * 1024 * 1024) throw new Error("요청이 너무 큽니다");
    chunks.push(c);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
}

/** refs/… 또는 media/… 만 허용 */
function safeRel(rel) {
  const norm = path.posix.normalize(String(rel || ""));
  if (!/^(refs|media)\/[^/]+$/.test(norm) || norm.endsWith("reference.md")) throw new Error(`허용되지 않는 경로: ${rel}`);
  return path.join(P.dir, norm);
}

function state() {
  const ep = loadEpisode(slug);
  return { episode: ep, files: listFiles(ep) };
}

function save(input, { submit = false } = {}) {
  const raw = JSON.parse(fs.readFileSync(P.json, "utf8"));
  const f = input ?? {};
  const next = {
    ...raw,
    topic: f.topic ?? raw.topic,
    audience: f.audience ?? raw.audience,
    tone: f.tone ?? raw.tone,
    cta: f.cta ?? raw.cta,
    reference: { ...raw.reference, ...f.reference },
    theme: { ...raw.theme, ...f.theme },
    brief: { ...raw.brief, ...f.brief },
    caption: f.caption ?? raw.caption,
    hashtags: f.hashtags ?? raw.hashtags,
    upload: { ...raw.upload, ...f.upload },
  };
  const parsed = EpisodeSchema.safeParse(next);
  if (!parsed.success) {
    throw new Error(parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("\n"));
  }
  const ep = parsed.data;
  // 메모는 실제로 존재하는 파일에 대해서만 유지
  const notes = new Map((f.brief?.files ?? ep.brief.files).map((x) => [x.path, x.note]));
  ep.brief.files = listFiles({ ...ep, brief: { ...ep.brief, files: [] } }).map(({ path: p, use }) => ({
    path: p,
    use,
    note: notes.get(p) ?? "",
  }));
  if (submit) ep.brief.submittedAt = new Date().toISOString();
  saveEpisode(ep);
  writeReferenceMd(ep);
  return ep;
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  try {
    if (req.method === "GET" && url.pathname === "/") {
      return send(res, 200, fs.readFileSync(PAGE, "utf8"), "text/html; charset=utf-8");
    }
    if (req.method === "GET" && url.pathname === "/api/state") return send(res, 200, state());

    if (req.method === "POST" && url.pathname === "/api/save") {
      save(await readJson(req));
      return send(res, 200, state());
    }

    if (req.method === "POST" && url.pathname === "/api/submit") {
      save(await readJson(req), { submit: true });
      send(res, 200, state());
      console.log(`\n✓ 입력 완료 → episodes/${slug}/episode.json 저장. Claude 에서 /shorts-new ${slug}`);
      setTimeout(() => process.exit(0), 300);
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/upload") {
      const ep = loadEpisode(slug);
      const dir = uploadDir(ep, url.searchParams.get("use"));
      if (Number(req.headers["content-length"] || 0) > MAX_UPLOAD) throw new Error("500MB 초과 파일은 올릴 수 없습니다");
      fs.mkdirSync(dir, { recursive: true });
      const original = path.basename(url.searchParams.get("name") || "file");
      const ext = path.extname(original).toLowerCase().replace(/[^.a-z0-9]/g, "");
      const stem = path.basename(original, path.extname(original)).replace(/[^\p{L}\p{N}_-]+/gu, "_").slice(0, 60) || "file";
      let name = `${stem}${ext}`;
      for (let i = 2; fs.existsSync(path.join(dir, name)) || name === "reference.md"; i++) name = `${stem}-${i}${ext}`;
      await pipeline(req, fs.createWriteStream(path.join(dir, name)));
      save(null); // brief.files·reference.md 갱신
      return send(res, 200, state());
    }

    if (req.method === "POST" && url.pathname === "/api/delete") {
      const { path: rel } = await readJson(req);
      fs.rmSync(safeRel(rel), { force: true });
      save(null);
      return send(res, 200, state());
    }

    if (req.method === "GET" && url.pathname.startsWith("/files/")) {
      const abs = safeRel(decodeURIComponent(url.pathname.slice("/files/".length)));
      if (!fs.existsSync(abs)) return send(res, 404, { error: "없음" });
      res.writeHead(200, { "Content-Type": TYPES[path.extname(abs).toLowerCase()] ?? "application/octet-stream" });
      return fs.createReadStream(abs).pipe(res);
    }

    send(res, 404, { error: "없음" });
  } catch (e) {
    send(res, 400, { error: e.message });
  }
});

function listen(port) {
  server.once("error", (e) => {
    if (e.code === "EADDRINUSE" && port < 4565) return listen(port + 1);
    throw e;
  });
  server.listen(port, "127.0.0.1", () => {
    const url = `http://127.0.0.1:${port}/`;
    console.log(`▶ 입력 페이지: ${url}  (episodes/${slug}) — "입력 완료" 또는 Ctrl+C 로 종료`);
    if (!hasFlag("no-open") && process.platform === "darwin") spawn("open", [url], { stdio: "ignore", detached: true }).unref();
  });
}
listen(4545);
