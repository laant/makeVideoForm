import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";
import Taegukgi from "./taegukgi";

// paper-city · 구리시 페이퍼 디오라마 월드 (전편 롱테이크 무대)
// 종이 콜라주 문법을 SVG로: 크림 탁상 위 도시 스트립 + 강변북로 + 종이 자동차 +
// 두 게양대(계측선은 수치 발화 앵커에서 깃대와 함께 자람 — 규칙: 수치 컷만).

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const ez = (x: number) => 1 - Math.pow(1 - x, 3);
const at = (t: number, t0: number | undefined, d = 0.9) =>
  t0 === undefined || t0 < 0 ? 0 : ez(clamp01((t - t0) / d));

export type PaperStages = {
  xAt?: number;        // s3 빈 베란다 X
  parkAt?: number;     // s4 공원 펼침
  pole1At?: number;    // s5 50m 게양대(+계측선)
  mtOpenAt?: number;   // s6 아차산 단면 펼침
  pole2At?: number;    // s7 75m 게양대(+계측선)
  compareAt?: number;  // s8 깃발 vs 배구코트
  compareEnd?: number;
  dominoAt?: number;   // s11 거리 태극기 도미노
  warmAt?: number;     // s12 온광 마무리
};

const GROUND = 1265;
const P1X = 350, P1TOP = 640;   // 50m 깃대
const P2X = 830, P2BASE = 1080, P2TOP = 430; // 75m 깃대(산)

export default function PaperCity({ stages }: { stages: PaperStages }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;
  const s = stages;
  const xs = at(t, s.xAt, 1.2);
  const park = at(t, s.parkAt, 1.1);
  const p1 = at(t, s.pole1At, 1.6);
  const mt = at(t, s.mtOpenAt, 1.2);
  const p2 = at(t, s.pole2At, 1.8);
  const cmpIn = at(t, s.compareAt, 0.9);
  const cmp = s.compareEnd !== undefined && t > s.compareEnd ? 0 : cmpIn;
  const dom = at(t, s.dominoAt, 1.6);
  const warm = at(t, s.warmAt, 1.5);
  const carX = 140 + ((t * 95) % 900);
  const flutter = Math.sin(t * 2.2) * 2.2;

  const bld = (x: number, w: number, h: number, fill: string, k: string) => (
    <g key={k}>
      <rect x={x} y={GROUND - h} width={w} height={h} rx={5} fill={fill}
            stroke="rgba(43,43,51,0.12)" strokeWidth={2} />
      <rect x={x + 6} y={GROUND - h + 8} width={w - 12} height={10} fill="rgba(255,255,255,0.5)" />
    </g>
  );

  const dimLine = (x: number, yBot: number, yTopFull: number, p: number, key: string) => {
    if (p <= 0.01) return null;
    const yTop = yBot - (yBot - yTopFull) * p;
    return (
      <g key={key} style={{ filter: `drop-shadow(0 0 7px ${C.red})` }}>
        <line x1={x - 55} y1={yBot} x2={x + 55} y2={yBot} stroke={C.red} strokeWidth={4} />
        <line x1={x - 55} y1={yTop} x2={x + 55} y2={yTop} stroke={C.red} strokeWidth={4} />
        <line x1={x} y1={yBot - 6} x2={x} y2={yTop + 6} stroke={C.red} strokeWidth={4} />
        <polygon points={`${x},${yTop} ${x - 10},${yTop + 17} ${x + 10},${yTop + 17}`} fill={C.red} />
        <polygon points={`${x},${yBot} ${x - 10},${yBot - 17} ${x + 10},${yBot - 17}`} fill={C.red} />
      </g>
    );
  };

  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {/* 탁상 그림자 + 강 + 강변북로 */}
        <ellipse cx={540} cy={GROUND + 130} rx={480} ry={46} fill="rgba(43,43,51,0.08)" />
        <rect x={40} y={GROUND + 66} width={1000} height={40} rx={20} fill="#A9CBE8" />
        <rect x={40} y={GROUND + 18} width={1000} height={34} rx={17} fill="#B9B2A6" />
        <rect x={40} y={GROUND + 32} width={1000} height={4} fill="rgba(255,255,255,0.8)" strokeDasharray="30 24" />
        {/* 도시 스트립 */}
        {bld(110, 90, 150, "#EAD9C2", "b1")}
        {bld(215, 74, 200, "#DCCBB2", "b2")}
        {bld(470, 96, 176, "#E6D2BE", "b3")}
        {bld(580, 80, 226, "#D8C6AE", "b4")}
        {bld(676, 70, 130, "#EAD9C2", "b5")}
        {/* 아파트 3동 (X 스티커 대상) */}
        {[0, 1, 2].map((i) => bld(255 + i * 66, 54, 300, "#E2D0BA", `apt${i}`))}
        {xs > 0.01 && [0, 1, 2, 3, 4, 5].map((i) => {
          const p = ez(clamp01(xs * 6 - i));
          const x = 268 + (i % 3) * 66, y = GROUND - 274 + Math.floor(i / 3) * 90;
          return (
            <g key={`x${i}`} opacity={p} transform={`translate(${x},${y}) scale(${0.6 + 0.4 * p})`}>
              <line x1={-13} y1={-13} x2={13} y2={13} stroke={C.red} strokeWidth={7} strokeLinecap="round" />
              <line x1={13} y1={-13} x2={-13} y2={13} stroke={C.red} strokeWidth={7} strokeLinecap="round" />
            </g>
          );
        })}
        {/* 공원 (s4) */}
        {park > 0.01 && (<g opacity={park}>
          <rect x={210} y={GROUND - 14} width={300} height={16} rx={8} fill={C.green} opacity={0.65} />
          {[0, 1, 2].map((i) => (
            <g key={`tr${i}`} transform={`translate(${250 + i * 100},${GROUND - 18}) scale(${park})`}>
              <rect x={-4} y={-18} width={8} height={18} fill="#8A6B4D" />
              <circle cx={0} cy={-30} r={20} fill={C.green} />
            </g>
          ))}
          <rect x={P1X - 22} y={GROUND - 12} width={44} height={12} rx={6} fill="#B9B2A6" />
        </g>)}
        {/* 아차산 (우측, s6에 단면 펼침) */}
        <g>
          <polygon points={`700,${GROUND} 1050,${GROUND} ${P2X + 45},960`} fill={C.green} opacity={0.9} />
          {mt > 0.01 && (<g opacity={mt}>
            <polygon points={`760,${GROUND} 1010,${GROUND} ${P2X + 40},1005`} fill="#C9A876" />
            {[0, 1, 2].map((i) => (
              <line key={`ly${i}`} x1={790 + i * 14} y1={GROUND - i * 55 - 40} x2={990 - i * 20} y2={GROUND - i * 55 - 40}
                    stroke="#8A6B4D" strokeWidth={5} opacity={0.7} />
            ))}
            {[0, 1, 2].map((i) => (
              <rect key={`ft${i}`} x={856 + i * 36} y={1052 - i * 7} width={26} height={16} rx={3} fill="#B9B2A6" />
            ))}
          </g>)}
        </g>
        {/* 게양대 1 — 50m (s5) */}
        {p1 > 0.01 && (<g>
          <rect x={P1X - 7} y={GROUND - 10 - (GROUND - 10 - P1TOP) * p1} width={14}
                height={(GROUND - 10 - P1TOP) * p1} rx={6} fill="#9C9484" />
          {dimLine(P1X + 120, GROUND - 10, P1TOP, p1, "d1")}
        </g>)}
        {/* 게양대 2 — 75m (s7) */}
        {p2 > 0.01 && (<g>
          <rect x={P2X - 8} y={P2BASE - (P2BASE - P2TOP) * p2} width={16}
                height={(P2BASE - P2TOP) * p2} rx={7} fill="#9C9484" />
          {dimLine(P2X + 130, P2BASE, P2TOP, p2, "d2")}
        </g>)}
        {/* s8 비교: 큰 깃발 아래 배구코트 카드 */}
        {cmp > 0.01 && (<g opacity={cmp}>
          <rect x={270} y={505} width={540} height={368} rx={10} fill="#F3C86E"
                stroke="#C79A3B" strokeWidth={4} />
          <line x1={540} y1={505} x2={540} y2={873} stroke="#C79A3B" strokeWidth={4} />
          <rect x={270} y={505} width={540} height={368} fill="none" />
        </g>)}
        {/* 거리 도미노 태극기 (s11) */}
        {dom > 0.01 && [0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
          const p = ez(clamp01(dom * 8 - i));
          const x = 120 + i * 118;
          return (
            <g key={`df${i}`} opacity={p} transform={`translate(${x},${GROUND + 16}) scale(${p})`}>
              <line x1={0} y1={0} x2={0} y2={-66} stroke="#9C9484" strokeWidth={5} />
              <g transform={`translate(1,-66)`}>
                <foreignObject width={54} height={36} x={0} y={0}>
                  <div style={{ transform: "scale(1)" }}><Taegukgi width={54} /></div>
                </foreignObject>
              </g>
            </g>
          );
        })}
        {/* 종이 자동차 (상시 순환) */}
        <g transform={`translate(${carX},${GROUND + 20})`}>
          <rect x={-34} y={-26} width={68} height={22} rx={9} fill={C.red} opacity={0.92} />
          <rect x={-18} y={-40} width={34} height={17} rx={7} fill="#F3E8D4" />
          <circle cx={-18} cy={-2} r={9} fill="#2B2B33" />
          <circle cx={18} cy={-2} r={9} fill="#2B2B33" />
        </g>
        {/* 온광 (s12) */}
        {warm > 0.01 && (
          <rect x={0} y={0} width={1080} height={1920} fill="#F7B733" opacity={0.10 * warm} />
        )}
      </svg>
      {/* 깃발들 — SVG 밖 HTML 레이어 (Taegukgi 컴포넌트) */}
      {p1 > 0.55 && (
        <div style={{ position: "absolute", left: P1X + 8, top: P1TOP - 10,
                      transform: `skewY(${flutter}deg)`, transformOrigin: "left center" }}>
          <Taegukgi width={150} wave={flutter} />
        </div>
      )}
      {p2 > 0.55 && (
        <div style={{ position: "absolute", left: P2X + 9, top: P2TOP - 12,
                      transform: `skewY(${-flutter}deg)`, transformOrigin: "left center" }}>
          <Taegukgi width={195} wave={-flutter} />
        </div>
      )}
      {cmp > 0.3 && (
        <div style={{ position: "absolute", left: 250, top: 320, opacity: cmp }}>
          <Taegukgi width={580} wave={flutter * 0.5} />
        </div>
      )}
    </AbsoluteFill>
  );
}
