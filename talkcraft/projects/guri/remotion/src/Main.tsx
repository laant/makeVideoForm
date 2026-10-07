import React from "react";
import {
  AbsoluteFill, Audio, Sequence, getInputProps, staticFile,
  useCurrentFrame, interpolate,
} from "remotion";
import { timing, sceneById } from "./timing";
import { C, FONT, FONT_FACE_CSS, gridBg } from "./theme";
import { Subtitles } from "./Subtitles";
import PaperCity from "./cards/paper-city";
import NumberSlabPop from "./cards/number-slab-pop";
import AltBlockLines from "./cards/alt-block-lines";

export const FPS = 30;
export const TOTAL_FRAMES = Math.ceil(timing.totalSec * FPS) + 12;

const absSay = (id: string, sub: string): number => {
  const sc = sceneById(id);
  const i = sc.text.indexOf(sub);
  if (i < 0) throw new Error(`anchor not found: ${id} "${sub}"`);
  return sc.chars[i].t;
};
const sceneStart = (id: string) => sceneById(id).startSec;
const F = (sec: number) => Math.round(sec * FPS);

export const A = {
  xAt: absSay("s3", "사라"),
  parkAt: absSay("s4", "발상"),
  pole1At: absSay("s5", "오십"),
  n50: absSay("s5", "오십"),
  mtOpenAt: absSay("s6", "아차산"),
  pole2At: absSay("s7", "칠십오"),
  n75: absSay("s7", "칠십오"),
  compareAt: absSay("s8", "가로"),
  n1812: absSay("s8", "십팔"),
  s9Start: sceneStart("s9"),
  award: absSay("s10", "이천십"),
  dominoAt: absSay("s11", "곳곳"),
  n365: absSay("s11", "삼백"),
  s12Start: sceneStart("s12"),
  warmAt: sceneStart("s12"),
  row1: absSay("s12", "멋지다"),
  row2: absSay("s12", "과하다"),
};

// 전편 연속 슬로 푸시 + 그리드 드리프트 (라이트 페이퍼 버전 — 비네트 약하게)
const Rig: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const scale = 1.02 + 0.05 * (frame / TOTAL_FRAMES);
  const panX = 9 * Math.sin(t * 0.51);
  const panY = 7 * Math.sin(t * 0.37 + 1.2);
  const breathe = 0.08 + 0.04 * Math.sin(t * 0.9);
  return (
    <AbsoluteFill style={{ ...gridBg, backgroundPosition: `${t * 6}px ${t * 3.4}px` }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translate(${panX}px, ${panY}px)` }}>
        {children}
      </AbsoluteFill>
      <AbsoluteFill style={{
        pointerEvents: "none",
        background: `radial-gradient(ellipse 82% 62% at 50% 44%, transparent 55%, rgba(43,30,10,${breathe}) 100%)`,
      }} />
    </AbsoluteFill>
  );
};

const TopSlab: React.FC<{ children: React.ReactNode; y?: number }> = ({ children, y = 190 }) => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: y }}>
    <div>{children}</div>
  </AbsoluteFill>
);

const CUES: { t: number; name: string; vol: number }[] = [
  { t: A.pole1At, name: "pk-impact-impact-deep-whoosh", vol: 0.28 },
  { t: A.n50 - 0.1, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.pole2At, name: "pk-impact-impact-deep-whoosh", vol: 0.3 },
  { t: A.n1812 - 0.1, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.award, name: "pk-mech-lock-quick", vol: 0.3 },
  { t: A.dominoAt, name: "pk-paper-paper-slide", vol: 0.32 },
  { t: A.row1, name: "pk-paper-paper-slide", vol: 0.3 },
  { t: A.row2, name: "pk-paper-paper-slide", vol: 0.3 },
];

export const Main: React.FC = () => {
  const { sfxSolo } = getInputProps() as { sfxSolo?: boolean };

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <style>{FONT_FACE_CSS}</style>
      <Rig>
        {/* 월드 — 전편 롱테이크 페이퍼 디오라마 */}
        <PaperCity stages={{
          xAt: A.xAt, parkAt: A.parkAt, pole1At: A.pole1At, mtOpenAt: A.mtOpenAt,
          pole2At: A.pole2At, compareAt: A.compareAt, compareEnd: A.s9Start,
          dominoAt: A.dominoAt, warmAt: A.warmAt,
        }} />

        {/* 수치 슬랩 — 발화 앵커에 팝, 다음 국면 전 퇴장 (계측선 규칙: 수치 씬만) */}
        <Sequence from={F(A.n50 - 0.34)} durationInFrames={F(A.mtOpenAt) - F(A.n50 - 0.34)} layout="none" name="slab-50">
          <TopSlab><NumberSlabPop value="50" unit="m" caption="한강시민공원 게양대 · 2007" /></TopSlab>
        </Sequence>
        <Sequence from={F(A.n75 - 0.34)} durationInFrames={F(A.compareAt) - F(A.n75 - 0.34)} layout="none" name="slab-75">
          <TopSlab><NumberSlabPop value="75" unit="m" caption="아차산 게양대 · 아파트 25층 · 2013" /></TopSlab>
        </Sequence>
        <Sequence from={F(A.n1812 - 0.34)} durationInFrames={F(A.s9Start) - F(A.n1812 - 0.34)} layout="none" name="slab-1812">
          <TopSlab y={130}><NumberSlabPop value="18×12" unit="m" caption="배구 코트보다 큰 태극기" /></TopSlab>
        </Sequence>
        <Sequence from={F(A.award - 0.34)} durationInFrames={F(A.dominoAt) - F(A.award - 0.34)} layout="none" name="slab-2010">
          <TopSlab><NumberSlabPop value="2010" unit="년" caption="국기 선양 대통령 표창" /></TopSlab>
        </Sequence>
        <Sequence from={F(A.n365 - 0.34)} durationInFrames={F(A.s12Start) - F(A.n365 - 0.34)} layout="none" name="slab-365">
          <TopSlab><NumberSlabPop value="365" unit="일" caption="일 년 내내 펄럭입니다" /></TopSlab>
        </Sequence>

        {/* CTA — 양자택일 */}
        <Sequence from={F(A.s12Start)} name="cta">
          <AltBlockLines
            rows={[
              { text: "멋지다", at: A.row1 - A.s12Start, accent: true },
              { text: "과하다", at: A.row2 - A.s12Start, accent: false },
            ]}
          />
        </Sequence>
      </Rig>

      <Subtitles bottom={350} maxWidth="90%" fontSize={70} keywords={[]} />

      {!sfxSolo && <Audio src={staticFile("full.mp3")} />}
      {CUES.map((c, i) => (
        <Sequence key={i} from={F(c.t)} name={`sfx-${c.name}`}>
          <Audio src={staticFile(`sfx/${c.name}.mp3`)} volume={c.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
