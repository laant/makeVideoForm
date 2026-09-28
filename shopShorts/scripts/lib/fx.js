// 트랜지션·화면 효과 라이브러리 (FFmpeg, 합성 단계에서 적용 — 결정적: 랜덤 시드 고정)
// 목록·용도: templates/scenes/README.md

// ── 트랜지션 (transitionOut) ────────────────────────────────
// xfade 내장 이름이거나 custom 수식. custom 수식의 P 는 1(이전 씬) → 0(다음 씬)
// 좌표는 plane 별(크로마는 절반 해상도)이므로 샘플링은 plane 선택 헬퍼로.
// st()/ld() 금지: xfade 는 슬라이스 스레드로 돌아 변수가 경쟁 → 줄무늬. 하위 수식은 문자열로 인라인한다.
const pick = (src, x, y) =>
  `if(eq(PLANE,0),${src}0(${x},${y}),if(eq(PLANE,1),${src}1(${x},${y}),if(eq(PLANE,2),${src}2(${x},${y}),${src}3(${x},${y}))))`;
const G = "(1-abs(2*P-1))"; // 중간에서 최대가 되는 강도 0→1→0
const mixAt = (ax, ay, bx, by) => `(${pick("a", ax, ay)}*P+${pick("b", bx, by)}*(1-P))`;
const clampX = (e) => `clip(${e},0,W-1)`;
const clampY = (e) => `clip(${e},0,H-1)`;
const warp = (dx, dy) => mixAt(clampX(`X+${dx}`), clampY(`Y+${dy}`), clampX(`X+${dx}`), clampY(`Y+${dy}`));

const R = "hypot(X-W/2,Y-H/2)"; // 중심 거리

export const TRANSITION_DEFS = {
  cut: { desc: "하드 컷 (겹침 없음)" },
  crossfade: { xfade: "fade", desc: "크로스페이드 — 기본" },
  "white-flash": { xfade: "fadewhite", desc: "화이트 플래시 — 강조·반전" },
  "black-flash": { xfade: "fadeblack", desc: "블랙 페이드 — 챕터 전환" },
  "rgb-split": {
    // 크로마 평면을 좌우로 벌렸다 모음 (색 채널 분리)
    expr: `if(eq(PLANE,0),${mixAt("X", "Y", "X", "Y")},${mixAt(clampX(`X-${G}*14*(2*PLANE-3)`), "Y", clampX(`X+${G}*14*(2*PLANE-3)`), "Y")})`,
    desc: "색 채널 분리 — 글리치·테크 느낌",
  },
  iris: { xfade: "circleopen", desc: "원형 아이리스 — 결과 공개" },
  glitch: (() => {
    // 가로 띠마다 다른 시점에 교체 + 띠 어긋남
    const band = "floor(Y/H*48)";
    const off = `(mod(${band}*73,17)-8)*${G}*6`;
    return {
      expr: `if(gt(P,mod(${band}*37,11)/11),${pick("a", clampX(`X+${off}`), "Y")},${pick("b", clampX(`X-${off}`), "Y")})`,
      desc: "디지털 글리치 — 오류·반전",
    };
  })(),
  "light-leak": (() => {
    // 우상단에서 따뜻한 빛이 번짐
    const k = `(${G}*clip(1-hypot(X/W-0.85,Y/H-0.12)*1.3,0,1))`;
    const m = mixAt("X", "Y", "X", "Y");
    return {
      expr: `if(eq(PLANE,0),clip(${m}+150*${k},0,255),if(eq(PLANE,1),clip(${m}-35*${k},0,255),clip(${m}+40*${k},0,255)))`,
      desc: "라이트 릭 — 감성·회상",
    };
  })(),
  "cross-warp": {
    // 이전 씬은 바깥으로 늘어나고 다음 씬은 늘어난 상태에서 제자리로
    expr: mixAt(clampX(`W/2+(X-W/2)*(0.6+0.4*P)`), "Y", clampX(`W/2+(X-W/2)*(1-1.6*(1-P)*P)`), "Y"),
    desc: "크로스 왜곡",
  },
  morph: { xfade: "dissolve", desc: "모핑(픽셀 디졸브 근사)" },
  "whoosh-left": { xfade: "smoothleft", desc: "휙 팬 ← (whoosh 효과음과 함께)" },
  "whoosh-right": { xfade: "smoothright", desc: "휙 팬 →" },
  "slide-up": { xfade: "slideup", desc: "위로 밀기 — 목록·다음 항목" },
  zoom: { xfade: "zoomin", desc: "시네마틱 줌 인" },
  "gravity-lens": (() => {
    // 중심으로 빨려 들어가는 핀치
    const f = `(1-${G}*0.45*clip(1-${R}/(W*0.75),0,1))`;
    return { expr: warp(`(X-W/2)*(${f}-1)`, `(Y-H/2)*(${f}-1)`), desc: "그래비티 렌즈 — 핀치" };
  })(),
  ripple: (() => {
    const d = `(sin(${R}/(W*0.02)-(1-P)*30)*${G}*W*0.012)`;
    return { expr: warp(d, d), desc: "물결 — 부드러운 전환" };
  })(),
  vortex: (() => {
    // 중심 가까울수록 크게 회전
    const a = `(${G}*2.2*clip(1-${R}/(W*0.9),0,1))`;
    const x = clampX(`W/2+(X-W/2)*cos(${a})-(Y-H/2)*sin(${a})`);
    const y = clampY(`H/2+(X-W/2)*sin(${a})+(Y-H/2)*cos(${a})`);
    return { expr: mixAt(x, y, x, y), desc: "소용돌이" };
  })(),
  heat: {
    expr: warp(`(sin(Y/(H*0.012)+(1-P)*25)*${G}*W*0.018)`, "0"),
    desc: "열 왜곡 — 아지랑이",
  },
  "noise-warp": (() => {
    const d = `((sin(X/W*23+Y/H*31)*cos(Y/H*17-X/W*7))*${G}*W*0.04)`;
    return { expr: warp(d, `${d}*0.6`), desc: "노이즈 공간 왜곡" };
  })(),
  burn: (() => {
    // 노이즈 경계로 타들어가며 교체, 경계선은 얇은 주황 불꽃
    const n = "((sin(X/W*19)*cos(Y/H*13)+sin((X/W+Y/H)*11))/4+0.5)";
    const px = `if(gt(${n},P),${pick("b", "X", "Y")},${pick("a", "X", "Y")})`;
    const e = `(clip(1-abs(${n}-P)*90,0,1)*${G})`;
    return {
      expr: `if(eq(PLANE,0),clip(${px}*(1-${e})+210*${e},0,255),if(eq(PLANE,1),clip(${px}-45*${e},0,255),clip(${px}+60*${e},0,255)))`,
      desc: "번 — 타들어가는 전환",
    };
  })(),
};
export const TRANSITIONS = Object.keys(TRANSITION_DEFS);

/** xfade 필터 인자 (transition=… 또는 transition=custom:expr=…) */
export function xfadeArgs(name) {
  const d = TRANSITION_DEFS[name];
  if (!d || name === "cut") throw new Error(`xfade 없는 트랜지션: ${name}`);
  if (d.xfade) return `transition=${d.xfade}`;
  return `transition=custom:expr='${d.expr.replace(/'/g, "\\'")}'`;
}

// ── 화면 효과 (scene.effects: ["scanlines", "vignette"]) ──────
// 입력/출력 모두 yuv420p 1080x1920. dur(초)는 소스 필터(gradients) 길이용.
const gray = (lumExpr) => `format=gray,geq=lum='${lumExpr}',format=yuv420p`;
export const EFFECT_DEFS = {
  blur: { f: () => "gblur=sigma=10", desc: "블러 — 배경화·포커스 아웃" },
  mosaic: { f: () => "pixelize=w=24:h=24", desc: "모자이크" },
  "color-bleed": { f: () => "chromashift=cbh=10:crh=-10:cbv=2", desc: "컬러 번짐 — 아날로그" },
  "tape-damage": {
    f: () => "rgbashift=rh=-5:bh=5,noise=alls=10:allf=t:all_seed=7,drawgrid=w=iw:h=6:t=2:c=black@0.25,eq=saturation=0.8,format=yuv420p",
    desc: "VHS 테이프 손상",
  },
  "film-dust": { f: () => "noise=alls=14:allf=t+u:all_seed=11", desc: "필름 먼지·그레인" },
  "film-damage": {
    f: () => "curves=preset=vintage,noise=alls=22:allf=t+u:all_seed=13,vignette=PI/4.5,format=yuv420p",
    desc: "낡은 필름 — 회상",
  },
  halftone: { f: () => gray("if(gt(lum(X,Y),127.5*(1+sin(X*PI/4)*sin(Y*PI/4))),235,20)"), desc: "하프톤 망점" },
  duotone: {
    f: () => "format=gray,format=rgb24,curves=r='0/0.10 1/1':g='0/0.05 1/0.85':b='0/0.35 1/0.45',format=yuv420p",
    desc: "듀오톤 인쇄 (네이비→옐로)",
  },
  dither: {
    f: () => gray("if(gt(lum(X,Y),255*(mod(X,2)*2+mod(Y,2)*3-4*mod(X,2)*mod(Y,2)+0.5)/4),235,20)"),
    desc: "디더링 (2x2 Bayer)",
  },
  "light-flare": {
    src: (dur) => `gradients=s=1080x1920:c0=0xffd9a0:c1=0x000000:x0=930:y0=180:x1=240:y1=1500:type=radial:d=${dur}:r=30:speed=0`,
    blend: "screen:all_opacity=0.55",
    desc: "라이트 플레어",
  },
  monochrome: { f: () => "hue=s=0", desc: "흑백" },
  scanlines: { f: () => "drawgrid=w=iw:h=4:t=1:c=black@0.35", desc: "스캔라인" },
  "chromatic-aberration": { f: () => "rgbashift=rh=-8:bh=8:rv=2,format=yuv420p", desc: "색수차" },
  crt: {
    f: () => "lenscorrection=k1=0.08:k2=0.04,vignette=PI/4,drawgrid=w=iw:h=4:t=1:c=black@0.3,eq=contrast=1.1,format=yuv420p",
    desc: "CRT 곡면 모니터",
  },
  "digital-glitch": {
    // 0.125초마다 바뀌는 가로 띠 어긋남 (T 기반 — 결정적)
    f: () =>
      "geq=lum='lum(X+if(lt(mod(Y+floor(T*8)*53,97),9),28,0),Y)':cb='cb(X+if(lt(mod(Y*2+floor(T*8)*53,97),9),14,0),Y)':cr='cr(X-if(lt(mod(Y*2+floor(T*8)*29,89),7),12,0),Y)',rgbashift=rh=-6:bh=6,format=yuv420p",
    desc: "디지털 글리치",
  },
  woodblock: {
    f: () => "edgedetect=mode=colormix:high=0.25:low=0.08,lutyuv=y='floor(val/64)*64+24',hue=s=0.6",
    desc: "목판화 근사 (윤곽+포스터화)",
  },
  "cross-hatch": {
    f: () =>
      // 아주 어두운 곳은 먹칠, 중간톤은 3겹 빗금 (다크 테마에서도 글자 대비 유지)
      gray("if(lt(lum(X,Y),35),25,if(lt(lum(X,Y),70)*lt(mod(X,4),1)+lt(lum(X,Y),120)*lt(mod(X-Y,6),1)+lt(lum(X,Y),175)*lt(mod(X+Y,6),1),25,235))"),
    desc: "크로스 해칭 펜화",
  },
  painterly: { f: () => "gblur=sigma=2,edgedetect=mode=colormix:high=0,eq=saturation=1.3", desc: "회화풍 근사" },
  vignette: { f: () => "vignette=PI/4", desc: "비네트 — 시선 집중" },
};
export const EFFECTS = Object.keys(EFFECT_DEFS);

/**
 * [in] 에 효과 체인을 적용해 [out] 을 만드는 filter_complex 조각 목록
 * @returns {string[]}
 */
export function effectFilters(names, inLabel, outLabel, dur) {
  if (!names?.length) return [`[${inLabel}]null[${outLabel}]`];
  const parts = [];
  let cur = inLabel;
  names.forEach((n, j) => {
    const d = EFFECT_DEFS[n];
    const next = j === names.length - 1 ? outLabel : `${outLabel}_${j}`;
    if (d.src) {
      parts.push(`${d.src(dur)},format=gbrp[${next}_g]`);
      parts.push(`[${cur}]format=gbrp[${next}_b]`);
      parts.push(`[${next}_b][${next}_g]blend=all_mode=${d.blend},format=yuv420p[${next}]`);
    } else {
      parts.push(`[${cur}]${d.f()},scale=1080:1920,setsar=1,format=yuv420p[${next}]`);
    }
    cur = next;
  });
  return parts;
}
