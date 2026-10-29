"""Create a neutral profile and normalize another recording."""

from __future__ import annotations

import argparse

from sk_speech import PitchExtractor, calibrate_pitch, normalize_pitch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("neutral_audio")
    parser.add_argument("--audio", help="Optional recording to normalize")
    parser.add_argument("--profile", default="pitch_profile.json")
    parser.add_argument("--output", default="normalized_pitch.csv")
    args = parser.parse_args()

    extractor = PitchExtractor()
    profile = calibrate_pitch(extractor.from_file(args.neutral_audio))
    profile_path = profile.save(args.profile)
    print(f"profile: {profile_path.resolve()}")
    print(f"neutral F0: {profile.mean_f0_hz:.3f} Hz")
    print(f"neutral intensity: {profile.mean_intensity_db:.3f} dB")

    if args.audio:
        normalized = normalize_pitch(extractor.from_file(args.audio), profile)
        output = normalized.to_csv(args.output)
        print(f"normalized sequence: {output.resolve()}")


if __name__ == "__main__":
    main()

