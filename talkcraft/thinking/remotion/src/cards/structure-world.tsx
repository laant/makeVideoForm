import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// structure-world · 씬별 스테이지 월드 — 혼돈(장바구니) → 정렬(뼈대 타일) → 구조(에디터)
// 각 스테이지는 씬 Sequence 안에서 마운트되어 로컬 t(초)로 움직인다.
// 타격감 규칙: backOut 팝 + 착지 셰이크, 등장 타이밍은 나레이션 앵커(tSay)와 동기.

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
// 착지 직후 감쇠 진동 (타격감)
const shake = (t: number, at: number, amp = 7, freq = 26) => {
  const dt = t - at;
  if (dt < 0 || dt > 0.45) return 0;
  return amp * Math.exp(-dt * 9) * Math.sin(dt * freq);
};

const useT = () => {
  const { fps } = useVideoConfig();
  return useCurrentFrame() / fps;
};

const WORLD_W = 1080;

// ── 공용 소품 ──────────────────────────────────────────────

// 스크립블 줄 (에디터/채팅 — 글자 대신 회색 바)
const ScribbleLine: React.FC<{ w: number; indent?: number; color?: string; h?: number }> = ({
  w, indent = 0, color = C.clayDim, h = 14,
}) => (
  <div style={{ marginLeft: indent, width: w, height: h, borderRadius: h / 2,
                background: color, marginBottom: 16 }} />
);

// 이질적 물건 (혼돈 유발자) — 이모지 소품
export const ITEMS = ["👟", "🚌", "🏷️", "✏️", "🧾"];

// ── s1 훅: 채팅창 + 스크립블 붙여넣기 + 빨간 X ────────────────
export const StageHook: React.FC<{ xAt: number }> = ({ xAt }) => {
  const t = useT();
  const panelIn = tw(t, 0.05, 0.4, power3Out);
  const pasteIn = tw(t, 0.45, 0.35, backOut(1.4));
  const xIn = tw(t, xAt, 0.22, backOut(2.2));
  const sh = shake(t, xAt + 0.22, 12);
  const lines = [420, 560, 360, 500, 300];
  return (
    <div style={{ position: "absolute", left: 120, top: 260, width: 840,
                  transform: `translateY(${lerp(60, 0, panelIn)}px) translateX(${sh}px)`,
                  opacity: panelIn }}>
      <div style={{ background: C.bgPanel, border: `2px solid ${C.line}`, borderRadius: 28,
                    padding: "44px 48px", boxShadow: "0 24px 60px rgba(0,0,0,0.45)" }}>
        <div style={{ display: "flex", gap: 12, marginBottom: 30 }}>
          {[C.red, C.warm, C.clayDim].map((c, i) => (
            <div key={i} style={{ width: 16, height: 16, borderRadius: 8, background: c, opacity: 0.7 }} />
          ))}
        </div>
        {lines.map((w, i) => <ScribbleLine key={i} w={w} />)}
        <div style={{ marginTop: 26, borderRadius: 18, border: `2px dashed ${C.clay}`,
                      padding: "26px 30px", opacity: pasteIn,
                      transform: `scale(${lerp(0.8, 1, pasteIn)})` }}>
          {[500, 640, 430].map((w, i) => <ScribbleLine key={i} w={w * 0.9} color={C.clay} h={12} />)}
        </div>
      </div>
      {/* 빨간 X — 부정 신호 */}
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center",
                    justifyContent: "center", opacity: xIn,
                    transform: `scale(${lerp(2.2, 1, xIn)}) rotate(${lerp(-14, -4, xIn)}deg)` }}>
        <div style={{ position: "relative", width: 340, height: 340,
                      filter: `drop-shadow(0 0 34px ${C.red})` }}>
          {[45, -45].map((r, i) => (
            <div key={i} style={{ position: "absolute", left: 20, top: 150, width: 300, height: 44,
                                  borderRadius: 22, background: C.red, transform: `rotate(${r}deg)` }} />
          ))}
        </div>
      </div>
    </div>
  );
};

// ── s2 문제a: 장바구니에 물건 쏟아짐 ──────────────────────────
export const StageBasket: React.FC = () => {
  const t = useT();
  const basketIn = tw(t, 0.05, 0.4, power3Out);
  const drops = [0.9, 1.35, 1.8, 2.3, 2.75, 3.3, 3.7, 4.1];
  return (
    <div style={{ position: "absolute", left: 0, top: 240, width: WORLD_W, height: 1100 }}>
      {/* 바구니 */}
      <div style={{ position: "absolute", left: 290, top: 560, width: 500, height: 340,
                    opacity: basketIn, transform: `translateY(${lerp(60, 0, basketIn)}px)` }}>
        <div style={{ width: "100%", height: "100%", background: C.bgPanel,
                      border: `4px solid ${C.clay}`, borderTop: "none",
                      borderRadius: "0 0 60px 60px",
                      clipPath: "polygon(0 0, 100% 0, 86% 100%, 14% 100%)" }} />
        <div style={{ position: "absolute", left: -20, top: -8, width: 540, height: 20,
                      borderRadius: 10, background: C.clay }} />
      </div>
      {/* 쏟아지는 이질적 물건 — 착지 셰이크 */}
      {drops.map((at, i) => {
        const item = ITEMS[i % ITEMS.length];
        const p = tw(t, at, 0.5, power2Out);
        if (p <= 0) return null;
        const lx = 250 + ((i * 173) % 560);
        const rot = ((i * 97) % 60) - 30;
        const overflow = i >= 5; // 뒤쪽 물건은 테두리 밖으로 튄다
        const ly = overflow ? 900 + ((i * 53) % 60) : 640 + ((i * 71) % 180);
        return (
          <div key={i} style={{ position: "absolute", left: lx, top: lerp(-140, ly, p),
                                fontSize: 110, transform: `rotate(${lerp(rot * 3, rot, p)}deg) translateX(${shake(t, at + 0.5, 5)}px)`,
                                filter: "grayscale(0.75) brightness(1.15)" }}>
            {item}
          </div>
        );
      })}
    </div>
  );
};

// ── s3 문제b: 엉킨 경로 + 어지러운 로봇 ────────────────────────
export const StageTangle: React.FC = () => {
  const t = useT();
  const drawP = tw(t, 0.2, 2.6, power2Out);
  const dizzy = Math.sin(t * 5) * 14 * clamp01((t - 1.6) / 0.6);
  const PATH = "M 540 380 C 200 480, 900 620, 480 740 C 120 850, 940 900, 560 1030 " +
               "C 260 1130, 820 1180, 520 1290";
  const LEN = 2600;
  return (
    <div style={{ position: "absolute", left: 0, top: 160, width: WORLD_W, height: 1300 }}>
      <svg width={WORLD_W} height={1300} style={{ position: "absolute", inset: 0 }}>
        <path d={PATH} fill="none" stroke={C.clayDim} strokeWidth={16} strokeLinecap="round"
              strokeDasharray={LEN} strokeDashoffset={LEN * (1 - drawP)} opacity={0.9} />
      </svg>
      {ITEMS.map((item, i) => (
        <div key={i} style={{ position: "absolute", left: 150 + ((i * 205) % 720),
                              top: 420 + ((i * 260) % 760), fontSize: 92,
                              filter: "grayscale(0.85) brightness(0.9)", opacity: 0.8 }}>
          {item}
        </div>
      ))}
      <div style={{ position: "absolute", left: 470, top: 300, fontSize: 150,
                    transform: `rotate(${dizzy}deg)`, filter: "grayscale(0.3)" }}>
        🤖
      </div>
    </div>
  );
};

// ── s4·s5 해결: 뼈대 타일 4개 + 마인드맵 가지 ──────────────────
const TILES = [
  { icon: "🏁", label: "출발" },
  { icon: "🛒", label: "마트" },
  { icon: "✏️", label: "문구점" },
  { icon: "🏠", label: "귀가" },
];

// tileAts: 각 타일이 팝되는 로컬 초 (s4에선 단어 앵커, s5에선 0=즉시 전부)
export const StageSkeleton: React.FC<{ tileAts: number[]; branchAt?: number; pushIn?: boolean }> = ({
  tileAts, branchAt, pushIn = false,
}) => {
  const t = useT();
  const camScale = pushIn ? lerp(1, 1.06, tw(t, 0, 6, power2Out)) : 1;
  const TILE_W = 224, GAP = 22;
  const rowX = (WORLD_W - TILE_W * 4 - GAP * 3) / 2;
  return (
    <div style={{ position: "absolute", left: 0, top: 400, width: WORLD_W, height: 1150,
                  transform: `scale(${camScale})`, transformOrigin: "50% 30%" }}>
      {TILES.map((tile, i) => {
        const p = tw(t, tileAts[i], 0.3, backOut(1.9));
        if (p <= 0) return null;
        const x = rowX + i * (TILE_W + GAP);
        return (
          <div key={i}>
            <div style={{ position: "absolute", left: x, top: 120, width: TILE_W, height: 250,
                          background: C.bgPanel, border: `3px solid ${C.clay}`, borderRadius: 30,
                          display: "flex", flexDirection: "column", alignItems: "center",
                          justifyContent: "center", gap: 14,
                          opacity: p, transform: `translateY(${lerp(-70, 0, p)}px) scale(${lerp(0.7, 1, p)}) translateX(${shake(t, tileAts[i] + 0.3, 4)}px)`,
                          boxShadow: `0 0 ${lerp(0, 30, p)}px rgba(255, 184, 77, 0.35)` }}>
              <div style={{ fontSize: 92, filter: "grayscale(0.6) brightness(1.2)" }}>{tile.icon}</div>
              <div style={{ fontFamily: FONT.kr, fontWeight: 800, fontSize: 44, color: C.text }}>
                {tile.label}
              </div>
            </div>
            {/* s5: 가지 전개 — 타일당 세부 블랭크 타일 2개 */}
            {branchAt !== undefined && [0, 1].map((b) => {
              const bp = tw(t, branchAt + i * 0.32 + b * 0.16, 0.34, power3Out);
              if (bp <= 0) return null;
              const by = 440 + b * 190;
              return (
                <div key={b}>
                  <svg style={{ position: "absolute", left: x + TILE_W / 2 - 4, top: 370, width: 8, height: by - 370 + 10 }}>
                    <rect x={0} y={0} width={8} height={(by - 370 + 10) * bp} rx={4} fill={C.clayDim} />
                  </svg>
                  <div style={{ position: "absolute", left: x + 26, top: by, width: TILE_W - 52, height: 130,
                                background: "rgba(154, 161, 171, 0.14)", border: `2px solid ${C.clayDim}`,
                                borderRadius: 22, opacity: bp,
                                transform: `translateY(${lerp(-24, 0, bp)}px)`,
                                display: "flex", flexDirection: "column", justifyContent: "center",
                                paddingLeft: 22, gap: 0 }}>
                    <ScribbleLine w={100} h={10} />
                    <ScribbleLine w={64} h={10} />
                  </div>
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

// ── s6 확장: 에디터 패널 — 스크립블 코드가 줄줄이 스냅 ─────────
export const StageEditor: React.FC<{ snapAt: number }> = ({ snapAt }) => {
  const t = useT();
  const panelIn = tw(t, 0.1, 0.4, power3Out);
  const glowP = tw(t, snapAt, 0.5, power2Out);
  const rows = [
    { w: 300, ind: 0 }, { w: 420, ind: 60 }, { w: 360, ind: 60 }, { w: 250, ind: 120 },
    { w: 400, ind: 120 }, { w: 330, ind: 60 }, { w: 460, ind: 0 }, { w: 280, ind: 60 },
    { w: 380, ind: 120 }, { w: 220, ind: 0 },
  ];
  return (
    <div style={{ position: "absolute", left: 110, top: 280, width: 860,
                  opacity: panelIn, transform: `translateY(${lerp(50, 0, panelIn)}px)` }}>
      <div style={{ background: C.bgPanel, border: `3px solid ${lerp(0, 1, glowP) > 0.3 ? C.warm : C.clay}`,
                    borderRadius: 30, padding: "48px 52px",
                    boxShadow: glowP > 0 ? `0 0 ${glowP * 60}px rgba(255, 184, 77, 0.4)` : "0 24px 60px rgba(0,0,0,0.45)" }}>
        <div style={{ display: "flex", gap: 12, marginBottom: 34 }}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ width: 16, height: 16, borderRadius: 8, background: C.clayDim }} />
          ))}
        </div>
        {rows.map((r, i) => {
          const rp = tw(t, 0.5 + i * 0.22, 0.26, backOut(1.5));
          if (rp <= 0) return <div key={i} style={{ height: 30 }} />;
          return (
            <div key={i} style={{ opacity: rp, transform: `translateX(${lerp(-40, 0, rp)}px)` }}>
              <ScribbleLine w={r.w} indent={r.ind}
                            color={glowP > 0.3 && r.ind === 0 ? C.warm : C.clayDim} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ── s7 아웃트로: 딸깍 버튼 + 파티클 + 어떻게/무엇을 대비 ────────
export const StageClick: React.FC<{ howAt: number; whatAt: number }> = ({ howAt, whatAt }) => {
  const t = useT();
  const pressP = tw(t, 0.4, 0.25, power3Out);
  const howP = tw(t, howAt, 0.28, backOut(1.7));
  const strikeP = tw(t, howAt + 0.5, 0.3, power2Out);
  const whatP = tw(t, whatAt, 0.3, backOut(1.9));
  return (
    <div style={{ position: "absolute", left: 0, top: 240, width: WORLD_W, height: 1200 }}>
      {/* 버튼 */}
      <div style={{ position: "absolute", left: 440, top: 880, width: 200, height: 200,
                    borderRadius: 100, background: C.bgPanel, border: `4px solid ${C.clay}`,
                    transform: `scale(${lerp(1, 0.9, pressP)})`,
                    boxShadow: pressP > 0.6 ? `0 0 50px rgba(255, 184, 77, 0.5)` : "none",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 84 }}>
        👆
      </div>
      {/* 상승 파티클 — 결정론적 */}
      {Array.from({ length: 26 }).map((_, i) => {
        const at = 0.7 + (i % 9) * 0.14;
        const pp = tw(t, at, 2.6, power2Out);
        if (pp <= 0) return null;
        const px = 180 + ((i * 137) % 720);
        return (
          <div key={i} style={{ position: "absolute", left: px, top: lerp(880, 60 + ((i * 61) % 220), pp),
                                width: 14 + (i % 3) * 8, height: 14 + (i % 3) * 8, borderRadius: 14,
                                background: C.warm, opacity: (1 - pp) * 0.9,
                                boxShadow: `0 0 18px ${C.warm}` }} />
        );
      })}
      {/* '어떻게' — 빨간 취소선 / '무엇을' — 웜 글로우 */}
      <div style={{ position: "absolute", left: 0, top: 180, width: WORLD_W, display: "flex",
                    justifyContent: "center", gap: 60 }}>
        <div style={{ opacity: howP, transform: `scale(${lerp(0.7, 1, howP)})`, position: "relative" }}>
          <div style={{ fontFamily: FONT.kr, fontWeight: 800, fontSize: 96, color: C.clayDim,
                        padding: "18px 44px", border: `4px solid ${C.clayDim}`, borderRadius: 26 }}>
            어떻게
          </div>
          <div style={{ position: "absolute", left: "6%", top: "50%", height: 14, borderRadius: 7,
                        background: C.red, width: `${strikeP * 88}%`,
                        boxShadow: `0 0 22px ${C.red}` }} />
        </div>
        <div style={{ opacity: whatP, transform: `scale(${lerp(0.7, 1, whatP)}) translateX(${shake(t, whatAt + 0.3, 5)}px)` }}>
          <div style={{ fontFamily: FONT.kr, fontWeight: 800, fontSize: 96, color: C.text,
                        padding: "18px 44px", border: `4px solid ${C.warm}`, borderRadius: 26,
                        boxShadow: `0 0 44px rgba(255, 184, 77, 0.55)` }}>
            무엇을
          </div>
        </div>
      </div>
    </div>
  );
};

// ── s8 티저: 사무실 군상 + 붉은 스포트라이트 + 슬램 ─────────────
export const StageTeaser: React.FC<{ spotAt: number; slamAt: number }> = ({ spotAt, slamAt }) => {
  const t = useT();
  const spotP = tw(t, spotAt, 0.3, power3Out);
  const slamP = tw(t, slamAt, 0.26, backOut(2.0));
  const rows = [0, 1, 2];
  const cols = [0, 1, 2, 3];
  return (
    <div style={{ position: "absolute", left: 0, top: 240, width: WORLD_W, height: 1200 }}>
      {rows.map((r) =>
        cols.map((c) => {
          const isTarget = r === 1 && c === 1;
          const x = 90 + c * 240, y = 140 + r * 300;
          return (
            <div key={`${r}-${c}`} style={{ position: "absolute", left: x, top: y, width: 190, height: 230,
                          opacity: isTarget && spotP > 0 ? 1 : 0.45 }}>
              <div style={{ width: 70, height: 70, borderRadius: 40, background: C.clayDim,
                            margin: "0 auto",
                            boxShadow: isTarget && spotP > 0 ? `0 0 ${spotP * 60}px ${C.red}` : "none",
                            border: isTarget && spotP > 0 ? `3px solid ${C.red}` : "none" }} />
              <div style={{ width: 150, height: 90, borderRadius: 18, background: C.clayDim,
                            margin: "14px auto 0", opacity: 0.9 }} />
              <div style={{ width: 190, height: 26, borderRadius: 8, background: "rgba(154,161,171,0.25)",
                            marginTop: 12 }} />
            </div>
          );
        }),
      )}
      {/* 스포트라이트 콘 */}
      {spotP > 0 && (
        <div style={{ position: "absolute", left: 330 + 95 - 210, top: 0, width: 420, height: 520,
                      background: `linear-gradient(180deg, rgba(255,59,48,${0.34 * spotP}) 0%, rgba(255,59,48,0) 92%)`,
                      clipPath: "polygon(42% 0, 58% 0, 100% 100%, 0 100%)" }} />
      )}
      {/* 다음 편 슬램 */}
      {slamP > 0 && (
        <div style={{ position: "absolute", left: 0, top: 740, width: WORLD_W, display: "flex",
                      flexDirection: "column", alignItems: "center", gap: 22,
                      opacity: slamP, transform: `scale(${lerp(1.7, 1, slamP)}) translateX(${shake(t, slamAt + 0.26, 8)}px)` }}>
          <div style={{ fontFamily: FONT.kr, fontWeight: 800, fontSize: 58, color: "#fff",
                        background: C.red, padding: "20px 46px", borderRadius: 22,
                        boxShadow: `0 0 46px rgba(255, 59, 48, 0.6)` }}>
            일 못하는 사람들의 공통점
          </div>
          <div style={{ fontFamily: FONT.kr, fontWeight: 600, fontSize: 40, color: C.dim }}>
            2편에서 계속
          </div>
        </div>
      )}
    </div>
  );
};
