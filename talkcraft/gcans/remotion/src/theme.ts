// G-Cans 파생 토큰 — 건축쇼츠: 콘크리트 다크 + 빨간 계측선 단일 강조 + 물 티일
export const C = {
  bg: '#0B0F14',
  bgPanel: 'rgba(18, 24, 32, 0.9)',
  gold: '#FF3B30',            // 카드 재사용을 위해 키 이름 유지 — 값은 계측선 레드
  red: '#FF3B30',
  teal: '#3DA8BC',
  concrete: '#B9B2A6',
  soil: '#6B5138',
  text: '#F2F5F7',
  dim: '#8FA0AD',
  line: 'rgba(185, 178, 166, 0.10)',
};

export const FONT = {
  kr: 'Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif',
  mono: 'Menlo, "SF Mono", monospace',
};

export const FONT_FACE_CSS = `
@font-face { font-family: 'Pretendard'; src: url('fonts/Pretendard-Bold.ttf') format('truetype'); font-weight: 700 800; }
@font-face { font-family: 'Pretendard'; src: url('fonts/Pretendard-SemiBold.ttf') format('truetype'); font-weight: 400 600; }
`;

export const gridBg: React.CSSProperties = {
  backgroundColor: C.bg,
  backgroundImage:
    `linear-gradient(${C.line} 1px, transparent 1px),` +
    `linear-gradient(90deg, ${C.line} 1px, transparent 1px)`,
  backgroundSize: '72px 72px',
};
