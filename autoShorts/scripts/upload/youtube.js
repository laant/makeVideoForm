// YouTube Data API v3 — Shorts 업로드 (세로 영상 ≤ 3분이면 자동으로 Shorts 분류)
import fs from "node:fs";
import path from "node:path";
import { google } from "googleapis";
import { ROOT } from "../lib/paths.js";

const TOKEN_PATH = path.join(ROOT, ".secrets", "youtube-token.json");

export function youtubeReady() {
  const missing = [];
  if (!process.env.YT_CLIENT_ID) missing.push("YT_CLIENT_ID");
  if (!process.env.YT_CLIENT_SECRET) missing.push("YT_CLIENT_SECRET");
  if (!fs.existsSync(TOKEN_PATH)) missing.push(".secrets/youtube-token.json (npm run yt:auth)");
  return missing;
}

export function youtubeMeta(ep) {
  const base = ep.upload.title || ep.topic;
  const title = (base.includes("#Shorts") ? base : `${base} #Shorts`).slice(0, 100);
  const description = [ep.caption, "", ep.hashtags.join(" ")].join("\n").trim().slice(0, 5000);
  const tags = ep.hashtags.map((h) => h.replace(/^#/, "")).slice(0, 15);
  return { title, description, tags, privacyStatus: process.env.YT_PRIVACY || "private" };
}

export async function uploadYouTube(ep, file) {
  return uploadYouTubeWith(youtubeMeta(ep), file);
}

// meta: { title, description, tags, privacyStatus, publishAt? } · thumbnail: jpg 경로(선택, 채널 전화 인증 필요)
function client() {
  const oauth = new google.auth.OAuth2(process.env.YT_CLIENT_ID, process.env.YT_CLIENT_SECRET);
  oauth.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8")));
  // access token 갱신 시 저장 (refresh_token 유지)
  oauth.on("tokens", (t) => {
    const cur = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8"));
    fs.writeFileSync(TOKEN_PATH, JSON.stringify({ ...cur, ...t }, null, 2), { mode: 0o600 });
  });
  return google.youtube({ version: "v3", auth: oauth });
}

// OAuth 앱이 '테스트' 상태면 refresh token 이 7일 뒤 만료 → invalid_grant
export function explainAuthError(e) {
  const msg = String(e?.response?.data?.error ?? e?.message ?? e);
  return /invalid_grant|expired|revoked/i.test(msg)
    ? `YouTube 토큰 만료·폐기 (OAuth 앱 '테스트' 상태는 7일마다 만료) — npm run yt:auth 로 다시 인증하세요`
    : msg;
}

/** 토큰 발급 경과 일수 (yt:auth 가 obtained_at 기록, 없으면 null) */
export function youtubeTokenAgeDays() {
  if (!fs.existsSync(TOKEN_PATH)) return null;
  const at = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8")).obtained_at;
  return at ? (Date.now() - Date.parse(at)) / 86400000 : null;
}

/** 토큰이 가리키는 채널 { id, title, handle } */
export async function youtubeChannel() {
  const res = await client().channels.list({ part: ["snippet"], mine: true });
  const c = res.data.items?.[0];
  if (!c) throw new Error("토큰에 연결된 YouTube 채널이 없습니다 — yt:auth 에서 채널을 선택했는지 확인");
  return { id: c.id, title: c.snippet.title, handle: c.snippet.customUrl ?? null };
}

export async function uploadYouTubeWith(meta, file, { thumbnail } = {}) {
  const yt = client();
  const size = fs.statSync(file).size;
  const status = { privacyStatus: meta.publishAt ? "private" : meta.privacyStatus, selfDeclaredMadeForKids: false };
  if (meta.publishAt) status.publishAt = meta.publishAt;
  const res = await yt.videos.insert(
    {
      part: ["snippet", "status"],
      requestBody: {
        snippet: { title: meta.title, description: meta.description, tags: meta.tags, categoryId: "22", defaultLanguage: "ko" },
        status,
      },
      media: { body: fs.createReadStream(file) },
    },
    {
      onUploadProgress: (e) => process.stdout.write(`\r  YouTube 업로드 ${Math.round((e.bytesRead / size) * 100)}%`),
    },
  );
  process.stdout.write("\n");
  const id = res.data.id;
  const result = { id, url: `https://youtube.com/shorts/${id}`, privacy: res.data.status?.privacyStatus, publishAt: res.data.status?.publishAt ?? null };
  if (thumbnail) {
    try {
      await yt.thumbnails.set({ videoId: id, media: { mimeType: "image/jpeg", body: fs.createReadStream(thumbnail) } });
      result.thumbnail = path.basename(thumbnail);
    } catch (e) {
      // 영상은 이미 올라갔으므로 실패로 처리하지 않음 (대개 채널 전화 인증 미완료)
      console.warn(`  ⚠ 썸네일 설정 실패: ${e.message} — YouTube Studio에서 직접 지정하세요`);
      result.thumbnailError = e.message;
    }
  }
  return result;
}
