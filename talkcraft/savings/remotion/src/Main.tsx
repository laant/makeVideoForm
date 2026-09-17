import React from "react";
import {
  AbsoluteFill, Audio, Sequence, getInputProps, staticFile, useCurrentFrame,
} from "remotion";
import { timing, sceneFrameRanges, tSay, sceneById } from "./timing";
import { C, FONT_FACE_CSS, gridBg } from "./theme";
import { Subtitles } from "./Subtitles";
import NumberSlabPop from "./cards/number-slab-pop";
import {
  StageDoors, StageRuler, StageCoins, StageDouble, StageCalendar, StageBridge, StageRetro, StagePhone,
} from "./cards/money-world";

export const FPS = 30;
export const TOTAL_FRAMES = Math.ceil(timing.totalSec * FPS) + 12;
const F = (sec: number) => Math.round(sec * FPS);

const ranges = Object.fromEntries(sceneFrameRanges(FPS, TOTAL_FRAMES).map((r) => [r.id, r]));
const Seq: React.FC<{ id: string; children: React.ReactNode }> = ({ id, children }) => (
  <Sequence from={ranges[id].from} durationInFrames={ranges[id].duration} layout="none" name={id}>
    {children}
  </Sequence>
);

// 씬-로컬 앵커 (수기 초 금지)
const A = {
  s2push: tSay("s2", "군 복무"),
  s3bonus: tSay("s3", "정부가"),
  s3stamp: tSay("s3", "비과세"),
  s4grow: tSay("s4", "두 배"),
  s5: ["칠일", "팔일", "십이일"].map((w) => tSay("s5", w)),
  s5red: tSay("s5", "십육일"),
  s6cross: tSay("s6", "새 계좌"),
  s6close: tSay("s6", "특별"),
  s7grow: tSay("s7", "오를"),
  s8cards: tSay("s8", "홀수생"),
};

// 수치 슬랩 — 씬 시작 + 0.3s에 등장, 씬 끝까지 (다음 씬 시작 직전 퇴장)
const SLABS: { id: string; value: string; unit: string; caption: string }[] = [
  { id: "s1", value: "19.4", unit: "%", caption: "연 최고 효과 · 10월 7일 2차 오픈" },
  { id: "s2", value: "19~34", unit: "세", caption: "총급여 7,500만↓ · 복무 최대 6년 차감" },
  { id: "s3", value: "+216", unit: "만 원", caption: "우대형 기여금 · 이자 비과세" },
  { id: "s4", value: "12", unit: "%", caption: "우대형 기여금 (일반형 6%)" },
  { id: "s5", value: "10.7~16", unit: "", caption: "7일 홀수 · 8일 짝수 · 12일~ 누구나" },
  { id: "s6", value: "①→②", unit: "", caption: "새 계좌 개설 후 특별중도해지" },
  { id: "s7", value: "25", unit: "%", caption: "내년 소급 상향 (최대)" },
  { id: "s8", value: "1397", unit: "", caption: "서민금융진흥원 · 11월 계좌 개설" },
];

const Rig: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const scale = 1.015 + 0.035 * (frame / TOTAL_FRAMES);
  return (
    <AbsoluteFill style={{ ...gridBg, backgroundPosition: `${t * 5}px ${t * 3}px` }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translate(${6 * Math.sin(t * 0.4)}px, ${4 * Math.sin(t * 0.31 + 1.1)}px)` }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const TopSlab: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 150 }}>
    <div>{children}</div>
  </AbsoluteFill>
);

export const Main: React.FC = () => {
  const { sfxSolo } = getInputProps() as { sfxSolo?: boolean };
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <style>{FONT_FACE_CSS}</style>
      <Rig>
        <Seq id="s1"><StageDoors /></Seq>
        <Seq id="s2"><StageRuler pushAt={A.s2push} /></Seq>
        <Seq id="s3"><StageCoins bonusAt={A.s3bonus} stampAt={A.s3stamp} /></Seq>
        <Seq id="s4"><StageDouble growAt={A.s4grow} /></Seq>
        <Seq id="s5"><StageCalendar ats={A.s5} redAt={A.s5red} /></Seq>
        <Seq id="s6"><StageBridge crossAt={A.s6cross} closeAt={A.s6close} /></Seq>
        <Seq id="s7"><StageRetro growAt={A.s7grow} /></Seq>
        <Seq id="s8"><StagePhone cardsAt={A.s8cards} /></Seq>
        {SLABS.map((s) => {
          const r = ranges[s.id];
          const from = r.from + F(0.3);
          return (
            <Sequence key={s.id} from={from} durationInFrames={Math.max(1, r.duration - F(0.3))} layout="none" name={`slab-${s.id}`}>
              <TopSlab><NumberSlabPop value={s.value} unit={s.unit} caption={s.caption} /></TopSlab>
            </Sequence>
          );
        })}
      </Rig>
      <Subtitles bottom={350} maxWidth="90%" fontSize={70} keywords={["홀수"]} />
      {!sfxSolo && <Audio src={staticFile("full.mp3")} />}
    </AbsoluteFill>
  );
};
