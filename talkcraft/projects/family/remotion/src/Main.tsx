import React from "react";
import {
  AbsoluteFill, Audio, Sequence, getInputProps, staticFile,
  useCurrentFrame, interpolate,
} from "remotion";
import { timing, sceneById } from "./timing";
import { C, FONT, FONT_FACE_CSS, gridBg } from "./theme";
import { Subtitles } from "./Subtitles";
import TimelineWorld, { Era } from "./cards/timeline-world";
import NumberSlabPop from "./cards/number-slab-pop";

export const FPS = 30;
export const TOTAL_FRAMES = Math.ceil(timing.totalSec * FPS) + 12;

const sceneStart = (id: string) => sceneById(id).startSec;
const absSay = (id: string, sub: string): number => {
  const sc = sceneById(id);
  const i = sc.text.indexOf(sub);
  if (i < 0) throw new Error(`anchor not found: ${id} "${sub}"`);
  return sc.chars[i].t;
};
const F = (sec: number) => Math.round(sec * FPS);

// 시대 레일 — 씬 시작 앵커에 노드가 켜진다 (연도·아이콘은 코드가 보장하는 정확성)
const ERAS: Era[] = [
  { year: "시작", label: "족보를 열다", at: 0, icon: "book" },
  { year: "660", label: "시조 이무", at: sceneStart("s2"), icon: "helmet" },
  { year: "1573", label: "청련 이후백", at: sceneStart("s4"), icon: "brush" },
  { year: "1597", label: "명량해전", at: sceneStart("s6"), icon: "ship" },
  { year: "1619", label: "의마총", at: sceneStart("s7"), icon: "horse" },
  { year: "1627", label: "해남 입향", at: sceneStart("s9"), icon: "house" },
  { year: "1919", label: "임시정부", at: sceneStart("s10"), icon: "flag" },
  { year: "오늘", label: "너희들", at: sceneStart("s11"), icon: "children" },
];

const A = {
  km1000: absSay("s8", "천 킬로"),
  y400: absSay("s9", "사백"),
  gen24: absSay("s12", "이십사"),
};

const Rig: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const scale = 1.015 + 0.035 * (frame / TOTAL_FRAMES);
  const panX = 7 * Math.sin(t * 0.4);
  const panY = 5 * Math.sin(t * 0.31 + 1.1);
  return (
    <AbsoluteFill style={{ ...gridBg, backgroundPosition: `${t * 5}px ${t * 3}px` }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translate(${panX}px, ${panY}px)` }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const TopSlab: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 70 }}>
    <div>{children}</div>
  </AbsoluteFill>
);

export const Main: React.FC = () => {
  const { sfxSolo } = getInputProps() as { sfxSolo?: boolean };
  const frame = useCurrentFrame();
  const t = frame / FPS;
  // focus = 현재 시각이 지난 마지막 시대 인덱스
  let focus = 0;
  ERAS.forEach((e, i) => { if (t >= e.at) focus = i; });

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <style>{FONT_FACE_CSS}</style>
      <Rig>
        <TimelineWorld eras={ERAS} focus={focus} />
        {/* 수치 슬랩 — 핵심 숫자만 (가족용이라 절제) */}
        <Sequence from={F(A.km1000 - 0.3)} durationInFrames={F(sceneStart("s9")) - F(A.km1000 - 0.3)} layout="none" name="slab-1000km">
          <TopSlab><NumberSlabPop value="1,000" unit="km" caption="사흘을 달린 충성스러운 말" /></TopSlab>
        </Sequence>
        <Sequence from={F(A.y400 - 0.3)} durationInFrames={F(sceneStart("s10")) - F(A.y400 - 0.3)} layout="none" name="slab-400">
          <TopSlab><NumberSlabPop value="400" unit="년" caption="해남 삼산면의 터전" /></TopSlab>
        </Sequence>
        <Sequence from={F(A.gen24 - 0.3)} layout="none" name="slab-24">
          <TopSlab><NumberSlabPop value="24" unit="대" caption="이야기의 주인공은 너희들" /></TopSlab>
        </Sequence>
      </Rig>

      <Subtitles bottom={70} maxWidth="80%" fontSize={70} keywords={[]} />

      {!sfxSolo && <Audio src={staticFile("full.mp3")} />}
    </AbsoluteFill>
  );
};
