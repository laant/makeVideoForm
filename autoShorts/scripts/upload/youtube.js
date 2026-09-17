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
  const oauth = new google.auth.OAuth2(process.env.YT_CLIENT_ID, process.env.YT_CLIENT_SECRET);
  oauth.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8")));
  // access token 갱신 시 저장 (refresh_token 유지)
  oauth.on("tokens", (t) => {
    const cur = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8"));
    fs.writeFileSync(TOKEN_PATH, JSON.stringify({ ...cur, ...t }, null, 2), { mode: 0o600 });
  });
  const yt = google.youtube({ version: "v3", auth: oauth });
  const meta = youtubeMeta(ep);
  const size = fs.statSync(file).size;
  const res = await yt.videos.insert(
    {
      part: ["snippet", "status"],
      requestBody: {
        snippet: { title: meta.title, description: meta.description, tags: meta.tags, categoryId: "22", defaultLanguage: "ko" },
        status: { privacyStatus: meta.privacyStatus, selfDeclaredMadeForKids: false },
      },
      media: { body: fs.createReadStream(file) },
    },
    {
      onUploadProgress: (e) => process.stdout.write(`\r  YouTube 업로드 ${Math.round((e.bytesRead / size) * 100)}%`),
    },
  );
  process.stdout.write("\n");
  return { id: res.data.id, url: `https://youtube.com/shorts/${res.data.id}`, privacy: meta.privacyStatus };
}
