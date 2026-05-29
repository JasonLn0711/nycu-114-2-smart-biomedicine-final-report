import {
  Audio,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
} from "remotion";
import { FPS, scenes } from "./scenes";

export const FinalReportVideo = () => {
  return (
    <>
      <Audio src={staticFile("audio/narration.wav")} />
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={Math.round(scene.start * FPS)}
          durationInFrames={Math.round(scene.duration * FPS)}
        >
          <Scene image={scene.image} caption={scene.caption} captionZh={scene.captionZh} />
        </Sequence>
      ))}
    </>
  );
};

const Scene = ({
  image,
  caption,
  captionZh,
}: {
  image: string;
  caption: string;
  captionZh: string;
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 360], [1, 1.055], {
    extrapolateRight: "clamp",
  });
  const opacity = interpolate(frame, [0, 18], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#fbfbf8",
        overflow: "hidden",
        position: "relative",
        fontFamily:
          'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      <Img
        src={staticFile(image)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "center",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 72,
          right: 72,
          bottom: 54,
          opacity,
          padding: "22px 30px",
          background: "rgba(255,255,255,0.88)",
          border: "1px solid rgba(40,40,34,0.12)",
          borderRadius: 8,
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
        }}
      >
        <div
          style={{
            fontSize: 38,
            lineHeight: 1.22,
            color: "#1e1e1a",
            fontWeight: 650,
            letterSpacing: 0,
          }}
        >
          {caption}
        </div>
        <div
          style={{
            marginTop: 10,
            fontSize: 25,
            lineHeight: 1.28,
            color: "#4c514a",
            letterSpacing: 0,
          }}
        >
          {captionZh}
        </div>
      </div>
    </div>
  );
};
