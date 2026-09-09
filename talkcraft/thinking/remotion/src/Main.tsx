import React from "react";
import {
  AbsoluteFill, Audio, Sequence, getInputProps, staticFile,
  useCurrentFrame,
} from "remotion";
import { timing, sceneFrameRanges, tSay } from "./timing";
import { C, FONT_FACE_CSS, gridBg } from "./theme";
import { Subtitles } from "./Subtitles";
import {
  StageHook, StageBasket, StageTangle, StageSkeleton, StageEditor,
  StageClick, StageTeaser,
} from "./cards/structure-world";

export const FPS = 30;
export const TOTAL_FRAMES = Math.ceil(timing.totalSec * FPS) + 12;

const ranges = Object.fromEntries(
  sceneFrameRanges(FPS, TOTAL_FRAMES).map((r) => [r.id, r]),
);
const Seq: React.FC<{ id: string; children: React.ReactNode }> = ({ id, children }) => (
  <Sequence from={ranges[id].from} durationInFrames={ranges[id].duration} layout="none" name={id}>
    {children}
  </Sequence>
);

// 씬-로컬 앵커 (수기 초 금지 — 전부 나레이션 타임스탬프에서)
const A = {
  s1x: tSay("s1", "프롬프트"),
  s4t: ["출발", "마트", "문구점", "귀가"].map((w) => tSay("s4", w)),
  s5b: tSay("s5", "세부"),
  s6snap: tSay("s6", "설계"),
  s7how: tSay("s7", "어떻게"),
  s7what: tSay("s7", "무엇을"),
  s8spot: tSay("s8", "일 못한다는"),
  s8slam: tSay("s8", "소름"),
};

const Rig: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const scale = 1.015 + 0.035 * (frame / TOTAL_FRAMES);
  const panX = 6 * Math.sin(t * 0.4);
  const panY = 4 * Math.sin(t * 0.31 + 1.1);
  return (
    <AbsoluteFill style={{ ...gridBg, backgroundPosition: `${t * 5}px ${t * 3}px` }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translate(${panX}px, ${panY}px)` }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => {
  const { sfxSolo } = getInputProps() as { sfxSolo?: boolean };
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <style>{FONT_FACE_CSS}</style>
      <Rig>
        <Seq id="s1"><StageHook xAt={A.s1x} /></Seq>
        <Seq id="s2"><StageBasket /></Seq>
        <Seq id="s3"><StageTangle /></Seq>
        <Seq id="s4"><StageSkeleton tileAts={A.s4t} /></Seq>
        <Seq id="s5"><StageSkeleton tileAts={[0, 0, 0, 0]} branchAt={A.s5b} pushIn /></Seq>
        <Seq id="s6"><StageEditor snapAt={A.s6snap} /></Seq>
        <Seq id="s7"><StageClick howAt={A.s7how} whatAt={A.s7what} /></Seq>
        <Seq id="s8"><StageTeaser spotAt={A.s8spot} slamAt={A.s8slam} /></Seq>
      </Rig>

      <Subtitles bottom={350} maxWidth="90%" fontSize={70} keywords={["뼈대"]} />

      {!sfxSolo && <Audio src={staticFile("full.mp3")} />}
    </AbsoluteFill>
  );
};
