from __future__ import annotations

import numpy as np
import pytest

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


class _FakeFormants:
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2

    def ts(self):
        return [0.01, 0.02]

    def get_value_at_time(self, index, time):
        return self.f1 if index == 1 else self.f2


class _FakeSound:
    values = (500.0, 1_500.0)

    def __init__(self, *args, **kwargs):
        pass

    def to_formant_burg(self, **kwargs):
        return _FakeFormants(*self.values)


@pytest.mark.parametrize(
    ("f1", "f2", "expected"),
    [(400, 1800, "i"), (400, 1500, "u"), (600, 900, "o"), (600, 1500, "a"), (900, 1500, "e")],
)
def test_compute_vowel_type_covers_formant_regions(monkeypatch, f1, f2, expected):
    _FakeSound.values = (f1, f2)
    monkeypatch.setattr(sk_vowels.pm, "Sound", _FakeSound)
    monkeypatch.setattr(sk_vowels.librosa.feature, "mfcc", lambda **kwargs: np.zeros((13, 2)))

    midpoint, vowel = sk_vowels.compute_vowel_type(np.ones(1000), 1000, 100, 300, 25, 10)
    assert midpoint == 2000
    assert vowel == expected


def test_vowel_boundary_detectors_build_segments(monkeypatch):
    monkeypatch.setattr(sk_vowels.fl, "normalize_audio", lambda y: np.asarray(y))
    monkeypatch.setattr(
        sk_vowels.librosa.feature,
        "rms",
        lambda **kwargs: np.array([[0.0, 0.2, 0.2, 0.0, 0.3]]),
    )
    monkeypatch.setattr(
        sk_vowels.librosa.feature,
        "zero_crossing_rate",
        lambda **kwargs: np.array([[0.2, 0.05, 0.05, 0.2, 0.05]]),
    )
    monkeypatch.setattr(sk_vowels.librosa.feature, "mfcc", lambda **kwargs: np.zeros((13, 2)))
    _FakeSound.values = (600, 1500)
    monkeypatch.setattr(sk_vowels.pm, "Sound", _FakeSound)

    boundaries = sk_vowels.detect_vowel_boundaries(np.ones(2_000), 1_000)
    assert boundaries == [(20, "a"), (40, "a")]

    boundaries2 = sk_vowels.detect_vowel_boundaries2(np.ones(2_000), 1_000)
    assert boundaries2 == [(20, "e"), (40, "e")]


def test_parallel_vowel_detector_collects_worker_results(monkeypatch):
    monkeypatch.setattr(sk_vowels.fl, "normalize_audio", lambda y: np.asarray(y))
    monkeypatch.setattr(
        sk_vowels.librosa.feature,
        "rms",
        lambda **kwargs: np.array([[0.0, 0.2, 0.2, 0.0]]),
    )
    monkeypatch.setattr(
        sk_vowels.librosa.feature,
        "zero_crossing_rate",
        lambda **kwargs: np.array([[0.2, 0.05, 0.05, 0.2]]),
    )
    monkeypatch.setattr(sk_vowels, "compute_vowel_type", lambda *args: (20, "i"))
    assert sk_vowels.detect_vowel_boundaries_parallel(np.ones(1_000), 1_000) == [(20, "i")]


def test_formant_frequency_and_vowel_aggregations(monkeypatch):
    boundaries = [(100, "a"), (200, "a")]
    analyses = [
        {"frequencies": [[400, 600], [1500], [2500], [3500], [np.nan]]},
        {"frequencies": [[600], [1700], [2700], [3700], [4700]]},
    ]
    means = sk_vowels.calculate_formant_freq(np.ones(500), 100, boundaries, analyses)
    assert means[0][:4] == pytest.approx([500, 1500, 2500, 3500])
    assert means[0][4] is None

    formant_values = {f"f{i}": [float(i), float(i + 2)] for i in range(1, 6)}
    monkeypatch.setattr(sk_vowels, "calculate_formant_amplitude", lambda *args, **kwargs: formant_values)
    amplitudes = sk_vowels.mean_amplitude_dB_for_vowels(
        np.ones(500), 100, boundaries, formants=analyses
    )
    assert amplitudes["a"]["f1"] == pytest.approx(2.0)
    assert set(amplitudes) == {"a", "e", "i", "o", "u"}

    monkeypatch.setattr(sk_vowels, "calculate_formant_energy", lambda *args, **kwargs: formant_values)
    energies = sk_vowels.mean_energy_for_vowels(np.ones(500), 100, boundaries, formants=analyses)
    assert energies["a"]["f5"] == pytest.approx(6.0)

    monkeypatch.setattr(sk_vowels, "calculate_formant_freq", lambda *args, **kwargs: means)
    frequencies = sk_vowels.mean_formants_for_vowels(np.ones(500), 100, boundaries, analyses)
    assert frequencies["a"]["f1"] == pytest.approx(550.0)
    assert frequencies["a"]["f5"] == pytest.approx(4700.0)


def test_vowel_formant_info_preserves_analysis_fields(monkeypatch):
    expected = ([[500.0]], [0.01], [[80.0]], [60.0])
    monkeypatch.setattr(sk_vowels.fmt, "formant_frequencies", lambda *args: expected)
    result = sk_vowels.get_vowel_formant_info(np.ones(1_000), 1_000, [(200, "a"), (600, "i")])

    assert len(result) == 2
    assert result[0] == {
        "frequencies": expected[0],
        "voiced_times": expected[1],
        "bandwidths": expected[2],
        "intensities": expected[3],
    }


def test_shift_formants_vowels_loads_applies_and_writes(monkeypatch):
    signal = np.array([0.1, -0.1])
    written = {}
    monkeypatch.setattr(sk_vowels.librosa, "load", lambda path, sr=None: (signal, 16_000))
    monkeypatch.setattr(sk_vowels, "apply_formant_shifts_vowels", lambda *args, **kwargs: signal * 2)
    monkeypatch.setattr(
        sk_vowels.sf,
        "write",
        lambda path, data, sr: written.update(path=path, data=np.asarray(data), sr=sr),
    )

    result = sk_vowels.shift_formants_vowels("in.wav", "out.wav", [(10, "a")], {"a": [1] * 5})
    assert result is None
    assert written["path"] == "out.wav"
    assert written["sr"] == 16_000
    np.testing.assert_allclose(written["data"], signal * 2)


@pytest.mark.parametrize(
    "function_name,extra_kwargs",
    [
        ("stretch_vowels_preserve_pitch", {}),
        ("stretch_vowels_preserve_pitch2", {}),
        ("stretch_vowels_preserve_pitch3", {}),
        ("stretch_vowels_preserve_pitch4", {"filter_size": 1}),
        ("stretch_vowels_preserve_pitch5", {"cutoff_freq": 4.0}),
    ],
)
def test_vowel_stretch_variants_preserve_non_vowel_regions(
    monkeypatch, function_name, extra_kwargs
):
    signal = np.arange(20, dtype=float)

    def fake_stretch(y, rate):
        return np.repeat(y, round(1 / rate))

    monkeypatch.setattr(sk_vowels.librosa.effects, "time_stretch", fake_stretch)
    monkeypatch.setattr(sk_vowels, "butter_lowpass_filter", lambda data, **kwargs: np.asarray(data))

    function = getattr(sk_vowels, function_name)
    result = function(
        signal,
        10,
        [(10, "a")],
        delta_seconds=0.2,
        speed_factor=2.0,
        **extra_kwargs,
    )

    assert len(result) == 24
    np.testing.assert_array_equal(result[:8], signal[:8])
    np.testing.assert_array_equal(result[-8:], signal[-8:])


def test_butter_lowpass_filter_delegates_to_scipy(monkeypatch):
    monkeypatch.setattr(sk_vowels, "butter", lambda *args, **kwargs: ([1.0], [1.0]))
    monkeypatch.setattr(sk_vowels, "lfilter", lambda b, a, data: np.asarray(data) * 2)
    np.testing.assert_array_equal(
        sk_vowels.butter_lowpass_filter(np.array([1.0, 2.0]), 100.0, 1_000),
        [2.0, 4.0],
    )
