// YouTube 채널 여러 개 — 채널별로 토큰을 따로 저장한다.
//   .env:  YT_CHANNEL_FINANCE=@knowledge-f-financial · YT_CHANNEL_TECH=@upup__tech · YT_CHANNEL_DEFAULT=finance
//   토큰:  .secrets/youtube-token.<key>.json   (예: youtube-token.finance.json)
// 키를 안 주면 YT_CHANNEL_DEFAULT(없으면 finance). 예전 단일 설정(YT_CHANNEL_HANDLE·youtube-token.json)은
// 기본 채널의 대체값으로만 읽는다.
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "../lib/paths.js";

const SECRETS = path.join(ROOT, ".secrets");
const LEGACY_TOKEN = path.join(SECRETS, "youtube-token.json");

export function defaultChannel() {
  return (process.env.YT_CHANNEL_DEFAULT || "finance").toLowerCase();
}

export function channelKey(key) {
  const k = (key || defaultChannel()).toLowerCase();
  if (!/^[a-z0-9_-]+$/.test(k)) throw new Error(`채널 키 형식 오류: ${key}`);
  return k;
}

/** 채널 키 → 기대 핸들(@…). YT_CHANNEL_<KEY>, 기본 채널이면 옛 YT_CHANNEL_HANDLE 도 허용 */
export function channelHandle(key) {
  const k = channelKey(key);
  const v = process.env[`YT_CHANNEL_${k.toUpperCase()}`] || (k === defaultChannel() ? process.env.YT_CHANNEL_HANDLE : "");
  return v ? v.trim() : null;
}

/** 등록된 채널 목록 {key, handle} */
export function listChannels() {
  return Object.keys(process.env)
    .map((n) => /^YT_CHANNEL_([A-Z0-9_]+)$/.exec(n)?.[1])
    .filter((k) => k && !["HANDLE", "DEFAULT"].includes(k))
    .map((k) => ({ key: k.toLowerCase(), handle: process.env[`YT_CHANNEL_${k}`] }));
}

/** 읽을 토큰 경로 — 채널 전용 파일, 없으면 (기본 채널에 한해) 옛 단일 파일 */
export function tokenPath(key) {
  const k = channelKey(key);
  const p = path.join(SECRETS, `youtube-token.${k}.json`);
  if (fs.existsSync(p)) return p;
  if (k === defaultChannel() && fs.existsSync(LEGACY_TOKEN)) return LEGACY_TOKEN;
  return p;
}

/** 쓸 토큰 경로 — 항상 채널 전용 파일 */
export function tokenWritePath(key) {
  return path.join(SECRETS, `youtube-token.${channelKey(key)}.json`);
}

/** 설정값(@핸들 또는 UC… 채널 ID)이 실제 채널 {handle,id} 와 같은가 — 핸들이 없는 채널은 ID 로 등록된다 */
export function sameChannel(want, ch) {
  if (!want || !ch) return false;
  const w = want.trim().toLowerCase();
  return w === (ch.handle ?? "").toLowerCase() || w === (ch.id ?? "").toLowerCase();
}

/** 새 채널 키를 .env 에 등록 (YT_CHANNEL_<KEY>=@핸들|UC…) */
export function registerChannel(key, value) {
  const envPath = path.join(ROOT, ".env");
  const name = `YT_CHANNEL_${channelKey(key).toUpperCase()}`;
  const cur = fs.existsSync(envPath) ? fs.readFileSync(envPath, "utf8") : "";
  if (new RegExp(`^${name}=`, "m").test(cur)) return false;
  fs.appendFileSync(envPath, `${cur.endsWith("\n") ? "" : "\n"}${name}=${value}\n`);
  process.env[name] = value;
  return true;
}
