import React from "react";
import { Composition } from "remotion";
import { Main, TOTAL_FRAMES, FPS } from "./Main";

export const Root: React.FC = () => (
  <Composition id="Savings" component={Main} durationInFrames={TOTAL_FRAMES}
               fps={FPS} width={1080} height={1920} />
);
