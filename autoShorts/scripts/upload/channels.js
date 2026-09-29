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
