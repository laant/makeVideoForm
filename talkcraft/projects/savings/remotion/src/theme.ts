// AI 사고력 1편 파생 토큰 — 클레이 다크: 차콜 스튜디오 + 부정 레드 + 정답 웜 글로우
export const C = {
  bg: '#111318',
  bgPanel: 'rgba(24, 27, 34, 0.92)',
  gold: '#FFB84D',            // 카드 재사용 키 — 값은 웜 글로우(정답 전용)
  red: '#FF3B30',             // 부정 신호 전용
  warm: '#FFB84D',
  clay: '#9AA1AB',            // 찰흙 회색
  clayDim: '#5E656F',
  text: '#F2F5F7',
  dim: '#8FA0AD',
  line: 'rgba(154, 161, 171, 0.08)',
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

import type React from 'react';
