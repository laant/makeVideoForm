import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// number-slab-pop · 数字弹出 —— template/cards/number-slab-pop.tsx 복사·개조
// 개조: 데모 문맥(백색+호스트) 제거, 금색 슬랩/다크 텍스트, 값·캡션 props화 (2개 인스턴스 병렬 배치용).
// 동효 본체(块先落 → 数字后弹 → 单位延后 → 说明行 최후) 3단 구조와 파라미터는 원본 유지.
export const meta = { width: 1080, height: 1920, fps: 30, durationInFrames: 101 };

// ===== 可摘走的核心动画参数 =====
// 语义：这是「结论感」的数字——一次弹出就到位，不给过程。
const CONFIG = {
  lead: 0.10,        // 起手静置 s（Sequence 배치를 단어 앵커에 맞추므로 짧게）
  slabDrop: 20,      // 色块起始上移 px（从上方落下）
  slabScale: 0.94,   // 色块起始缩放
  slabDur: 0.24,     // 色块落定 s
  numScale: 0.72,    // 数字起始缩放
  numDur: 0.28,      // 数字弹出 s
  decLag: 0.20,      // 单位相对数字弹出起点的延后 s
  decIn: 0.18,       // 单位淡入 s
  capRise: 6,        // 说明行上浮 px
  capIn: 0.24,       // 说明行淡入 s
};

/* 时间表（카드 내 상대 초）
   0.10–0.34  色块落定 opacity/y -20→0/scale 0.94→1（power3.out）
   0.34–0.62  数字整体弹出 opacity/scale 0.72→1（back.out(1.7)）
   0.54–0.72  单位淡入（power2.out）
   0.72–0.96  说明行淡入上浮（power2.out） */

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

export default function NumberSlabPop({
  value = "23", unit = "%", caption = "较去年增长",
}: { value?: string; unit?: string; caption?: string }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;

  // ① 色块先落到位（数字此刻还不在场）
  const slabP = tw(t, CONFIG.lead, CONFIG.slabDur, power3Out);
  // ② 块落定后数字整体弹出
  const numAt = CONFIG.lead + CONFIG.slabDur;
  const numP = tw(t, numAt, CONFIG.numDur, backOut(1.7));
  // ②b 单位延后单独淡入
  const decP = tw(t, numAt + CONFIG.decLag, CONFIG.decIn, power2Out);
  // ③ 说明行最后淡入上浮
  const capAt = numAt + CONFIG.decLag + CONFIG.decIn;
  const capP = tw(t, capAt, CONFIG.capIn, power2Out);

  return (
    <div style={{ fontFamily: FONT.kr, textAlign: "center" }}>
      <div style={{
        display: "inline-block", padding: "26px 44px 30px", borderRadius: 28,
        background: C.gold, transformOrigin: "50% 50%",
        opacity: slabP,
        transform: `translateY(${lerp(-CONFIG.slabDrop, 0, slabP)}px) scale(${lerp(CONFIG.slabScale, 1, slabP)})`,
      }}>
        <div style={{
          display: "flex", alignItems: "baseline", whiteSpace: "nowrap",
          fontVariantNumeric: "tabular-nums", color: C.bg, fontWeight: 800,
          lineHeight: 1, letterSpacing: "-0.02em",
          opacity: Math.min(1, numP), transform: `scale(${lerp(CONFIG.numScale, 1, numP)})`,
          transformOrigin: "50% 60%",
        }}>
          <span style={{ fontSize: 108 }}>{value}</span>
          <span style={{ fontSize: 58, marginLeft: 8, opacity: decP }}>{unit}</span>
        </div>
      </div>
      <div style={{
        marginTop: 20, fontSize: 30, fontWeight: 400, color: C.dim, letterSpacing: 3,
        opacity: capP, transform: `translateY(${lerp(CONFIG.capRise, 0, capP)}px)`,
      }}>{caption}</div>
    </div>
  );
}
