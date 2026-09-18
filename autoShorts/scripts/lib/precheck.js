// 업로드 전 점검 (Shorts Factory 6단계) — verify · upload · publish 가 공유
//   자동: 자리표시자 · 링크 약속 vs 실제 URL · URL 접속 · 글자 수 제한
//   수동: 모바일 가독성 · 브랜딩 · 약속한 자료 내용 (체크리스트로 출력)

// 템플릿·입력 페이지·new-episode 뼈대에서 오는 기본 문구 (그대로 남으면 미완성)
const SKELETON = ["훅 문장", "CTA 문장", "헤드라인", "제목"];
const PLACEHOLDER_RE = [
  /@?your[_-]?(handle|name|channel|link|url)/i,
  /\b(TODO|TBD|FIXME|XXX+)\b/,
  /lorem ipsum/i,
  /\{\{[^}]*\}\}/,
  /\[(?:여기|이름|링크|URL|주제|채널|핸들|날짜|숫자)[^\]]*\]/i,
  /<(?:여기|이름|링크|URL|주제|채널|핸들)[^>]*>/i,
  /example\.com/i,
];
// 시청자에게 "링크를 보라"고 약속하는 표현
const LINK_PROMISE_RE = /(설명\s*(란|창)?\s*(의|에|을)?\s*링크|아래\s*링크|설명\s*란|고정\s*댓글|프로필\s*(의\s*)?링크|링크\s*(는|를|에서|확인|클릭|참고)|link\s*in\s*bio)/i;
const URL_RE = /https?:\/\/[^\s)<>"'\]]+/g;

/** onScreen 등 중첩 값에서 문자열만 [경로, 값] 으로 */
export function strings(obj, where) {
  if (typeof obj === "string") return [{ where, text: obj }];
  if (Array.isArray(obj)) return obj.flatMap((v, i) => strings(v, `${where}[${i}]`));
  if (obj && typeof obj === "object") return Object.entries(obj).flatMap(([k, v]) => strings(v, `${where}.${k}`));
  return [];
}

/** 자리표시자·뼈대 문구 → [{where, text, hit}] */
export function findPlaceholders(items) {
  const out = [];
  for (const { where, text } of items) {
    const t = text.trim();
    if (SKELETON.includes(t)) out.push({ where, text: t, hit: "뼈대 기본 문구" });
    for (const re of PLACEHOLDER_RE) {
      const m = t.match(re);
      if (m) out.push({ where, text: t.slice(0, 60), hit: m[0] });
    }
  }
  return out;
}

export const extractUrls = (text) => [...new Set((text.match(URL_RE) ?? []).map((u) => u.replace(/[.,;:!?。]+$/, "")))];

/** URL 접속 확인: ok | warn(봇 차단 가능성) | fail */
export async function checkUrl(url, timeoutMs = 10000) {
  const tryFetch = async (method) => {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), timeoutMs);
    try {
      return await fetch(url, { method, redirect: "follow", signal: ctl.signal, headers: { "user-agent": "Mozilla/5.0 (autoShorts precheck)" } });
    } finally {
      clearTimeout(timer);
    }
  };
  try {
    let res = await tryFetch("HEAD");
    if (res.status === 405 || res.status === 501) res = await tryFetch("GET");
    if (res.status < 400) return { url, level: "ok", detail: `${res.status}` };
    if ([401, 403, 429].includes(res.status)) return { url, level: "warn", detail: `${res.status} — 봇 차단일 수 있음, 브라우저로 직접 확인` };
    return { url, level: "fail", detail: `${res.status}` };
  } catch (e) {
    return { url, level: "fail", detail: e.name === "AbortError" ? "시간 초과" : e.message };
  }
}

/**
 * 업로드 전 점검
 * @param {{ texts: {where:string,text:string}[], spoken?: string[], description: string, limits?: {where:string,text:string,max:number}[] }} p
 *   texts: 자리표시자를 볼 모든 문자열(화면·제목·설명) · spoken: 나레이션 · description: 설명/캡션(링크가 있어야 할 곳)
 * @returns {Promise<{ fails: string[], warns: string[], oks: string[], manual: string[] }>}
 */
export async function precheck({ texts, spoken = [], description, limits = [] }) {
  const fails = [];
  const warns = [];
  const oks = [];

  const ph = findPlaceholders(texts);
  if (ph.length) ph.forEach((p) => fails.push(`자리표시자 남음: ${p.where} "${p.text}" (${p.hit})`));
  else oks.push("자리표시자·뼈대 문구 없음");

  const urls = extractUrls(description);
  const promiser = [...spoken.map((s) => ({ where: "나레이션", text: s })), { where: "설명", text: description }].find((x) => LINK_PROMISE_RE.test(x.text));
  if (promiser && !urls.length) fails.push(`${promiser.where}에서 링크를 안내하는데 설명에 URL 이 없음: "${promiser.text.match(LINK_PROMISE_RE)[0]}"`);
  else if (promiser) oks.push(`링크 안내 ↔ 설명 URL ${urls.length}개`);

  for (const r of await Promise.all(urls.map((u) => checkUrl(u)))) {
    const line = `URL ${r.url} → ${r.detail}`;
    (r.level === "ok" ? oks : r.level === "warn" ? warns : fails).push(line);
  }

  for (const { where, text, max } of limits) {
    if (text.length > max) warns.push(`${where} ${text.length}자 > ${max}자 — 뒷부분이 잘립니다`);
  }

  const manual = [
    "모바일 실제 크기로 재생: 자막·화면 글자가 읽히는지, 플랫폼 UI(상단·하단)에 가리지 않는지",
    "캡션·설명이 나레이션·화면 내용과 일치하는지 (숫자·날짜·조건)",
    "링크로 약속한 자료가 실제로 그 내용을 담고 있는지 (로그인 없이 열리는지)",
    "브랜딩: 색·폰트·채널 핸들·로고 위치가 다른 영상과 일관적인지",
  ];
  return { fails, warns, oks, manual };
}

export function printPrecheck(r) {
  console.log("\n── 업로드 전 점검 ──");
  r.oks.forEach((s) => console.log(`✓ ${s}`));
  r.warns.forEach((s) => console.log(`⚠ ${s}`));
  r.fails.forEach((s) => console.log(`✗ ${s}`));
  console.log("사람이 확인할 것:");
  r.manual.forEach((s) => console.log(`  □ ${s}`));
}
