// YouTube OAuth 인증 — 채널별 토큰 → .secrets/youtube-token.<키>.json
//   npm run yt:auth -- --channel finance | tech      (생략하면 YT_CHANNEL_DEFAULT)
// 브라우저에서 고른 채널이 .env YT_CHANNEL_<키> 와 다르면 저장하지 않는다(다른 채널 토큰을 덮어쓰는 사고 방지).
// Google Cloud Console → API 및 서비스 → YouTube Data API v3 사용 설정
// → OAuth 동의 화면(테스트 사용자에 본인 계정 추가) → 사용자 인증 정보 → OAuth 클라이언트 ID(데스크톱 앱)
import "../lib/env.js";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { google } from "googleapis";
import { channelKey, channelHandle, tokenWritePath, listChannels } from "./channels.js";

const ai = process.argv.indexOf("--channel");
const KEY = channelKey(ai >= 0 ? process.argv[ai + 1] : undefined);
const WANT = channelHandle(KEY);
if (!WANT) {
  console.error(`YT_CHANNEL_${KEY.toUpperCase()} 가 .env 에 없습니다. 등록된 채널: ${listChannels().map((c) => `${c.key}=${c.handle}`).join(", ") || "(없음)"}`);
  process.exit(1);
}
export const TOKEN_PATH = tokenWritePath(KEY);
const PORT = 53682;

if (!process.env.YT_CLIENT_ID || !process.env.YT_CLIENT_SECRET) {
  console.error("YT_CLIENT_ID / YT_CLIENT_SECRET 을 .env 에 설정하세요.");
  process.exit(1);
}
const redirect = `http://127.0.0.1:${PORT}/oauth2callback`;
const oauth = new google.auth.OAuth2(process.env.YT_CLIENT_ID, process.env.YT_CLIENT_SECRET, redirect);
const url = oauth.generateAuthUrl({
  access_type: "offline",
  prompt: "consent",
  // force-ssl: 올린 뒤 제목·설명 수정(videos.update)용. upload 권한만으로는 403 insufficient scopes
  scope: ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtube.force-ssl"],
});

console.log(`[${KEY}] ${WANT} 채널로 인증합니다 — 브라우저에서 반드시 이 브랜드 채널을 고르세요.\n\n${url}\n`);
const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, redirect);
  if (u.pathname !== "/oauth2callback") return res.end();
  try {
    const { tokens } = await oauth.getToken(u.searchParams.get("code"));
    oauth.setCredentials(tokens);
    const ch = await google.youtube({ version: "v3", auth: oauth }).channels.list({ part: ["snippet"], mine: true });
    const c = ch.data.items?.[0];
    const got = (c?.snippet.customUrl ?? "").toLowerCase();
    if (!c || got !== WANT.toLowerCase()) {
      res.end(`채널 불일치 — 저장하지 않았습니다. 다시 실행해 ${WANT} 를 고르세요.`);
      console.error(`✗ 선택한 채널 ${c ? `${c.snippet.title} ${c.snippet.customUrl ?? ""}` : "(없음)"} ≠ [${KEY}] ${WANT} — 토큰을 저장하지 않았습니다`);
      return;
    }
    fs.mkdirSync(path.dirname(TOKEN_PATH), { recursive: true });
    fs.writeFileSync(TOKEN_PATH, JSON.stringify({ ...tokens, obtained_at: new Date().toISOString(), channel: { key: KEY, handle: c.snippet.customUrl, id: c.id } }, null, 2), { mode: 0o600 });
    res.end("인증 완료. 터미널로 돌아가세요.");
    console.log(`✓ [${KEY}] 채널: ${c.snippet.title} ${c.snippet.customUrl} (${c.id})`);
    console.log(`✓ 토큰 저장: ${path.relative(process.cwd(), TOKEN_PATH)}`);
  } catch (e) {
    res.end("인증 실패: " + e.message);
    console.error(e);
  } finally {
    server.close();
  }
});
server.listen(PORT, "127.0.0.1");
