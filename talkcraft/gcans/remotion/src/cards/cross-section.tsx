import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";

// cross-section · G-Cans 단면도 월드 (s3~s11 롱테이크의 무대)
// 레퍼런스(한강 수중보)의 "수면 단면 잘라 보여주기" 문법을 SVG 코드로 구현.
// 스테이지는 절대 초 앵커(props)로 열림 — 열린 요소는 이후 상주 (월드 캔버스 원칙).

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const ez = (x: number) => 1 - Math.pow(1 - x, 3);
const at = (t: number, t0: number, d = 0.8) => (t0 < 0 ? 0 : ez(clamp01((t - t0) / d)));

export type CrossSectionStages = {
  waterRiseAt?: number;   // s3 범람
  densifyAt?: number;     // s4 건물 밀집
  shaftAt?: number;       // s5 수직갱+터널 굴착
  riversAt?: number;      // s6 강 5개 물줄기
  plungeAt?: number;      // s7 낙수+파문
  pillarsAt?: number;     // s8 기둥 감쇠
  turbinesAt?: number;    // s9 터빈 배출
  calmAt?: number;        // s11 지상만 남기고 침묵
};

const SURF = 520;          // 지표 y
const SHAFT_X = 500;       // 수직갱 중심 x
const TUN_Y = 1150;        // 터널 중심 y

export default function CrossSection({ stages, dimNow }: {
  stages: CrossSectionStages; dimNow?: boolean;
}) {
  const { fps } = useVideoConfig();
  const tAbs = useCurrentFrame() / fps; // Sequence 내부 상대 초 — Main에서 앵커를 상대화해서 넘김
  const s = stages;
  const rise = at(tAbs, s.waterRiseAt ?? -1, 1.6);
  const dense = at(tAbs, s.densifyAt ?? -1, 1.0);
  const dig = at(tAbs, s.shaftAt ?? -1, 1.4);
  const rivers = at(tAbs, s.riversAt ?? -1, 1.2);
  const plunge = at(tAbs, s.plungeAt ?? -1, 0.9);
  const pillars = at(tAbs, s.pillarsAt ?? -1, 1.0);
  const turb = at(tAbs, s.turbinesAt ?? -1, 1.0);
  const calm = at(tAbs, s.calmAt ?? -1, 1.2);
  const spin = tAbs * 260; // 터빈 회전각

  // 범람 수위: 강 기준 위로 차오름 → 배수 단계(turbines)에서 다시 내려감
  const flood = rise * (1 - 0.85 * turb) * (1 - calm);
  const undergroundDim = 1 - 0.75 * calm;

  const houses: React.ReactNode[] = [];
  const baseN = 8, extraN = 10;
  for (let i = 0; i < baseN + Math.round(extraN * dense); i++) {
    const x = 130 + ((i * 89) % 830);
    if (Math.abs(x - SHAFT_X) < 55) continue;
    const h = 34 + ((i * 37) % 40);
    houses.push(<rect key={`h${i}`} x={x} y={SURF - h} width={46} height={h} rx={4}
                      fill={C.concrete} opacity={0.85} />);
  }

  const riverXs = [210, 360, 640, 790, 900];

  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {/* 지층 단면 */}
        <rect x={60} y={SURF} width={960} height={800} fill={C.soil} opacity={0.32 * undergroundDim} />
        <rect x={60} y={SURF} width={960} height={800} fill="url(#soilGrad)" opacity={undergroundDim} />
        <defs>
          <linearGradient id="soilGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#5A452F" stopOpacity={0.55} />
            <stop offset="100%" stopColor="#241A10" stopOpacity={0.75} />
          </linearGradient>
        </defs>
        {/* 지표선 + 강(중앙 저지대) */}
        <line x1={60} y1={SURF} x2={1020} y2={SURF} stroke={C.concrete} strokeWidth={5} />
        <path d={`M 430 ${SURF} q 110 46 220 0`} fill="none" stroke={C.teal} strokeWidth={7} />
        {/* 범람 수막 */}
        {flood > 0.01 && (
          <rect x={90} y={SURF - 52 * flood} width={900} height={52 * flood}
                fill={C.teal} opacity={0.5} />
        )}
        {houses}
        {/* 수직갱 + 터널 (굴착 진행) */}
        {dig > 0.01 && (<>
          <rect x={SHAFT_X - 34} y={SURF} width={68} height={(TUN_Y - 80 - SURF) * dig}
                fill="#10161E" stroke={C.concrete} strokeWidth={4} />
          {dig > 0.75 && (
            <rect x={150} y={TUN_Y - 80} width={780 * ez(clamp01((dig - 0.75) / 0.25))}
                  height={160} rx={80} fill="#10161E" stroke={C.concrete} strokeWidth={5} />
          )}
        </>)}
        {/* 강 5개 → 물줄기 */}
        {rivers > 0.01 && riverXs.map((x, i) => {
          const p = ez(clamp01(rivers * 5 - i));
          return (<g key={`r${i}`} opacity={p}>
            <circle cx={x} cy={SURF - 8} r={13} fill={C.teal} />
            <line x1={x} y1={SURF} x2={x} y2={SURF + (TUN_Y - 90 - SURF) * p}
                  stroke={C.teal} strokeWidth={6} opacity={0.75} strokeDasharray="14 20"
                  strokeDashoffset={-tAbs * 160} />
          </g>);
        })}
        {/* 낙수 기둥 + 파문 */}
        {plunge > 0.01 && (<>
          <rect x={SHAFT_X - 22} y={SURF + 6} width={44} height={(TUN_Y - 110 - SURF) * plunge}
                fill={C.teal} opacity={0.9} />
          {[0, 1, 2].map((i) => {
            const rp = clamp01((tAbs - (s.plungeAt ?? 0) - 0.5 - i * 0.5) / 1.2 % 1);
            return <ellipse key={`w${i}`} cx={SHAFT_X} cy={TUN_Y}
                            rx={60 + 240 * rp} ry={16 + 34 * rp}
                            fill="none" stroke={C.teal} strokeWidth={5} opacity={(1 - rp) * 0.8} />;
          })}
        </>)}
        {/* 터널 속 기둥 열 (물의 기세를 죽임) */}
        {pillars > 0.01 && [0, 1, 2, 3, 4, 5, 6].map((i) => {
          const p = ez(clamp01(pillars * 7 - i));
          const x = 250 + i * 90;
          return <rect key={`p${i}`} x={x} y={TUN_Y + 62 - 124 * p} width={26} height={124 * p}
                       fill={C.concrete} opacity={0.95} />;
        })}
        {/* 터빈 4대 + 배출 화살표 */}
        {turb > 0.01 && (<g opacity={turb}>
          {[0, 1, 2, 3].map((i) => {
            const cx = 795 + (i % 2) * 78, cy = TUN_Y - 26 + Math.floor(i / 2) * 62;
            return (<g key={`t${i}`} transform={`translate(${cx},${cy})`}>
              <circle r={26} fill="none" stroke={C.concrete} strokeWidth={5} />
              <g transform={`rotate(${spin + i * 45})`}>
                <line x1={-20} y1={0} x2={20} y2={0} stroke={C.teal} strokeWidth={6} />
                <line x1={0} y1={-20} x2={0} y2={20} stroke={C.teal} strokeWidth={6} />
              </g>
            </g>);
          })}
          <path d={`M 930 ${TUN_Y} L 1000 ${TUN_Y}`} stroke={C.teal} strokeWidth={9}
                markerEnd="url(#arr)" />
          <defs>
            <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 z" fill={C.teal} />
            </marker>
          </defs>
        </g>)}
        {/* s11 — 지상 축구장 골대 */}
        {calm > 0.01 && (<g opacity={calm}>
          <line x1={420} y1={SURF - 4} x2={420} y2={SURF - 64} stroke={C.text} strokeWidth={6} />
          <line x1={640} y1={SURF - 4} x2={640} y2={SURF - 64} stroke={C.text} strokeWidth={6} />
          <line x1={420} y1={SURF - 64} x2={640} y2={SURF - 64} stroke={C.text} strokeWidth={6} />
          <line x1={90} y1={SURF - 2} x2={990} y2={SURF - 2} stroke="#3E7A46" strokeWidth={8} />
        </g>)}
      </svg>
    </AbsoluteFill>
  );
}
