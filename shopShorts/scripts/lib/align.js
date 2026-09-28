// 대본(정답 텍스트) ↔ 음성 인식 토큰(시간) 정렬 → 대본 단어별 타임스탬프
// 인식 결과의 "글자"는 틀릴 수 있으므로 시간만 가져온다. 글자 단위 편집거리 정렬 후,
// 짝이 없는 대본 글자는 앞뒤 시간으로 보간한다.
import { round3 } from "./proc.js";

const isChar = (c) => /[\p{L}\p{N}]/u.test(c);

/**
 * @param {string} narration
 * @param {{text:string, from:number, to:number}[]} tokens  초 단위
 * @param {number} audioEnd  음성 길이(초)
 * @returns {{ words: {text,start,end}[], matchRatio: number, recognized: string }}
 */
export function alignWords(narration, tokens, audioEnd) {
  // 인식 글자: 토큰 시간을 글자 수로 균등 분배
  const rec = [];
  for (const t of tokens) {
    const chars = [...t.text].filter(isChar);
    const step = chars.length ? (t.to - t.from) / chars.length : 0;
    chars.forEach((c, i) => rec.push({ c, start: t.from + step * i, end: t.from + step * (i + 1) }));
  }

  // 대본 글자 (단어 인덱스 포함)
  const wordsText = narration.split(/\s+/).filter(Boolean);
  const nar = [];
  wordsText.forEach((w, wi) => [...w].filter(isChar).forEach((c) => nar.push({ c, wi })));

  // 편집거리 DP
  const n = nar.length;
  const m = rec.length;
  const D = Array.from({ length: n + 1 }, (_, i) => new Int32Array(m + 1).fill(0).map((_, j) => (i === 0 ? j : j === 0 ? i : 0)));
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      const sub = D[i - 1][j - 1] + (nar[i - 1].c === rec[j - 1].c ? 0 : 1);
      D[i][j] = Math.min(sub, D[i - 1][j] + 1, D[i][j - 1] + 1);
    }
  }
  // 역추적: 대본 글자 → 인식 글자
  const map = new Array(n).fill(null);
  let matches = 0;
  for (let i = n, j = m; i > 0 || j > 0; ) {
    if (i > 0 && j > 0 && D[i][j] === D[i - 1][j - 1] + (nar[i - 1].c === rec[j - 1].c ? 0 : 1)) {
      map[i - 1] = rec[j - 1];
      if (nar[i - 1].c === rec[j - 1].c) matches++;
      i--;
      j--;
    } else if (i > 0 && (j === 0 || D[i][j] === D[i - 1][j] + 1)) {
      i--;
    } else {
      j--;
    }
  }

  // 짝 없는 글자 보간
  const times = map.map((r) => (r ? { start: r.start, end: r.end } : null));
  for (let i = 0; i < n; i++) {
    if (times[i]) continue;
    let k = i;
    while (k < n && !times[k]) k++;
    const from = i > 0 ? times[i - 1].end : 0;
    const to = k < n ? times[k].start : audioEnd;
    const step = (to - from) / (k - i);
    for (let x = i; x < k; x++) times[x] = { start: from + step * (x - i), end: from + step * (x - i + 1) };
    i = k - 1;
  }

  // 단어로 묶기 (글자가 없는 단어는 직전 끝 시간)
  const words = [];
  let prevEnd = 0;
  wordsText.forEach((text, wi) => {
    const idx = nar.map((x, i) => (x.wi === wi ? i : -1)).filter((i) => i >= 0);
    const start = idx.length ? Math.max(prevEnd, times[idx[0]].start) : prevEnd;
    const end = idx.length ? Math.max(start, times[idx.at(-1)].end) : prevEnd;
    words.push({ text, start, end });
    prevEnd = start;
  });
  // 같은 시각에 몰린 단어들(예: 인식은 "19.4%", 대본은 "십구 점 사 퍼센트")은 다음 단어 시작까지 글자 수 비례로 펼친다
  for (let i = 0; i < words.length; ) {
    let k = i + 1;
    while (k < words.length && words[k].start - words[i].start < 0.02) k++;
    if (k - i > 1) {
      const from = words[i].start;
      const to = k < words.length ? words[k].start : Math.max(words[k - 1].end, from);
      const lens = words.slice(i, k).map((w) => Math.max(1, [...w.text].filter(isChar).length));
      const total = lens.reduce((a, b) => a + b, 0);
      let t = from;
      for (let x = i; x < k; x++) {
        words[x].start = t;
        t += ((to - from) * lens[x - i]) / total;
        words[x].end = Math.max(words[x].end, t);
      }
    }
    i = k;
  }
  // 단어 끝은 다음 단어 시작을 넘지 않게
  for (let i = 0; i < words.length - 1; i++) words[i].end = Math.min(words[i].end, words[i + 1].start);

  return {
    words: words.map((w) => ({ text: w.text, start: round3(w.start), end: round3(w.end) })),
    matchRatio: n ? matches / n : 1,
    recognized: tokens.map((t) => t.text).join("").trim(),
  };
}
