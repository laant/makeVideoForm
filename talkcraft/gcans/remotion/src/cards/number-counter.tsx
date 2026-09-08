import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// number-counter · 数字滚动计数 —— template/cards/number-counter.tsx 복사·개조
// 개조: 데모 문맥(백색+호스트 분할)을 본편 다크 캔버스 중앙 배치로, 값/포맷을 "10.3조 원"으로.
// 동효 본체(트윈 카운트 → 落定 스케일 펀치 → 단위 지연 페이드)는 원본 유지.
export const meta = { width: 1080, height: 1920, fps: 30, durationInFrames: 300 };

// —— 可摘走的核心动画参数：a) tween 计数 + 落定弹一拍 ——
const CONFIG = {
  target: 10.3,      // 목표값 (조 단위)
  countDur: 1.3,     // 计数时长 s：1~1.5 先快后慢；>2s 观众已经听完这句了
  landScale: 1.08,   // 落定瞬间的放大一拍
  lead: 0.3,
};

/* 时间表（카드 내 상대 초）
   0.30–1.60  모드 a 카운트 0→target（power3.out）
   1.60–1.69  落定 放大 1.08（power2.out）
   1.69–1.87  回弹 1（back.out(3)）
   1.69–1.94  단위·캡션 淡入上移（power2.out） */

// —— 缓动与 tween helper（对照 GSAP 名字）——
const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const tw = (t: number, t0: number, d: number, ease: (x: number) => number) =>
  ease(clamp01((t - t0) / d));
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const power2Out = (x: number) => 1 - Math.pow(1 - x, 3);
const power3Out = (x: number) => 1 - Math.pow(1 - x, 4);
const backOut = (s = 1.70158) => (x: number) => {
  const u = x - 1;
  return 1 + (s + 1) * u * u * u + s * u * u;
};

const fmt = (n: number) => n.toFixed(1);

export default function NumberCounter({
  label = "주인 없는 숨은 보험금",
  caption = "2025년 말 기준 · 금융위원회",
  instant = false, // S6 루프 재등장용: 카운트 생략, 落定 상태로 즉시
}: { label?: string; caption?: string; instant?: boolean }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;

  // 모드 a：0 → 目标，easeOut 先快后慢
  const value = instant
    ? CONFIG.target
    : lerp(0, CONFIG.target, tw(t, CONFIG.lead, CONFIG.countDur, power3Out));
  const landAt = instant ? CONFIG.lead : 1.6;
  // 落定瞬间：轻放大一拍 + 回弹
  const scale = t < landAt + 0.09
    ? lerp(1, CONFIG.landScale, tw(t, landAt, 0.09, power2Out))
    : lerp(CONFIG.landScale, 1, tw(t, landAt + 0.09, 0.18, backOut(3)));
  // 단위/캡션 淡入（落定 보상）
  const deltaP = tw(t, landAt + 0.09, 0.25, power2Out);
  const inP = tw(t, 0, 0.35, power2Out);

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT.kr }}>
      <div style={{ textAlign: "center", opacity: inP, transform: `translateY(${lerp(24, 0, inP)}px)` }}>
        <div style={{ fontSize: 44, fontWeight: 600, color: C.dim, letterSpacing: 6, marginBottom: 30 }}>
          {label}
        </div>
        <div style={{
          display: "flex", alignItems: "baseline", justifyContent: "center", gap: 14,
          whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums",
          transform: `scale(${scale})`, transformOrigin: "50% 80%",
        }}>
          <span style={{ fontSize: 210, fontWeight: 800, color: C.gold, letterSpacing: -4, lineHeight: 1 }}>
            {fmt(value)}
          </span>
          <span style={{ fontSize: 110, fontWeight: 800, color: C.text }}>조</span>
          <span style={{ fontSize: 64, fontWeight: 600, color: C.dim, opacity: deltaP,
                         transform: `translateY(${lerp(8, 0, deltaP)}px)`, display: "inline-block" }}>
            원
          </span>
        </div>
        <div style={{ fontSize: 30, color: C.dim, letterSpacing: 3, marginTop: 34, opacity: deltaP }}>
          {caption}
        </div>
      </div>
    </AbsoluteFill>
  );
}
