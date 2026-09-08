import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// alt-block-lines · 双色块对句 —— template/cards/alt-block-lines.tsx 복사·개조
// 개조: 데모 문맥(백색+호스트) → 다크 캔버스 중앙 세로 스택, 행별 등장 시점을 단어 앵커로 주입.
// 동효 본체(색블록 scaleX 전개 + 문자 clip-path 2프레임 지연 "쓸어내기")는 원본 유지 — 본 카드 명문.
export const meta = { width: 1080, height: 1920, fps: 30, durationInFrames: 200 };

// ─────────────────────────────────────────────────────────────────────────
// 可摘走的核心动画：双色块对句（块刷出字）
//   ① 色块 scaleX 0→1（origin left，0.26s power3.out）
//   ② 文字 clip-path inset(0 100% 0 0) → inset(0 0% 0 0) 同曲线同时长，起点滞后 2 帧
//   命门：文字必须被块"刷"出来（clip 跟随）。
// ─────────────────────────────────────────────────────────────────────────
const CONFIG = {
  dur: 0.26,        // 单行展开时长 s（块与字共用）
  textLag: 0.067,   // 字相对块的滞后 s（2 帧 @30fps）—— 本卡命门
};

// —— 缓动与 tween helper ——
const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const tw = (t: number, t0: number, d: number, ease: (x: number) => number) =>
  ease(clamp01((t - t0) / d));
const power3Out = (x: number) => 1 - Math.pow(1 - x, 4);
const power2Out = (x: number) => 1 - Math.pow(1 - x, 3);

type Row = { text: string; at: number; accent: boolean };

export default function AltBlockLines({
  title = "댓글로 한 단어만",
  rows = [
    { text: "나왔다", at: 0.3, accent: true },
    { text: "없었다", at: 0.6, accent: false },
  ],
}: { title?: string; rows?: Row[] }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;
  const titleP = tw(t, 0, 0.3, power2Out);

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT.kr }}>
      <div style={{ fontSize: 42, fontWeight: 600, color: C.dim, letterSpacing: 5,
                    marginBottom: 46, opacity: titleP }}>
        {title}
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
        {rows.map((r, i) => {
          // ① 色块从左展开
          const bgP = tw(t, r.at, CONFIG.dur, power3Out);
          // ② 文字被块的右缘刷出来（同曲线同时长，滞后 2 帧）
          const txtP = tw(t, r.at + CONFIG.textLag, CONFIG.dur, power3Out);
          return (
            <span key={i} style={{ position: "relative", display: "inline-block",
                                   padding: "20px 56px 24px" }}>
              <span style={{
                position: "absolute", inset: 0, borderRadius: 10, transformOrigin: "0% 50%",
                background: r.accent ? C.gold : "transparent",
                boxShadow: r.accent ? undefined : `inset 0 0 0 3px ${C.dim}`,
                transform: `scaleX(${bgP})`,
              }} />
              <span style={{
                position: "relative", display: "inline-block", fontSize: 96, fontWeight: 800,
                lineHeight: 1.08, whiteSpace: "nowrap",
                color: r.accent ? C.bg : C.text,
                clipPath: `inset(0 ${(1 - txtP) * 100}% 0 0)`,
              }}>{r.text}</span>
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}
