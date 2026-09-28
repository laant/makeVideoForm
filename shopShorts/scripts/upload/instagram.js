// Instagram Graph API — Reels 게시 (resumable 업로드: 로컬 파일을 직접 전송, 공개 URL 불필요)
// 필요: 비즈니스/크리에이터 계정, instagram_content_publish 권한 토큰
import fs from "node:fs";

const env = () => ({
  host: process.env.IG_GRAPH_HOST || "graph.facebook.com",
  ver: process.env.IG_GRAPH_VERSION || "v23.0",
  user: process.env.IG_USER_ID,
  token: process.env.IG_ACCESS_TOKEN,
});

export function instagramReady() {
  const missing = [];
  if (!process.env.IG_USER_ID) missing.push("IG_USER_ID");
  if (!process.env.IG_ACCESS_TOKEN) missing.push("IG_ACCESS_TOKEN");
  return missing;
}

export function instagramCaption(ep) {
  return [ep.caption, "", ep.hashtags.join(" ")].join("\n").trim().slice(0, 2200);
}

async function graph(method, pathname, params = {}) {
  const { host, ver, token } = env();
  const url = new URL(`https://${host}/${ver}/${pathname}`);
  const body = new URLSearchParams({ ...params, access_token: token });
  const res =
    method === "GET"
      ? await fetch(`${url}?${body}`)
      : await fetch(url, { method, body, headers: { "Content-Type": "application/x-www-form-urlencoded" } });
  const data = await res.json();
  if (!res.ok || data.error) throw new Error(`Instagram ${pathname}: ${JSON.stringify(data.error ?? data)}`);
  return data;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function uploadInstagram(ep, file, opts) {
  return uploadInstagramWith(instagramCaption(ep), file, opts);
}

export async function uploadInstagramWith(caption, file, { thumbOffsetMs = 1200 } = {}) {
  const { user, token } = env();
  // 1) 컨테이너 생성
  const container = await graph("POST", `${user}/media`, {
    media_type: "REELS",
    upload_type: "resumable",
    caption: caption.slice(0, 2200),
    share_to_feed: "true",
    thumb_offset: String(thumbOffsetMs),
  });
  // 2) 파일 전송
  const size = fs.statSync(file).size;
  console.log(`  Instagram 컨테이너 ${container.id} — 영상 전송 (${(size / 1e6).toFixed(1)}MB)`);
  const up = await fetch(container.uri, {
    method: "POST",
    headers: { Authorization: `OAuth ${token}`, offset: "0", file_size: String(size) },
    body: fs.readFileSync(file),
  });
  const upData = await up.json().catch(() => ({}));
  if (!up.ok || upData.success === false) throw new Error(`Instagram 업로드 실패: ${JSON.stringify(upData)}`);
  // 3) 처리 완료 대기
  for (let i = 0; ; i++) {
    const st = await graph("GET", container.id, { fields: "status_code,status" });
    if (st.status_code === "FINISHED") break;
    if (st.status_code === "ERROR" || st.status_code === "EXPIRED") throw new Error(`Instagram 처리 실패: ${st.status}`);
    if (i > 60) throw new Error("Instagram 처리 대기 시간 초과(5분)");
    process.stdout.write(`\r  Instagram 처리 중… ${st.status_code}`);
    await sleep(5000);
  }
  process.stdout.write("\n");
  // 4) 게시
  const pub = await graph("POST", `${user}/media_publish`, { creation_id: container.id });
  const info = await graph("GET", pub.id, { fields: "permalink" }).catch(() => ({}));
  return { id: pub.id, url: info.permalink ?? null };
}
