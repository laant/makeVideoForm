import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "./theme";

// S3 방법 씬 — 브라우저 주소창 타이핑 示意 UI (bespoke; SHOTBOOK S3 노트 참조:
// 실서비스 cont.insure.or.kr 가 헤드리스 캡처를 404로 차단 → 真图 불가 사유 기록됨.
// mock 은 주소창·이름 카드에 한정, 페이지 본문을 위장하지 않음)
const URL_TEXT = "cont.insure.or.kr";

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const tw = (t: number, t0: number, d: number, ease: (x: number) => number) =>
  ease(clamp01((t - t0) / d));
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const power2Out = (x: number) => 1 - Math.pow(1 - x, 3);
const backOut = (s = 1.70158) => (x: number) => {
  const u = x - 1;
  return 1 + (s + 1) * u * u * u + s * u * u;
};

export default function BrowserType({
  typeAt = 0.4,      // 타이핑 시작 (카드 상대 초)
  nameAt = 2.0,      // "내보험찾아줌" 카드 팝
  badgeAt = 5.0,     // "3분" 배지 팝
}: { typeAt?: number; nameAt?: number; badgeAt?: number }) {
  const { fps } = useVideoConfig();
  const t = useCurrentFrame() / fps;

  const inP = tw(t, 0, 0.35, power2Out);
  const typeDur = 1.4;
  const chars = Math.round(lerp(0, URL_TEXT.length, tw(t, typeAt, typeDur, (x) => x)));
  const caretOn = Math.floor(t * 2.4) % 2 === 0 && t < typeAt + typeDur + 0.4;
  const nameP = tw(t, nameAt, 0.32, backOut(1.7));
  const badgeP = tw(t, badgeAt, 0.3, backOut(1.9));

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT.kr }}>
      <div style={{ width: 880, opacity: inP, transform: `translateY(${lerp(30, 0, inP)}px)` }}>
        {/* 브라우저 프레임 (示意) */}
        <div style={{ background: C.bgPanel, borderRadius: 24, border: `1px solid ${C.line}`,
                      overflow: "hidden", boxShadow: "0 30px 80px rgba(0,0,0,0.45)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "22px 26px",
                        borderBottom: `1px solid ${C.line}` }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((c) => (
              <span key={c} style={{ width: 18, height: 18, borderRadius: 9, background: c }} />
            ))}
            <div style={{ flex: 1, marginLeft: 16, background: "rgba(255,255,255,0.07)",
                          borderRadius: 12, padding: "14px 22px", fontFamily: FONT.mono,
                          fontSize: 34, color: C.text, letterSpacing: 1 }}>
              🔒 {URL_TEXT.slice(0, chars)}
              <span style={{ opacity: caretOn ? 1 : 0, color: C.gold }}>|</span>
            </div>
          </div>
          <div style={{ height: 430, display: "flex", alignItems: "center",
                        justifyContent: "center", flexDirection: "column", gap: 26 }}>
            {/* 서비스명 카드 팝 */}
            <div style={{ opacity: Math.min(1, nameP), transform: `scale(${lerp(0.8, 1, nameP)})`,
                          background: C.gold, color: C.bg, fontSize: 76, fontWeight: 800,
                          padding: "26px 54px", borderRadius: 18, letterSpacing: -1 }}>
              내보험찾아줌
            </div>
            <div style={{ opacity: Math.min(1, nameP), fontSize: 32, color: C.dim, letterSpacing: 2 }}>
              생명·손해보험협회 공동 운영 · 무료
            </div>
          </div>
        </div>
        {/* 3분 배지 */}
        <div style={{ display: "flex", justifyContent: "center", marginTop: 40 }}>
          <div style={{ opacity: Math.min(1, badgeP), transform: `scale(${lerp(0.7, 1, badgeP)})`,
                        border: `3px solid ${C.gold}`, color: C.gold, fontSize: 46, fontWeight: 800,
                        borderRadius: 999, padding: "16px 44px", letterSpacing: 1 }}>
            휴대폰 인증 ⏱ 3분
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
}
