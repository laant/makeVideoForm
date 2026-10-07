import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// dimension-counter · 빨간 계측선이 자라며 숫자가 카운트되는 카드 (건축쇼츠 계측선 규칙의 코드 구현)
// 규칙: 계측선은 명확한 수치가 있을 때만 — 이 카드 자체가 그 수치를 잰다.
// 동효: 0.3s 리드 → 선이 power3.out으로 신장 + 숫자 트윈 → 落定 화살촉 펀치 → 라벨 페이드.

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const tw = (t: number, t0: number, d: number, ease: (x: number) => number) =>
  ease(clamp01((t - t0) / d));
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const power2Out = (x: number) => 1 - Math.pow(1 - x, 3);
const power3Out = (x: number) => 1 - Math.pow(1 - x, 4);

export default function DimensionCounter({
  target = 50, unit = "m", prefix = "지하", label = "거대한 신전이 숨어 있습니다",
  growDur = 1.4, lineLen = 760, instant = false, decimals = 0,
}: {
  target?: number; unit?: string; prefix?: string; label?: string;
  growDur?: number; lineLen?: number; instant?: boolean; decimals?: number;
}) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;
  const p = instant ? 1 : tw(t, 0.3, growDur, power3Out);
  const value = lerp(0, target, p);
  const labelP = instant ? 1 : tw(t, 0.3 + growDur, 0.4, power2Out);
  const len = lineLen * p;
  const cx = 540;
  const top = (1920 - lineLen) / 2 - 60;

  const arrow = (y: number, dir: 1 | -1) => (
    <polygon
      points={`${cx},${y} ${cx - 13},${y + 22 * dir} ${cx + 13},${y + 22 * dir}`}
      fill={C.red}
    />
  );

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT.kr }}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {/* 보조선(고정): 상단 지표 / 하단 도달점 */}
        <line x1={cx - 190} y1={top} x2={cx + 190} y2={top}
              stroke={C.red} strokeWidth={3} opacity={0.9} />
        <line x1={cx - 190} y1={top + len} x2={cx + 190} y2={top + len}
              stroke={C.red} strokeWidth={3} opacity={0.9 * Math.min(1, p * 3)} />
        {/* 치수선(신장) + 화살촉 */}
        <line x1={cx} y1={top + 8} x2={cx} y2={top + len - 8}
              stroke={C.red} strokeWidth={4}
              style={{ filter: `drop-shadow(0 0 8px ${C.red})` }} />
        {p > 0.05 && arrow(top + 4, 1)}
        {p > 0.5 && arrow(top + len - 4, -1)}
      </svg>
      <div style={{ position: "absolute", top: top + lineLen * 0.42, left: cx + 60,
                    textAlign: "left" }}>
        <div style={{ fontSize: 42, fontWeight: 600, color: C.dim, opacity: labelP }}>
          {prefix}
        </div>
        <div style={{ fontSize: 130, fontWeight: 800, color: C.text, lineHeight: 1.05,
                      fontVariantNumeric: "tabular-nums" }}>
          {value.toFixed(decimals)}
          <span style={{ fontSize: 64, color: C.red, marginLeft: 8 }}>{unit}</span>
        </div>
        <div style={{ fontSize: 38, fontWeight: 600, color: C.dim, marginTop: 14,
                      opacity: labelP, transform: `translateY(${(1 - labelP) * 12}px)` }}>
          {label}
        </div>
      </div>
    </AbsoluteFill>
  );
}
