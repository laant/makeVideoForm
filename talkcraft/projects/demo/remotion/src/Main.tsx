import React from "react";
import {
  AbsoluteFill, Audio, Sequence, getInputProps, staticFile,
  useCurrentFrame, useVideoConfig, interpolate,
} from "remotion";
import { timing, sceneById } from "./timing";
import { C, FONT, FONT_FACE_CSS, gridBg } from "./theme";
import { Subtitles } from "./Subtitles";
import NumberCounter from "./cards/number-counter";
import NumberSlabPop from "./cards/number-slab-pop";
import StrikeAndReplace from "./cards/strike-and-replace";
import AltBlockLines from "./cards/alt-block-lines";
import BrowserType from "./BrowserType";

export const FPS = 30;
export const TOTAL_FRAMES = Math.ceil(55.776 * FPS) + 12;

// 절대 초 단어 앵커 — 전부 timing.json(ASR)에서 조회 (수기 초 금지)
const absSay = (id: string, sub: string): number => {
  const sc = sceneById(id);
  const i = sc.text.indexOf(sub);
  if (i < 0) throw new Error(`anchor not found: ${id} "${sub}"`);
  return sc.chars[i].t;
};
const sceneStart = (id: string) => sceneById(id).startSec;
const F = (sec: number) => Math.round(sec * FPS);

// ── 앵커 계산 (SHOTBOOK 장면표와 1:1) ──
export const A = {
  s1Land: absSay("s1", "10조"),
  s2Start: sceneStart("s2"),
  s3Start: sceneStart("s3"),
  slab1: absSay("s4", "80만"),
  slab2: absSay("s4", "3조"),
  s5Start: sceneStart("s5"),
  typeAt: absSay("s6", "사이트"),
  nameAt: absSay("s6", "내보험찾아줌"),
  badgeAt: absSay("s7", "3분"),
  s8Start: sceneStart("s8"),
  strike: absSay("s9", "가짜"),
  replace: absSay("s10", "진짜"),
  subNote: absSay("s10", "고정"),
  s11Start: sceneStart("s11"),
  row1: absSay("s12", "나왔다"),
  row2: absSay("s12", "없었다"),
  s13Start: sceneStart("s13"),
  loopNum: absSay("s13", "10조"),
};

// 시퀀스 말미 0.3s 페이드아웃 (양보 원칙: 하드 퇴장 금지)
const FadeOut: React.FC<{ durationInFrames: number; children: React.ReactNode }> = ({
  durationInFrames, children,
}) => {
  const frame = useCurrentFrame();
  const fadeFrames = Math.round(0.3 * FPS);
  const opacity = interpolate(
    frame, [durationInFrames - fadeFrames, durationInFrames], [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};

// G1/G4 축약 러그: 전편 연속 슬로 푸시 + 그리드 드리프트 + 리사주 팬 + 비네트 호흡
// (motion_check 정지 검출 대응: 매 프레임 전 화면에 미동이 실리도록 배경도 함께 움직인다)
const Rig: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const scale = 1.02 + 0.05 * (frame / TOTAL_FRAMES);
  const panX = 9 * Math.sin(t * 0.51);
  const panY = 7 * Math.sin(t * 0.37 + 1.2);
  const breathe = 0.3 + 0.1 * Math.sin(t * 0.9);
  return (
    <AbsoluteFill style={{ ...gridBg, backgroundPosition: `${t * 6}px ${t * 3.4}px` }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translate(${panX}px, ${panY}px)` }}>
        {children}
      </AbsoluteFill>
      <AbsoluteFill style={{
        pointerEvents: "none",
        background: `radial-gradient(ellipse 82% 62% at 50% 44%, transparent 55%, rgba(0,0,0,${breathe}) 100%)`,
      }} />
    </AbsoluteFill>
  );
};

// G3 축약: hold 구간 idle 미동 (三段式 "hold 必须带 idle 微动")
const IdleFloat: React.FC<{ phase?: number; children: React.ReactNode }> = ({ phase = 0, children }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const y = 4 * Math.sin(t * 1.15 + phase);
  const x = 2.5 * Math.sin(t * 0.83 + phase * 1.7);
  return <AbsoluteFill style={{ transform: `translate(${x}px, ${y}px)` }}>{children}</AbsoluteFill>;
};

// S2 정의 라인
const DefLine: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [6, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 430,
                           fontFamily: FONT.kr }}>
      <div style={{ fontSize: 46, fontWeight: 600, color: C.text, letterSpacing: 2, opacity: p,
                    transform: `translateY(${(1 - p) * 14}px)` }}>
        청구 안 한 <span style={{ color: C.gold }}>만기·휴면 보험금</span>
      </div>
    </AbsoluteFill>
  );
};

// SFX cue 표 (SHOTBOOK 기재; t 는 전부 앵커 파생, vol ≤0.35)
// 문장 사이 무성 갭 (蓄势 cue 배치용 — 良品口径: 경계 cue 는 갭에서 출성)
const gapAfter = (id: string): number => {
  const sc = sceneById(id);
  return sc.chars[sc.chars.length - 1].e + 0.5; // TTS 꼬리 실측 ~0.3s → 창(+0.45s)이 다음 문장 전에 닫히는 지점
};

const CUES: { t: number; name: string; vol: number }[] = [
  { t: gapAfter("s2"), name: "pk-data-data-load-os", vol: 0.3 },   // S1→S2 蓄势 (갭)
  { t: A.s1Land, name: "pk-scifi-scifi-click", vol: 0.28 },
  { t: A.slab1, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.slab2, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.typeAt, name: "pk-text-keyboard", vol: 0.3 },
  { t: gapAfter("s8"), name: "pk-impact-impact-deep-whoosh", vol: 0.3 }, // S4 경고 蓄势 (갭)
  { t: A.strike, name: "pk-paper-paper-slice-quick", vol: 0.32 },
  { t: gapAfter("s9"), name: "ding", vol: 0.3 },                   // 교체 직전 蓄势 (갭)
  { t: A.row1, name: "pk-paper-paper-slide", vol: 0.3 },
  { t: A.row2, name: "pk-paper-paper-slide", vol: 0.3 },
];

export const Main: React.FC = () => {
  const { sfxSolo } = getInputProps() as { sfxSolo?: boolean };

  // 시퀀스 경계 (초)
  const s1From = 0;
  const s1To = A.slab1;                         // S1 카운터 retire = 슬랩1 앵커 (SHOTBOOK 양보 원칙)
  const s2To = A.s5Start;
  const s3From = A.s5Start + 0.25;
  const s3To = A.s8Start;
  const s4From = A.s8Start + 0.15;              // 개막 공백 방지: s8 초입부터 라인 상주
  const s4To = A.s11Start;
  const s5To = A.s13Start;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <style>{FONT_FACE_CSS}</style>
      <Rig>
        {/* S1 훅 — number-counter */}
        <Sequence from={F(s1From)} durationInFrames={F(s1To) - F(s1From)} name="S1 counter">
          <FadeOut durationInFrames={F(s1To) - F(s1From)}>
            <Sequence from={F(A.s1Land - 1.69)} name="counter-inner">
              <NumberCounter />
            </Sequence>
          </FadeOut>
        </Sequence>

        {/* S2 정의·실적 — number-slab-pop ×2 */}
        <Sequence from={F(A.s3Start)} durationInFrames={F(s2To) - F(A.s3Start)} name="S2 def+slabs">
          <FadeOut durationInFrames={F(s2To) - F(A.s3Start)}>
            <DefLine />
            <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", gap: 60,
                                   flexDirection: "column" }}>
              <Sequence from={F(A.slab1 - 0.34) - F(A.s3Start)} layout="none" name="slab1">
                <NumberSlabPop value="80만" unit="건" caption="작년 한 해 찾아간 사람" />
              </Sequence>
              <Sequence from={F(A.slab2 - 0.34) - F(A.s3Start)} layout="none" name="slab2">
                <NumberSlabPop value="3조" unit="원" caption="작년 한 해 돌아간 돈" />
              </Sequence>
            </AbsoluteFill>
          </FadeOut>
        </Sequence>

        {/* S3 방법 — browser 示意 UI */}
        <Sequence from={F(s3From)} durationInFrames={F(s3To) - F(s3From)} name="S3 browser">
          <FadeOut durationInFrames={F(s3To) - F(s3From)}>
            <BrowserType
              typeAt={A.typeAt - s3From}
              nameAt={A.nameAt - s3From}
              badgeAt={A.badgeAt - s3From}
            />
          </FadeOut>
        </Sequence>

        {/* S4 경고 — strike-and-replace */}
        <Sequence from={F(s4From)} durationInFrames={F(s4To) - F(s4From)} name="S4 strike">
          <FadeOut durationInFrames={F(s4To) - F(s4From)}>
            <StrikeAndReplace
              strikeAt={A.strike - s4From}
              swapDelay={A.replace - (A.strike + 0.15)}
              subline="구분법은 고정 댓글에 📌"
              sublineDelay={A.subNote - A.replace}
            />
          </FadeOut>
        </Sequence>

        {/* S5 CTA — alt-block-lines */}
        <Sequence from={F(A.s11Start)} durationInFrames={F(s5To) - F(A.s11Start)} name="S5 cta">
          <FadeOut durationInFrames={F(s5To) - F(A.s11Start)}>
            <AltBlockLines
              rows={[
                { text: "나왔다", at: A.row1 - A.s11Start, accent: true },
                { text: "없었다", at: A.row2 - A.s11Start, accent: false },
              ]}
            />
          </FadeOut>
        </Sequence>

        {/* S6 루프 — number-counter 재등장 (즉시 모드) */}
        <Sequence from={F(A.s13Start)} name="S6 loop">
          <NumberCounter instant caption="아직 주인을 기다립니다" />
        </Sequence>
      </Rig>

      {/* 자막 素排 (세로 레드라인: bottom 350 / 90%) — keyword-pop 3회 */}
      <Subtitles bottom={350} maxWidth="90%" fontSize={46}
                 keywords={["10조", "내보험찾아줌"]} />

      {/* 나레이션 (sfxSolo 렌더 시 제외 — sfx_check 용) */}
      {!sfxSolo && <Audio src={staticFile("full.mp3")} />}
      {CUES.map((c, i) => (
        <Sequence key={i} from={F(c.t)} name={`sfx-${c.name}`}>
          <Audio src={staticFile(`sfx/${c.name}.mp3`)} volume={c.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
