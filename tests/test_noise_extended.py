from __future__ import annotations

import numpy as np
import pytest

from sk_speech import sk_noise


def test_normalize_and_noise_gate():
    assert sk_noise.normalize(5.0, 0.0, 10.0) == 0.5
    signal = np.array([0.05, 0.2, -1.0])
    np.testing.assert_array_equal(
        sk_noise.apply_noise_reduction(signal, noise_reduction_factor=0.1),
        [0.0, 0.2, -1.0],
    )


def test_power_spectral_density_of_silence_is_finite():
    frequencies, psd = sk_noise.compute_power_spectral_density(
        np.zeros(2_048), 16_000, n_fft=512, hop_length=128
    )

    assert len(frequencies) == len(psd) == 257
    assert np.isfinite(psd).all()
    assert np.all(psd == 0)


def test_noise_psd_analysis_uses_outside_speech_band(monkeypatch):
    monkeypatch.setattr(
        sk_noise,
        "compute_power_spectral_density",
        lambda *args, **kwargs: (np.array([100, 1_000, 5_000]), np.array([1e-2, 1.0, 1e-2])),
    )

    present, level_db = sk_noise.analyze_noise_in_psd(np.ones(8), 16_000, noise_threshold_db=-30)
    assert present
    assert level_db == pytest.approx(-20.0)


def test_spectral_subtraction_rejects_unknown_estimator(monkeypatch):
    monkeypatch.setattr(sk_noise.librosa, "stft", lambda *args, **kwargs: np.ones((3, 2), dtype=complex))

    with pytest.raises(ValueError, match="Неизвестный метод"):
        sk_noise.spectral_subtraction(np.ones(16), 16_000, noise_estimation_method="unknown")


def test_add_noise_is_reproducible_with_seed():
    signal = np.zeros(10)
    np.random.seed(42)
    first = sk_noise.add_noise(signal, 0.01)
    np.random.seed(42)
    second = sk_noise.add_noise(signal, 0.01)

    np.testing.assert_array_equal(first, second)
    assert np.any(first != 0)


def test_remove_noise_dispatches_arguments(monkeypatch):
    calls = {}
    monkeypatch.setattr(sk_noise.fl, "normalize_audio", lambda y: y + 1)
    monkeypatch.setattr(
        sk_noise.fl,
        "apply_low_pass_filter",
        lambda y, sr, cutoff: calls.update(y=y, sr=sr, cutoff=cutoff) or y,
    )

    result = sk_noise.remove_noise(np.zeros(4), 16_000, method="lowpass", cutoff_freq=2_000)
    np.testing.assert_array_equal(result, np.ones(4))
    assert calls["sr"] == 16_000
    assert calls["cutoff"] == 2_000
    with pytest.raises(ValueError, match="Unknown method"):
        sk_noise.remove_noise(np.zeros(4), 16_000, method="missing")


def test_composite_noise_analysis_combines_normalized_components(monkeypatch):
    monkeypatch.setattr(sk_noise, "analyze_noise_level_rms", lambda *args, **kwargs: (True, -40.0))
    monkeypatch.setattr(sk_noise, "analyze_noise_level_sf", lambda *args, **kwargs: (False, 0.5))
    monkeypatch.setattr(sk_noise, "analyze_noise_in_psd", lambda *args, **kwargs: (True, -20.0))

    result = sk_noise.analyze_noise_level(np.ones(8), 16_000)
    assert result["is_noisy_rms"] is True
    assert result["is_noisy_flatness"] is False
    assert result["combined_noise_level"] == pytest.approx((0.5 + 0.5 + 0.75) / 3)
