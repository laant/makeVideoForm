// 본편 파생 토큰 — design-language Apple 범식에서 파생 (돈 주제: 다크 네이비 + 금색 단일 강조)
export const C = {
  bg: '#0A0E1A',
  bgPanel: 'rgba(16, 22, 38, 0.9)',
  gold: '#FFC94D',
  red: '#FF5A6E',
  text: '#F2F5FC',
  dim: '#93A1BD',
  line: 'rgba(255, 201, 77, 0.13)',
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
