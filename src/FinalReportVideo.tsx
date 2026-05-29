import {
  Audio,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
} from "remotion";
import { FPS, scenes, type Scene as SceneData } from "./scenes";

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
          <Scene scene={scene} />
        </Sequence>
      ))}
    </>
  );
};

const Scene = ({ scene }: { scene: SceneData }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 360], [1, 1.055], {
    extrapolateRight: "clamp",
  });
  const opacity = interpolate(frame, [0, 18], [0, 1], {
    extrapolateRight: "clamp",
  });
  const hasSourceImages = Boolean(scene.sourceImages?.length);

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
        src={staticFile(scene.image)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "center",
          opacity: hasSourceImages ? 0.2 : 1,
        }}
      />
      {hasSourceImages && <SourceFigurePanel scene={scene} />}
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
          {scene.caption}
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
          {scene.captionZh}
        </div>
      </div>
    </div>
  );
};

const SourceFigurePanel = ({ scene }: { scene: SceneData }) => {
  const isPair = scene.sourceImages?.length === 2;

  return (
    <div
      style={{
        position: "absolute",
        top: 56,
        left: 68,
        right: 68,
        bottom: 230,
        display: "flex",
        gap: 26,
        alignItems: "stretch",
        justifyContent: "center",
      }}
    >
      {scene.sourceImages?.map((source) => (
        <div
          key={source.src}
          style={{
            flex: isPair ? 1 : "0 1 72%",
            minWidth: 0,
            display: "flex",
            flexDirection: "column",
            background: "rgba(255,255,255,0.96)",
            border: "1px solid rgba(30,30,26,0.16)",
            borderRadius: 8,
            overflow: "hidden",
            boxShadow: "0 16px 40px rgba(0,0,0,0.14)",
          }}
        >
          <div
            style={{
              flex: 1,
              minHeight: 0,
              padding: 18,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "#ffffff",
            }}
          >
            <Img
              src={staticFile(source.src)}
              style={{
                maxWidth: "100%",
                maxHeight: "100%",
                width: "100%",
                height: "100%",
                objectFit: source.fit ?? "contain",
              }}
            />
          </div>
          <div
            style={{
              padding: "13px 18px",
              fontSize: isPair ? 24 : 27,
              lineHeight: 1.2,
              color: "#34342f",
              background: "#f4f4ef",
              borderTop: "1px solid rgba(30,30,26,0.12)",
              letterSpacing: 0,
            }}
          >
            {source.label}
          </div>
        </div>
      ))}
    </div>
  );
};
