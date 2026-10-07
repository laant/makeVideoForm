import React from "react";
import {
  AbsoluteFill, Audio, Sequence, getInputProps, staticFile,
  useCurrentFrame, interpolate,
} from "remotion";
import { timing, sceneById } from "./timing";
import { C, FONT, FONT_FACE_CSS, gridBg } from "./theme";
import { Subtitles } from "./Subtitles";
import DimensionCounter from "./cards/dimension-counter";
import CrossSection from "./cards/cross-section";
import NumberSlabPop from "./cards/number-slab-pop";
import AltBlockLines from "./cards/alt-block-lines";

export const FPS = 30;
export const TOTAL_FRAMES = Math.ceil(timing.totalSec * FPS) + 12;

// 절대 초 단어 앵커 — 전부 timing.json에서 조회 (수기 초 금지)
const absSay = (id: string, sub: string): number => {
  const sc = sceneById(id);
  const i = sc.text.indexOf(sub);
  if (i < 0) throw new Error(`anchor not found: ${id} "${sub}"`);
  return sc.chars[i].t;
};
const sceneStart = (id: string) => sceneById(id).startSec;
const F = (sec: number) => Math.round(sec * FPS);

// ── 앵커 (건축쇼츠 규칙: 계측선·숫자 카드는 수치 발화 시점에) ──
export const A = {
  depth1: absSay("s1", "오십"),
  machine: absSay("s2", "기계"),
  s3Start: sceneStart("s3"),
  rise: absSay("s3", "비만"),
  dense: absSay("s4", "빽빽"),
  dig: absSay("s5", "땅속"),
  depth2: absSay("s5", "오십"),
  rivers: absSay("s6", "넘친"),
  dia: absSay("s6", "육"),
  plunge: absSay("s7", "폭포"),
  pillars: absSay("s8", "기둥"),
  n59: absSay("s8", "오십구"),
  turbines: absSay("s9", "터빈"),
  n200: absSay("s9", "이백"),
  y13: absSay("s10", "십삼"),
  w2: absSay("s10", "이 조"),
  p90: absSay("s10", "구십"),
  s11Start: sceneStart("s11"),
  s12Start: sceneStart("s12"),
  row1: absSay("s12", "필요"),
  row2: absSay("s12", "아닐까요"),
};

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

// 전편 연속 슬로 푸시 + 그리드 드리프트 + 비네트 호흡 (데모 Rig 계승)
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

// s2 — "신전이 아니라 기계" 태그라인 (기계에 레드 팝)
const TagLine: React.FC<{ popAtRel: number }> = ({ popAtRel }) => {
  const t = useCurrentFrame() / FPS;
  const inP = interpolate(t, [0, 0.4], [0, 1], { extrapolateRight: "clamp" });
  const pop = interpolate(t, [popAtRel, popAtRel + 0.25], [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 380,
                           fontFamily: FONT.kr }}>
      <div style={{ fontSize: 52, fontWeight: 700, color: C.text, opacity: inP,
                    transform: `translateY(${(1 - inP) * 14}px)` }}>
        신전이 아니라{" "}
        <span style={{ color: C.red, display: "inline-block",
                       transform: `scale(${1 + 0.14 * Math.sin(Math.min(pop, 1) * Math.PI)})` }}>
          도시를 지키는 기계
        </span>
      </div>
    </AbsoluteFill>
  );
};

// 슬랩 배치 러그 — 단면도 위(상단 밴드)에 얹는다
const TopSlab: React.FC<{ children: React.ReactNode; y?: number }> = ({ children, y = 210 }) => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: y }}>
    <div>{children}</div>
  </AbsoluteFill>
);

const CUES: { t: number; name: string; vol: number }[] = [
  { t: A.depth1 + 1.4, name: "pk-scifi-scifi-click", vol: 0.28 },
  { t: A.dig, name: "pk-impact-impact-deep-whoosh", vol: 0.3 },
  { t: A.dia - 0.1, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.plunge, name: "pk-impact-impact-deep-whoosh", vol: 0.32 },
  { t: A.n59 - 0.1, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.n200 - 0.1, name: "pk-impact-hit-fast-exciting", vol: 0.25 },
  { t: A.row1, name: "pk-paper-paper-slide", vol: 0.3 },
  { t: A.row2, name: "pk-paper-paper-slide", vol: 0.3 },
];

export const Main: React.FC = () => {
  const { sfxSolo } = getInputProps() as { sfxSolo?: boolean };
  const worldFrom = A.s3Start;
  const worldTo = A.s12Start;

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <style>{FONT_FACE_CSS}</style>
      <Rig>
        {/* S1 훅 — 계측선 카운터 (지하 50m) + s2 태그라인 */}
        <Sequence from={F(Math.max(0, A.depth1 - 0.3))}
                  durationInFrames={F(worldFrom) - F(Math.max(0, A.depth1 - 0.3))} name="S1 dim">
          <FadeOut durationInFrames={F(worldFrom) - F(Math.max(0, A.depth1 - 0.3))}>
            <DimensionCounter target={50} unit="m" prefix="지하" label="거대한 신전" />
            <Sequence from={F(sceneStart("s2")) - F(Math.max(0, A.depth1 - 0.3))} layout="none">
              <TagLine popAtRel={A.machine - sceneStart("s2")} />
            </Sequence>
          </FadeOut>
        </Sequence>

        {/* S2 월드 — 단면도 롱테이크 (s3~s11) */}
        <Sequence from={F(worldFrom)} durationInFrames={F(worldTo) - F(worldFrom)} name="world">
          <FadeOut durationInFrames={F(worldTo) - F(worldFrom)}>
            <CrossSection stages={{
              waterRiseAt: A.rise - worldFrom,
              densifyAt: A.dense - worldFrom,
              shaftAt: A.dig - worldFrom,
              riversAt: A.rivers - worldFrom,
              plungeAt: A.plunge - worldFrom,
              pillarsAt: A.pillars - worldFrom,
              turbinesAt: A.turbines - worldFrom,
              calmAt: A.s11Start - worldFrom,
            }} />
            {/* 수치 슬랩들 — 발화 앵커에 팝 (계측선 규칙: 수치 있는 씬만) */}
            <Sequence from={F(A.depth2 - 0.34) - F(worldFrom)} durationInFrames={F(A.rivers) - F(A.depth2 - 0.34)} layout="none" name="slab-50m">
              <TopSlab><NumberSlabPop value="50" unit="m" caption="도시 아래로 내린 깊이" /></TopSlab>
            </Sequence>
            <Sequence from={F(A.dia - 0.34) - F(worldFrom)} durationInFrames={F(A.plunge) - F(A.dia - 0.34)} layout="none" name="slab-64">
              <TopSlab><NumberSlabPop value="6.4" unit="km" caption="지름 10m · 강 5개를 삼킨다" /></TopSlab>
            </Sequence>
            <Sequence from={F(A.n59 - 0.34) - F(worldFrom)} durationInFrames={F(A.turbines) - F(A.n59 - 0.34)} layout="none" name="slab-59">
              <TopSlab><NumberSlabPop value="59" unit="개" caption="기둥 하나에 500톤" /></TopSlab>
            </Sequence>
            <Sequence from={F(A.n200 - 0.34) - F(worldFrom)} durationInFrames={F(A.y13) - F(A.n200 - 0.34)} layout="none" name="slab-200">
              <TopSlab><NumberSlabPop value="200" unit="톤" caption="매초 · 제트엔진급 터빈 4대" /></TopSlab>
            </Sequence>
            <Sequence from={F(A.y13 - 0.34) - F(worldFrom)} layout="none" name="slab-13">
              <TopSlab y={130}><NumberSlabPop value="13" unit="년" caption="공사 기간" /></TopSlab>
            </Sequence>
            <Sequence from={F(A.w2 - 0.34) - F(worldFrom)} layout="none" name="slab-2jo">
              <TopSlab y={360}><NumberSlabPop value="2조" unit="원" caption="총 사업비" /></TopSlab>
            </Sequence>
            <Sequence from={F(A.p90 - 0.34) - F(worldFrom)} layout="none" name="slab-90">
              <TopSlab y={590}><NumberSlabPop value="90" unit="%" caption="침수 피해 감소" /></TopSlab>
            </Sequence>
          </FadeOut>
        </Sequence>

        {/* S3 루프+CTA — 계측선 즉시 재등장 + 양자택일 */}
        <Sequence from={F(A.s12Start)} name="S3 loop-cta">
          <DimensionCounter target={50} unit="m" prefix="지하" label="서울에도, 필요할까?" instant />
          <AltBlockLines
            rows={[
              { text: "필요하다", at: A.row1 - A.s12Start, accent: true },
              { text: "아니다", at: A.row2 - A.s12Start, accent: false },
            ]}
          />
        </Sequence>
      </Rig>

      <Subtitles bottom={350} maxWidth="90%" fontSize={46} keywords={["신전"]} />

      {!sfxSolo && <Audio src={staticFile("full.mp3")} />}
      {CUES.map((c, i) => (
        <Sequence key={i} from={F(c.t)} name={`sfx-${c.name}`}>
          <Audio src={staticFile(`sfx/${c.name}.mp3`)} volume={c.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
