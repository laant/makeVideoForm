import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// strike-and-replace · 划线纠错替换 —— template/cards/strike-and-replace.tsx 복사·개조
// 개조: 데모 문맥(백색+호스트) → 다크 캔버스 중앙, 한국어 라인, 교체 지연(swapDelay)을
// 단어 앵커 간격("가짜"→"진짜" 발화 간격)으로 prop 주입. 快斩→立换→定格 3박 본체는 원본 유지.
export const meta = { width: 1080, height: 1920, fps: 30, durationInFrames: 360 };

// ─────────────────────────────────────────────────────────────────────────
// 可摘走的核心动画：划线纠错替换（"不是 A，而是 B"）
//   快斩    划掉线 scaleX 0→1，0.15s power3.out（origin left，线高 = 字号 8%）
//   立换    旧值淡出 + 新值从 y+8 同位淡入 0.25s（同位叠放 ⇒ 替换感）
//   定格    划线与新值同屏 hold
// ─────────────────────────────────────────────────────────────────────────
const CONFIG = {
  strikeDur: 0.15,   // 划线时长 s：一瞬间的快斩
  swapDur: 0.25,     // 交换时长 s（旧值淡出 + 新值升入）
  lead: 0.25,        // 起手静置：등장 후 스트라이크까지
  toRise: 8,         // 新值从下方多少 px 升入
  keepStrike: true,  // 划线留在屏上
  from: "가짜",      // 旧值
  to: "진짜",        // 新值
};

// —— 缓动与 tween helper（对照 GSAP 名字）——
const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const tw = (t: number, t0: number, d: number, ease: (x: number) => number) =>
  ease(clamp01((t - t0) / d));
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const power1Out = (x: number) => 1 - Math.pow(1 - x, 2);
const power2Out = (x: number) => 1 - Math.pow(1 - x, 3);
const power3Out = (x: number) => 1 - Math.pow(1 - x, 4);

export default function StrikeAndReplace({
  strikeAt = CONFIG.lead, // 스트라이크 시점 (카드 상대 초) — "가짜" 단어 앵커에서 계산해 주입
  swapDelay = 0.35, // 스트라이크 종료 → 교체 시작 지연 s (단어 앵커 간격에서 계산해 주입)
  subline = "",
  sublineDelay = 0, // 교체 시작 기준 서브라인 지연 s
}: { strikeAt?: number; swapDelay?: number; subline?: string; sublineDelay?: number }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;

  // 등장 (개막 공백 방지: 카드 자체는 s8 초입부터 라인 상주)
  const inP = tw(t, 0, 0.3, power2Out);
  // ① 划线：一瞬间快斩到底
  const strikeX = tw(t, strikeAt, CONFIG.strikeDur, power3Out);
  // ② 交换：旧值淡出、新值从 y+8 淡入回落（同位叠放 ⇒ 替换感）
  const swapAt = strikeAt + CONFIG.strikeDur + swapDelay;
  const fromOpacity = 1 - tw(t, swapAt, CONFIG.swapDur, power1Out);
  const toP = tw(t, swapAt, CONFIG.swapDur, power2Out);
  const toY = lerp(CONFIG.toRise, 0, toP);
  const strikeOpacity = CONFIG.keepStrike ? 1 : fromOpacity;
  const subP = tw(t, swapAt + sublineDelay, 0.3, power2Out);

  // 尺子：from / to 里更长的那一串（换值零位移）
  const longer = CONFIG.from.length >= CONFIG.to.length ? CONFIG.from : CONFIG.to;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT.kr }}>
      <div style={{
        fontSize: 74, fontWeight: 700, lineHeight: 1.5, whiteSpace: "nowrap",
        color: C.text, opacity: inP, transform: `translateY(${lerp(20, 0, inP)}px)`,
      }}>
        비슷한 이름의{" "}
        <span style={{ position: "relative", display: "inline-block", verticalAlign: "baseline" }}>
          <span style={{ visibility: "hidden", whiteSpace: "nowrap" }}>{longer}</span>
          <span style={{ position: "absolute", left: "50%", top: 0, whiteSpace: "nowrap",
                         transform: "translateX(-50%)", opacity: fromOpacity, color: C.text }}>
            {CONFIG.from}
            {/* 划掉线：唯一语义色（적색）。origin left + scaleX 0→1 */}
            <span style={{
              position: "absolute", left: 0, top: "50%", height: 6, width: "100%",
              background: C.red, borderRadius: 3, transformOrigin: "left center",
              opacity: strikeOpacity, transform: `translateY(-50%) scaleX(${strikeX})`,
            }} />
          </span>
          <span style={{ position: "absolute", left: "50%", top: 0, whiteSpace: "nowrap",
                         color: C.gold,
                         transform: `translateX(-50%) translateY(${toY}px)`, opacity: toP }}>
            {CONFIG.to}
          </span>
        </span>{" "}
        사이트
      </div>
      {subline ? (
        <div style={{ marginTop: 46, fontSize: 40, fontWeight: 600, color: C.dim, letterSpacing: 2,
                      opacity: subP, transform: `translateY(${lerp(10, 0, subP)}px)` }}>
          {subline}
        </div>
      ) : null}
    </AbsoluteFill>
  );
}
