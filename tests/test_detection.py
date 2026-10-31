from __future__ import annotations

import numpy as np

from sk_speech import sk_detection


def _f0_result(f0=(120.0, 130.0, 140.0), intensity=(85.0, 86.0, 84.0)):
    f0_values = np.asarray(f0, dtype=float)
    times = np.arange(len(f0_values), dtype=float) * 0.01
    intensity_values = np.asarray(intensity, dtype=float)
    return f0_values, times, intensity_values, times, None, None, None


def _patch_common(monkeypatch, *, f0=(120.0, 130.0, 140.0), intensity=(85.0, 86.0, 84.0)):
    monkeypatch.setattr(
        sk_detection.ns,
        "noise_reduction_spectral_subtraction",
        lambda y, sr, **kwargs: y,
    )
    monkeypatch.setattr(
        sk_detection.ns,
        "noise_reduction_spectral_subtraction_fast",
        lambda y, sr, **kwargs: y,
    )
    monkeypatch.setattr(
        sk_detection.pt,
        "extract_f0_voiced",
        lambda y, sr: _f0_result(f0=f0, intensity=intensity),
    )
    monkeypatch.setattr(
        sk_detection.pt,
        "remove_short_sequences",
        lambda values, min_length: np.asarray(values),
    )
    monkeypatch.setattr(
        sk_detection.pt,
        "calculate_pitch_intensity",
        lambda y, sr, only_speech: np.asarray(intensity, dtype=float),
    )
    monkeypatch.setattr(
        sk_detection.fmt,
        "extract_formants_from_segment_fast",
        lambda y, sr: [500.0, 1500.0],
    )
    monkeypatch.setattr(
        sk_detection.librosa.feature,
        "spectral_flatness",
        lambda y: np.array([[0.1]], dtype=float),
    )


def test_speech_mode_detectors_accept_full_f0_result(monkeypatch):
    _patch_common(monkeypatch)
    audio = np.ones(2048, dtype=float)

    assert sk_detection.is_soft_speech(audio, 16_000, intensity_max_db=90)
    assert sk_detection.is_loud_speech(audio, 16_000, intensity_threshold_db=80)
    assert not sk_detection.is_whisper(audio, 16_000, f0_avg=100)


def test_scream_uses_intensity_and_configured_f0_bounds(monkeypatch):
    audio = np.ones(2048, dtype=float)

    _patch_common(monkeypatch, f0=(420.0, 440.0, 460.0), intensity=(85.0, 86.0, 84.0))
    assert sk_detection.is_scream(audio, 16_000)
    assert not sk_detection.is_scream(audio, 16_000, min_f0=450.0)
    assert not sk_detection.is_scream(audio, 16_000, max_f0=430.0)
    assert not sk_detection.is_scream(audio, 16_000, intensity_threshold_db=90.0)
