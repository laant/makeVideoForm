import React from "react";

// taegukgi · 코드로 그린 규정 준수 태극기 — AI 생성이 못 하는 것을 코드가 한다.
// 비율 3:2, 태극 지름 = 세로/2, 태극 축은 대각선, 사괘: 건(상좌)·리(하좌)·감(상우)·곤(하우).
// 괘 막대는 대각선에 수직. width 하나로 스케일.

const R = "#CD2E3A"; // 국기 규정 홍
const B = "#0047A0"; // 국기 규정 청

export default function Taegukgi({ width = 300, wave = 0 }: { width?: number; wave?: number }) {
  const w = width, h = (width * 2) / 3;
  const cx = w / 2, cy = h / 2;
  const r = h / 4;                       // 태극 반지름
  const diag = (Math.atan2(h, w) * 180) / Math.PI; // 대각선 각도 ≈ 33.69°
  const bar = (dx: number, dy: number, len: number, th: number, key: string) => (
    <rect key={key} x={-len / 2 + dx} y={-th / 2 + dy} width={len} height={th} rx={th * 0.15} fill="#000" />
  );
  // 괘 하나: 3줄, split 배열이 true인 줄은 가운데가 끊김
  const trigram = (splits: boolean[], key: string) => {
    const len = r * 1.15, th = r * 0.18, gap = r * 0.30, cutW = th * 0.9;
    return (
      <g key={key}>
        {splits.map((split, i) => {
          const dy = (i - 1) * gap;
          if (!split) return bar(0, dy, len, th, `${key}b${i}`);
          return (
            <g key={`${key}s${i}`}>
              {bar(-(len + cutW) / 4 - cutW / 4, dy, (len - cutW) / 2, th, `${key}l${i}`)}
              {bar((len + cutW) / 4 + cutW / 4, dy, (len - cutW) / 2, th, `${key}r${i}`)}
            </g>
          );
        })}
      </g>
    );
  };
  const d = r * 2.0; // 태극 중심에서 괘 중심까지 거리
  const rad = (Math.PI * diag) / 180;
  const off = { x: Math.cos(rad) * d, y: Math.sin(rad) * d };

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}
         style={{ transform: `skewY(${wave}deg)`, filter: "drop-shadow(1px 2px 2px rgba(0,0,0,0.18))" }}>
      <rect x={0} y={0} width={w} height={h} fill="#fff" stroke="rgba(0,0,0,0.08)" strokeWidth={1} />
      {/* 태극 — 대각선 축, 상홍하청 + 음양 소원 */}
      <g transform={`translate(${cx},${cy}) rotate(${-diag})`}>
        <circle r={r} fill={B} />
        <path d={`M ${-r} 0 A ${r} ${r} 0 0 1 ${r} 0 Z`} fill={R} />
        <circle cx={-r / 2} cy={0} r={r / 2} fill={R} />
        <circle cx={r / 2} cy={0} r={r / 2} fill={B} />
      </g>
      {/* 사괘 — 건(상좌 3통) 곤(하우 6단) 감(상우 中통) 리(하좌 中단) */}
      <g transform={`translate(${cx - off.x},${cy - off.y}) rotate(${-diag})`}>{trigram([false, false, false], "geon")}</g>
      <g transform={`translate(${cx + off.x},${cy + off.y}) rotate(${-diag})`}>{trigram([true, true, true], "gon")}</g>
      <g transform={`translate(${cx + off.x},${cy - off.y}) rotate(${diag})`}>{trigram([true, false, true], "gam")}</g>
      <g transform={`translate(${cx - off.x},${cy + off.y}) rotate(${diag})`}>{trigram([false, true, false], "ri")}</g>
    </svg>
  );
}
