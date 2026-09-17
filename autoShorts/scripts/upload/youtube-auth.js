// YouTube OAuth 최초 1회 인증 → .secrets/youtube-token.json
//   npm run yt:auth
// Google Cloud Console → API 및 서비스 → YouTube Data API v3 사용 설정
// → OAuth 동의 화면(테스트 사용자에 본인 계정 추가) → 사용자 인증 정보 → OAuth 클라이언트 ID(데스크톱 앱)
import "../lib/env.js";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { google } from "googleapis";
import { ROOT } from "../lib/paths.js";

export const TOKEN_PATH = path.join(ROOT, ".secrets", "youtube-token.json");
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
  scope: ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"],
});

console.log(`브라우저에서 열어 로그인/동의하세요:\n\n${url}\n`);
const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, redirect);
  if (u.pathname !== "/oauth2callback") return res.end();
  try {
    const { tokens } = await oauth.getToken(u.searchParams.get("code"));
    fs.mkdirSync(path.dirname(TOKEN_PATH), { recursive: true });
    fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens, null, 2), { mode: 0o600 });
    res.end("인증 완료. 터미널로 돌아가세요.");
    console.log(`✓ 토큰 저장: ${path.relative(process.cwd(), TOKEN_PATH)}`);
  } catch (e) {
    res.end("인증 실패: " + e.message);
    console.error(e);
  } finally {
    server.close();
  }
});
server.listen(PORT, "127.0.0.1");
