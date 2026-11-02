from __future__ import annotations

import numpy as np

from sk_speech import sk_vowels


def test_formant_masks_cover_expected_frequency_bins():
    frequencies = np.array([50, 100, 150, 200, 250], dtype=float)

    amplitude_mask = sk_vowels.create_formant_mask_amplitude(frequencies, [150], bandwidth=50)
    energy_mask = sk_vowels.create_formant_mask_energy(frequencies, [150], bandwidth=50)
    range_mask = sk_vowels.create_formant_mask_low_high(frequencies, 100, 200)

    np.testing.assert_array_equal(amplitude_mask, [False, False, True, False, False])
    np.testing.assert_array_equal(energy_mask, [False, True, True, True, False])
    np.testing.assert_array_equal(range_mask, energy_mask)


def test_vowel_grouping_missing_and_closest_selection():
    boundaries = [(100, "a"), (200, "i"), (300, "a")]

    assert sk_vowels.group_vowels(boundaries) == ["a", "i"]
    assert sk_vowels.find_missing_vowels(boundaries) == {"e", "o", "u"}
    assert sk_vowels.find_closest_vowel(
        ["a", "i"],
        {"a": {"f1": np.nan, "f2": 2.0}, "i": {"f1": 1.0, "f2": 2.0}},
    ) == "i"


def test_determine_vowel_type_uses_frame_neighbourhood():
    boundaries = [(1_000, "a"), (4_000, "i")]

    assert sk_vowels.determine_vowel_type(1_200, boundaries, 16_000, frame_duration=0.05) == "a"
    assert sk_vowels.determine_vowel_type(2_500, boundaries, 16_000, frame_duration=0.05) == "unknown"


def test_formant_shift_is_noop_when_all_shifts_are_zero():
    signal = np.linspace(-0.5, 0.5, 1_600)
    result = sk_vowels.apply_formant_shifts_vowels(
        signal,
        16_000,
        [(400, "a")],
        {"a": [0, 0, 0, 0, 0]},
    )

    np.testing.assert_array_equal(result, signal)


def test_smooth_stretch_applies_hann_envelope(monkeypatch):
    monkeypatch.setattr(
        sk_vowels.librosa.effects,
        "time_stretch",
        lambda y, rate: np.ones(round(len(y) / rate)),
    )

    result = sk_vowels.smooth_stretch_vowel(np.ones(4), 16_000, stretch_factor=2.0)

    assert len(result) == 8
    assert result[0] == 0
    assert result[-1] == 0
    assert np.max(result) > 0.9


def test_wsola_returns_requested_length_and_finite_samples():
    signal = np.sin(2 * np.pi * 0.01 * np.arange(4096))
    result = sk_vowels.wsola(signal, 16_000, speed_factor=1.5, frame_size=512, hop_size=128)

    assert result.shape == (6144,)
    assert result.dtype == np.float32
    assert np.isfinite(result).all()
