from __future__ import annotations

import json

import numpy as np
import pytest

from sk_speech import PitchConfig, PitchExtractor, PitchProfile, calibrate_pitch, normalize_pitch


def sine(frequency: float = 220.0, amplitude: float = 0.2, seconds: float = 1.0, sr: int = 16_000):
    time = np.arange(round(seconds * sr)) / sr
    return amplitude * np.sin(2 * np.pi * frequency * time), sr


def test_pitch_and_intensity_are_aligned():
    audio, sr = sine()
    track = PitchExtractor(PitchConfig(sample_rate=sr)).extract(audio, sr)

    assert len(track.time_s) == len(track.f0_hz) == len(track.intensity_db) == len(track.voiced)
    assert track.voiced.any()
    assert np.nanmedian(track.f0_hz) == pytest.approx(220.0, abs=2.0)
    assert np.isfinite(track.intensity_db[track.voiced]).all()


def test_profile_round_trip_and_normalization(tmp_path):
    neutral_audio, sr = sine(200.0, 0.1)
    current_audio, _ = sine(240.0, 0.2)
    extractor = PitchExtractor(PitchConfig(sample_rate=sr))
    profile = calibrate_pitch(extractor.extract(neutral_audio, sr))

    path = profile.save(tmp_path / "profile.json")
    loaded = PitchProfile.load(path)
    relative = normalize_pitch(extractor.extract(current_audio, sr), loaded)

    assert json.loads(path.read_text())["mean_f0_hz"] > 0
    assert np.nanmedian(relative.f0_relative) == pytest.approx(0.2, abs=0.03)
    assert np.nanmedian(relative.intensity_delta_db) > 5.0


def test_empty_audio_has_empty_track():
    track = PitchExtractor().extract(np.empty(0), 16_000)
    assert track.time_s.size == 0
    assert track.f0_hz.size == 0

