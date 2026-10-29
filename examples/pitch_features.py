"""Extract an aligned F0/intensity sequence from one audio file."""

from __future__ import annotations

import argparse

from sk_speech import PitchConfig, PitchExtractor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("--output", default="pitch_features.csv")
    parser.add_argument("--sample-rate", type=int, default=16_000)
    parser.add_argument("--frame-step", type=float, default=0.01)
    parser.add_argument("--pitch-floor", type=float, default=50.0)
    parser.add_argument("--pitch-ceiling", type=float, default=800.0)
    args = parser.parse_args()

    extractor = PitchExtractor(
        PitchConfig(
            sample_rate=args.sample_rate,
            frame_step_s=args.frame_step,
            pitch_floor_hz=args.pitch_floor,
            pitch_ceiling_hz=args.pitch_ceiling,
        )
    )
    track = extractor.from_file(args.audio)
    output = track.to_csv(args.output)
    print(f"frames: {len(track.time_s)}")
    print(f"voiced frames: {int(track.voiced.sum())}")
    print(f"output: {output.resolve()}")


if __name__ == "__main__":
    main()

