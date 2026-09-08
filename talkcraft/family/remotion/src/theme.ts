// 구리 태극기 파생 토큰 — 페이퍼 콜라주: 크림 종이 바탕 + 태극 홍/청 + 계측선 레드
export const C = {
  bg: '#F5EFE2',
  bgPanel: 'rgba(255, 252, 244, 0.94)',
  gold: '#D6323C',            // 카드 재사용 키 — 값은 태극 홍(계측선 겸용)
  red: '#D6323C',
  blue: '#20409A',
  green: '#7BA05B',
  paper: '#FFFDF6',
  text: '#2B2B33',
  dim: '#8A8578',
  line: 'rgba(43, 43, 51, 0.06)',
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
