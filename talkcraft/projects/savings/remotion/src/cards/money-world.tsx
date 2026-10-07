import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// money-world · 청년미래적금 씬별 스테이지 — 은행 문 → 나이 자 → 동전 기둥 → 달력 → 통장 다리 → 소급 시계 → 알림 폰
// 규칙: 웜 글로우 = 혜택·정답 순서, 빨강 = 마감·잘못된 순서. 숫자는 NumberSlabPop(Main)이 담당.

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
const shake = (t: number, at: number, amp = 7, freq = 26) => {
  const dt = t - at;
  if (dt < 0 || dt > 0.45) return 0;
  return amp * Math.exp(-dt * 9) * Math.sin(dt * freq);
};
const useT = () => {
  const { fps } = useVideoConfig();
  return useCurrentFrame() / fps;
};
const W = 1080;
const GLOW = "0 0 40px rgba(255, 184, 77, 0.45)";

// 동전 기둥 — n개까지 쌓임(progress로 성장), 상단 보너스 묶음 옵션
const CoinStack: React.FC<{ x: number; baseY: number; count: number; p: number; w?: number; bonus?: number; glow?: boolean }> = ({
  x, baseY, count, p, w = 200, bonus = 0, glow = false,
}) => {
  const shown = Math.floor(count * p);
  const H = 26;
  return (
    <>
      {Array.from({ length: shown }).map((_, i) => (
        <div key={i} style={{ position: "absolute", left: x, top: baseY - (i + 1) * H, width: w, height: H - 4,
                              borderRadius: 12, background: i % 2 ? C.clay : C.clayDim,
                              boxShadow: glow ? "0 0 14px rgba(255,184,77,0.25)" : "none" }} />
      ))}
      {bonus > 0 && Array.from({ length: bonus }).map((_, i) => (
        <div key={`b${i}`} style={{ position: "absolute", left: x, top: baseY - (shown + i + 1) * H, width: w, height: H - 4,
                                    borderRadius: 12, background: C.warm, boxShadow: GLOW }} />
      ))}
    </>
  );
};

// s1 은행 문 — 두 판이 열리고 웜 라이트, 인파 점들이 몰려감
export const StageDoors: React.FC = () => {
  const t = useT();
  const openP = tw(t, 0.6, 1.6, power3Out);
  const crowdP = tw(t, 1.2, 3.0, power2Out);
  const doorW = 300, cx = W / 2, top = 360, h = 760;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: cx - doorW, top, width: doorW * 2, height: h, borderRadius: 40,
                    background: `radial-gradient(circle at 50% 45%, rgba(255,184,77,${0.55 * openP}) 0%, rgba(255,184,77,0) 70%)` }} />
      {[-1, 1].map((s) => (
        <div key={s} style={{ position: "absolute", left: cx + (s < 0 ? -doorW : 0), top, width: doorW, height: h,
                              background: C.clayDim, border: `4px solid ${C.clay}`, borderRadius: s < 0 ? "40px 0 0 40px" : "0 40px 40px 0",
                              transformOrigin: s < 0 ? "left center" : "right center",
                              transform: `perspective(1400px) rotateY(${s * -78 * openP}deg)` }} />
      ))}
      {Array.from({ length: 40 }).map((_, i) => {
        const lane = (i * 61) % 900 + 90, delay = (i % 8) * 0.12;
        const pp = clamp01((crowdP * 3.2 - delay) / 2.2);
        if (pp <= 0) return null;
        const y = lerp(1760, 1180, pp), x = lerp(lane, cx + (lane - cx) * 0.25, pp);
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 26, height: 40, borderRadius: 13,
                                     background: C.clay, opacity: 0.9 - pp * 0.5 }} />;
      })}
    </div>
  );
};

// s2 나이 자 — 눈금 자 위 마커, 군복 피규어가 뒤로 밀어줌
export const StageRuler: React.FC<{ pushAt: number }> = ({ pushAt }) => {
  const t = useT();
  const inP = tw(t, 0.1, 0.5, power3Out);
  const pushP = tw(t, pushAt, 0.9, backOut(1.3));
  const y = 1000, x0 = 120, len = 840, ticks = 16;
  const markerX = lerp(x0 + len * 0.82, x0 + len * 0.55, pushP);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: inP }}>
      <div style={{ position: "absolute", left: x0, top: y, width: len, height: 90, borderRadius: 20, background: C.clayDim,
                    border: `3px solid ${C.clay}` }} />
      {Array.from({ length: ticks + 1 }).map((_, i) => (
        <div key={i} style={{ position: "absolute", left: x0 + (len / ticks) * i, top: y + 8, width: 4,
                              height: i % 4 === 0 ? 40 : 22, background: C.text, opacity: 0.55 }} />
      ))}
      <div style={{ position: "absolute", left: markerX - 34, top: y - 60, width: 68, height: 68, borderRadius: 34,
                    background: C.warm, boxShadow: GLOW, transform: `translateX(${shake(t, pushAt + 0.9, 5)}px)` }} />
      <div style={{ position: "absolute", left: markerX + 50, top: y - 130, fontSize: 96, opacity: tw(t, pushAt - 0.4, 0.3, power2Out),
                    transform: `translateX(${lerp(60, 0, pushP)}px)` }}>🪖</div>
    </div>
  );
};

// s3 동전 기둥 + 정부 손 보너스 + 튕기는 도장
export const StageCoins: React.FC<{ bonusAt: number; stampAt: number }> = ({ bonusAt, stampAt }) => {
  const t = useT();
  const growP = tw(t, 0.2, 2.4, power2Out);
  const bonusP = tw(t, bonusAt, 0.6, backOut(1.6));
  const stampP = tw(t, stampAt, 0.5, power2Out);
  const stampX = stampP < 0.5 ? lerp(-260, 250, stampP * 2) : lerp(250, -320, (stampP - 0.5) * 2);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: 340, top: 1240, width: 400, height: 60, borderRadius: 30, background: C.clayDim }} />
      <CoinStack x={440} baseY={1246} count={18} p={growP} bonus={bonusP > 0 ? Math.round(4 * bonusP) : 0} glow={bonusP > 0.5} />
      {bonusP > 0 && (
        <div style={{ position: "absolute", left: 470, top: lerp(300, 560, bonusP), fontSize: 140, opacity: bonusP }}>🫴</div>
      )}
      {stampP > 0 && stampP < 1 && (
        <div style={{ position: "absolute", left: 540 + stampX, top: 900, width: 120, height: 120, borderRadius: 60,
                      background: C.red, opacity: 0.85, transform: `rotate(${stampP * 360}deg)` }} />
      )}
    </div>
  );
};

// s4 두 더미 — 우대형이 두 배로 자라며 글로우
export const StageDouble: React.FC<{ growAt: number }> = ({ growAt }) => {
  const t = useT();
  const baseP = tw(t, 0.2, 1.2, power2Out);
  const growP = tw(t, growAt, 1.4, power3Out);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: 120, top: 1240, width: 840, height: 60, borderRadius: 30, background: C.clayDim }} />
      <CoinStack x={210} baseY={1246} count={9} p={baseP} />
      <CoinStack x={650} baseY={1246} count={18} p={Math.max(baseP * 0.5, growP)} glow={growP > 0.3} />
      <div style={{ position: "absolute", left: 620, top: 620, width: 260, height: 660, borderRadius: 40,
                    boxShadow: growP > 0.3 ? GLOW : "none", opacity: growP }} />
    </div>
  );
};

// s5 달력 타일 3장 — 순차 팝, 마지막만 빨간 테두리
export const StageCalendar: React.FC<{ ats: number[]; redAt: number }> = ({ ats, redAt }) => {
  const t = useT();
  const redP = tw(t, redAt, 0.4, power2Out);
  const labels = ["홀", "짝", "누구나"];
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      {ats.map((at, i) => {
        const p = tw(t, at, 0.34, backOut(1.9));
        if (p <= 0) return null;
        const isLast = i === 2;
        return (
          <div key={i} style={{ position: "absolute", left: 90 + i * 310, top: 700, width: 280, height: 360, borderRadius: 34,
                                background: C.bgPanel, border: `4px solid ${isLast && redP > 0 ? C.red : C.clay}`,
                                boxShadow: isLast && redP > 0 ? `0 0 ${40 * redP}px ${C.red}` : "none",
                                opacity: p, transform: `translateY(${lerp(-60, 0, p)}px) scale(${lerp(0.7, 1, p)}) translateX(${shake(t, at + 0.34, 4)}px)`,
                                display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 20 }}>
            <div style={{ width: 200, height: 40, borderRadius: 12, background: C.clayDim }} />
            <div style={{ fontFamily: FONT.kr, fontWeight: 800, fontSize: isLast ? 56 : 88, color: isLast && redP > 0 ? C.red : C.text }}>
              {labels[i]}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// s6 두 통장 + 다리 — 새 통장 먼저(글로우) → 옛 통장 슬롯, 역순엔 빨간 X
export const StageBridge: React.FC<{ crossAt: number; closeAt: number }> = ({ crossAt, closeAt }) => {
  const t = useT();
  const inP = tw(t, 0.1, 0.5, power3Out);
  const crossP = tw(t, crossAt, 1.2, power2Out);
  const closeP = tw(t, closeAt, 0.8, power3Out);
  const Book: React.FC<{ x: number; y: number; glow?: boolean; sink?: number }> = ({ x, y, glow, sink = 0 }) => (
    <div style={{ position: "absolute", left: x, top: y + sink, width: 260, height: 340, borderRadius: 26,
                  background: C.bgPanel, border: `4px solid ${glow ? C.warm : C.clay}`, boxShadow: glow ? GLOW : "none",
                  clipPath: sink > 0 ? `inset(0 0 ${sink}px 0)` : undefined }}>
      {[0, 1, 2].map((i) => <div key={i} style={{ margin: "40px 30px 0", height: 14, borderRadius: 7, background: C.clayDim, width: 140 - i * 30 }} />)}
    </div>
  );
  return (
    <div style={{ position: "absolute", inset: 0, opacity: inP }}>
      <div style={{ position: "absolute", left: 80, top: 1180, width: 380, height: 50, borderRadius: 25, background: C.clayDim }} />
      <div style={{ position: "absolute", left: 620, top: 1180, width: 380, height: 50, borderRadius: 25, background: C.clayDim }} />
      <div style={{ position: "absolute", left: 440, top: 1195, width: 200, height: 20, borderRadius: 10, background: C.clay }} />
      <Book x={140} y={820} sink={closeP * 300} />
      <Book x={680} y={820} glow={crossP > 0.7} />
      <div style={{ position: "absolute", left: lerp(300, 700, crossP), top: 1050, width: 60, height: 120, borderRadius: 30, background: C.clay }} />
      {closeP > 0.5 && (
        <div style={{ position: "absolute", left: 500, top: 1080, fontSize: 90, color: C.red, fontWeight: 800, opacity: (closeP - 0.5) * 2,
                      textShadow: `0 0 24px ${C.red}` }}>✕</div>
      )}
    </div>
  );
};

// s7 화살표 성장 + 되감기는 시계
export const StageRetro: React.FC<{ growAt: number }> = ({ growAt }) => {
  const t = useT();
  const stackP = tw(t, 0.2, 1.0, power2Out);
  const arrowP = tw(t, growAt, 1.6, power3Out);
  const angle = -t * 200;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: 120, top: 1240, width: 500, height: 60, borderRadius: 30, background: C.clayDim }} />
      <CoinStack x={270} baseY={1246} count={12} p={stackP} glow={arrowP > 0.2} />
      <div style={{ position: "absolute", left: 356, top: lerp(930, 470, arrowP), width: 28, height: lerp(0, 460, arrowP), borderRadius: 14, background: C.warm, boxShadow: GLOW }} />
      <div style={{ position: "absolute", left: 320, top: lerp(930, 470, arrowP) - 50, width: 0, height: 0, opacity: arrowP,
                    borderLeft: "50px solid transparent", borderRight: "50px solid transparent", borderBottom: `70px solid ${C.warm}`, filter: "drop-shadow(0 0 16px rgba(255,184,77,0.6))" }} />
      <div style={{ position: "absolute", left: 660, top: 760, width: 300, height: 300, borderRadius: 150, border: `10px solid ${C.clay}`, background: C.bgPanel }}>
        <div style={{ position: "absolute", left: 140, top: 40, width: 12, height: 110, borderRadius: 6, background: C.text, transformOrigin: "50% 100%", transform: `rotate(${angle}deg)` }} />
        <div style={{ position: "absolute", left: 140, top: 70, width: 12, height: 80, borderRadius: 6, background: C.clay, transformOrigin: "50% 100%", transform: `rotate(${angle / 12}deg)` }} />
      </div>
    </div>
  );
};

// s8 알림 폰 + 홀/짝 카드
export const StagePhone: React.FC<{ cardsAt: number }> = ({ cardsAt }) => {
  const t = useT();
  const inP = tw(t, 0.1, 0.5, power3Out);
  const bell = 0.6 + 0.4 * Math.abs(Math.sin(t * 3));
  return (
    <div style={{ position: "absolute", inset: 0, opacity: inP }}>
      <div style={{ position: "absolute", left: 370, top: 560, width: 340, height: 680, borderRadius: 50, background: C.bgPanel, border: `5px solid ${C.clay}`,
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 150, filter: `drop-shadow(0 0 ${30 * bell}px rgba(255,184,77,0.7))` }}>🔔</div>
      {["홀수생", "짝수생"].map((lab, i) => {
        const p = tw(t, cardsAt + i * 0.25, 0.4, backOut(1.8));
        if (p <= 0) return null;
        return (
          <div key={i} style={{ position: "absolute", left: i === 0 ? 60 : 760, top: 800, width: 260, height: 200, borderRadius: 30,
                                background: C.bgPanel, border: `4px solid ${C.warm}`, boxShadow: GLOW, opacity: p,
                                transform: `translateY(${lerp(80, 0, p)}px) scale(${lerp(0.7, 1, p)})`,
                                display: "flex", alignItems: "center", justifyContent: "center",
                                fontFamily: FONT.kr, fontWeight: 800, fontSize: 64, color: C.text }}>{lab}</div>
        );
      })}
    </div>
  );
};
