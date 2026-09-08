import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";
import Taegukgi from "./taegukgi";

// timeline-world · "시간을 달리는" 연대기 월드 (가로 1920×1080)
// 코드 강점: 정확한 연도 레일 + 시대 비네트 + 규정 준수 태극기.
// 하단 1/4 = 연대 레일(660→현재), 중앙 = 시대별 아이콘 비네트.

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const ez = (x: number) => 1 - Math.pow(1 - x, 3);
const at = (t: number, t0: number | undefined, d = 0.9) =>
  t0 === undefined ? 0 : ez(clamp01((t - t0) / d));

export type Era = {
  year: string; label: string; at: number; icon: string;
};

const RAIL_Y = 690;
const X0 = 180, X1 = 1740;

// 시대 아이콘 (심플 SVG 벡터)
const Icon: React.FC<{ kind: string; p: number }> = ({ kind, p }) => {
  const s = { stroke: "#5A4632", strokeWidth: 7, fill: "none", strokeLinecap: "round" as const };
  const common = { opacity: p, transform: `scale(${0.7 + 0.3 * p})`, transformOrigin: "center" };
  switch (kind) {
    case "book": return (
      <g {...common}>
        <path d="M -90 40 Q -90 -50 0 -50 Q 90 -50 90 40 L 90 60 Q 45 40 0 60 Q -45 40 -90 60 Z" fill="#F8F2E0" stroke="#B08A4F" strokeWidth={7} />
        <path d="M 0 -50 L 0 60" {...s} stroke="#B08A4F" />
        <circle cx={0} cy={-72} r={13} fill="#F3C86E" />
      </g>);
    case "helmet": return (
      <g {...common}>
        <path d="M -60 30 Q -60 -60 0 -60 Q 60 -60 60 30 Z" fill="#8E9DAF" stroke="#5A4632" strokeWidth={6} />
        <path d="M 0 -60 L 0 -95" {...s} />
        <circle cx={0} cy={-102} r={9} fill="#D6323C" />
        <rect x={-70} y={30} width={140} height={16} rx={8} fill="#5A4632" />
      </g>);
    case "brush": return (
      <g {...common}>
        <rect x={-8} y={-85} width={16} height={100} rx={8} fill="#B08A4F" />
        <path d="M -14 15 Q 0 55 14 15 Z" fill="#2B2B33" />
        <path d="M -70 60 Q 0 85 70 60" {...s} stroke="#3E7A46" />
        <ellipse cx={52} cy={-30} rx={30} ry={38} fill="#BFD9C9" stroke="#5A4632" strokeWidth={5} />
        <path d="M 30 -52 Q 52 -66 74 -52" {...s} strokeWidth={5} />
      </g>);
    case "ship": return (
      <g {...common}>
        <path d="M -95 20 L 95 20 L 65 65 L -65 65 Z" fill="#B08A4F" stroke="#5A4632" strokeWidth={6} />
        <rect x={-70} y={-15} width={140} height={35} rx={6} fill="#8A6B4D" />
        <path d="M 0 -15 L 0 -80" {...s} />
        <path d="M 0 -80 L 48 -58 L 0 -40 Z" fill="#D6323C" />
        <path d="M -110 72 Q -55 88 0 72 Q 55 56 110 72" {...s} stroke="#5E8FA8" />
      </g>);
    case "horse": return (
      <g {...common}>
        <ellipse cx={-6} cy={14} rx={60} ry={31} fill="#B5713F" />
        <path d="M 36 -2 Q 58 -18 66 -44 L 84 -36 Q 74 -8 52 6 Z" fill="#B5713F" />
        <circle cx={78} cy={-46} r={15} fill="#B5713F" />
        <ellipse cx={94} cy={-42} rx={10} ry={8} fill="#A05F2E" />
        <path d="M 70 -58 L 64 -72 M 82 -58 L 80 -72" stroke="#5A3A1E" strokeWidth={6} strokeLinecap="round" />
        <path d="M 44 -10 Q 58 -30 64 -48" stroke="#5A3A1E" strokeWidth={8} fill="none" strokeLinecap="round" />
        <rect x={-52} y={38} width={13} height={38} rx={6} fill="#8F5A30" />
        <rect x={-20} y={42} width={13} height={36} rx={6} fill="#8F5A30" />
        <rect x={14} y={40} width={13} height={38} rx={6} fill="#8F5A30" />
        <rect x={38} y={36} width={13} height={38} rx={6} fill="#8F5A30" />
        <path d="M -62 8 Q -88 -4 -94 14 Q -82 28 -62 22 Z" fill="#5A3A1E" />
        <rect x={100} y={-38} width={26} height={17} rx={4} fill="#F3F0E8" stroke="#D6323C" strokeWidth={3} />
      </g>);
    case "house": return (
      <g {...common}>
        <path d="M -80 5 L 0 -55 L 80 5 Z" fill="#C9A876" stroke="#5A4632" strokeWidth={6} />
        <rect x={-60} y={5} width={120} height={55} fill="#F3E8D4" stroke="#5A4632" strokeWidth={6} />
        <rect x={-14} y={22} width={28} height={38} fill="#8A6B4D" />
        <path d="M -110 70 Q 0 92 110 70" stroke="#3E7A46" strokeWidth={8} fill="none" strokeLinecap="round" />
      </g>);
    case "flag": return (
      <g {...common}>
        <rect x={-6} y={-95} width={12} height={165} rx={6} fill="#8A6B4D" />
        <g transform="translate(9,-92)">
          <foreignObject width={150} height={100} x={0} y={0}>
            <Taegukgi width={144} />
          </foreignObject>
        </g>
      </g>);
    case "children": return (
      <g {...common}>
        <circle cx={-34} cy={-38} r={22} fill="#F0C6A0" />
        <path d="M -56 30 Q -34 -14 -12 30 Z" fill="#5E8FA8" />
        <circle cx={34} cy={-32} r={20} fill="#F0C6A0" />
        <path d="M 14 32 Q 34 -8 54 32 Z" fill="#D6323C" />
        <path d="M -70 -62 Q 0 -95 70 -58" stroke="#F3C86E" strokeWidth={7} fill="none" strokeLinecap="round" strokeDasharray="2 16" />
      </g>);
    default: return null;
  }
};

export default function TimelineWorld({ eras, focus }: { eras: Era[]; focus: number }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;

  // 현재 초점 시대 인덱스 (Main이 절대 초 배열로 focus 계산해 넘김)
  return (
    <AbsoluteFill style={{ fontFamily: FONT.kr }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {/* 연대 레일 */}
        <line x1={X0} y1={RAIL_Y} x2={X1} y2={RAIL_Y} stroke="#C9BBA4" strokeWidth={6} />
        <line x1={X0} y1={RAIL_Y} x2={X0 + (X1 - X0) * clamp01(focus / Math.max(1, eras.length - 1))}
              y2={RAIL_Y} stroke={C.red} strokeWidth={6}
              style={{ filter: `drop-shadow(0 0 6px ${C.red})` }} />
        {eras.map((e, i) => {
          const x = X0 + ((X1 - X0) * i) / (eras.length - 1);
          const p = at(t, e.at, 0.7);
          const active = i === Math.round(focus);
          return (
            <g key={e.year} opacity={p}>
              <circle cx={x} cy={RAIL_Y} r={active ? 16 : 10}
                      fill={i <= focus ? C.red : "#C9BBA4"} />
            </g>
          );
        })}
      </svg>
      {/* 연도·라벨 (HTML 텍스트) */}
      {eras.map((e, i) => {
        const x = X0 + ((X1 - X0) * i) / (eras.length - 1);
        const p = at(t, e.at, 0.7);
        const active = i === Math.round(focus);
        return (
          <div key={e.year} style={{ position: "absolute", left: x - 100, top: RAIL_Y + 26,
                                     width: 200, textAlign: "center", opacity: p }}>
            <div style={{ fontSize: active ? 44 : 32, fontWeight: 800,
                          color: active ? C.red : "#7A6E5B", transition: "none" }}>{e.year}</div>
            <div style={{ fontSize: 26, fontWeight: 600, color: "#7A6E5B" }}>{e.label}</div>
          </div>
        );
      })}
      {/* 중앙 비네트 — 초점 시대 아이콘 */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {eras.map((e, i) => {
          const isFocus = i === Math.round(focus);
          if (!isFocus) return null;
          const p = at(t, e.at, 0.8);
          return (
            <g key={`icon-${e.year}`} transform="translate(960, 360) scale(2.1)">
              <Icon kind={e.icon} p={p} />
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
}
