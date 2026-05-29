import { Composition } from "remotion";
import { FinalReportVideo } from "./FinalReportVideo";
import { FPS, TOTAL_FRAMES } from "./scenes";

export const RemotionRoot = () => {
  return (
    <Composition
      id="FinalReportVideo"
      component={FinalReportVideo}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
