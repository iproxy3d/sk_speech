from __future__ import annotations

import numpy as np
import pytest

from sk_speech import sk_formants


def test_formant_range_and_index_validation(monkeypatch):
    monkeypatch.setattr(
        sk_formants,
        "extract_formants",
        lambda signal, sr, formants=None: [500.0, 1500.0, 2500.0, 3500.0, 4500.0],
    )

    assert sk_formants.formant_range(1) == 1200
    assert sk_formants.get_formant_frequency_by_index(np.zeros(8), 16_000, 3) == 2500.0
    with pytest.raises(ValueError, match="между 1 и 5"):
        sk_formants.get_formant_frequency_by_index(np.zeros(8), 16_000, 0)


def test_remove_outliers_preserves_regular_values_and_nan_only_input():
    cleaned = sk_formants.remove_outliers([10.0, 11.0, 12.0, 13.0, 1000.0])
    np.testing.assert_array_equal(cleaned, [10.0, 11.0, 12.0, 13.0])

    nan_only = sk_formants.remove_outliers([np.nan, np.nan])
    assert len(nan_only) == 2
    assert np.isnan(nan_only).all()


def test_calculate_formant_bandwidth_supports_max_and_mean():
    bandwidths = [[10.0, 20.0, 30.0, 1000.0], [], [], [], []]

    assert sk_formants.calculate_formant_bandwidth_(bandwidths, 1, method="max") == 30.0
    assert sk_formants.calculate_formant_bandwidth_(bandwidths, 1, method="mean") == 20.0
    assert sk_formants.calculate_formant_bandwidth_(bandwidths, 2) == 0
    with pytest.raises(ValueError, match="между 1 и 5"):
        sk_formants.calculate_formant_bandwidth_(bandwidths, 6)


def test_segment_duration_handles_zero_and_bounds_large_shifts():
    assert sk_formants.calculate_segment_duration([0, 0, 0]) == pytest.approx(0.0025)
    assert sk_formants.calculate_segment_duration([0], base_duration=0.001) == pytest.approx(0.001)

    value = sk_formants.calculate_segment_duration([500, -200])
    assert np.isfinite(value)
    assert 0.0007 <= value <= 0.0025


@pytest.mark.parametrize("shifts", [[], [np.nan], [np.inf]])
def test_segment_duration_rejects_missing_or_non_finite_shifts(shifts):
    with pytest.raises(ValueError, match="formant_shifts"):
        sk_formants.calculate_segment_duration(shifts)


def test_segment_smoothing_and_pattern_classification():
    segments = sk_formants.segment_and_smooth(np.array([1, 2, 3, 3, 2, 1], dtype=float), 2)
    np.testing.assert_allclose(segments[0], [1, 2, 3])
    np.testing.assert_allclose(segments[1], [3, 2, 1])

    patterns = sk_formants.analyze_formant_patterns(
        frequencies=[[500, 510, 520, 520, 510, 500]],
        bandwidths=[[100, 102, 104, 104, 102, 100]],
        formant_ranges={1: (200, 1400)},
        num_segments=2,
        eps_freq=0.1,
        eps_width=0.1,
    )
    assert patterns == [([1, -1], [1, -1])]


def test_find_peak_time_and_generate_signal_shape():
    assert sk_formants.find_max_formant_energy_time([]) == 0
    assert sk_formants.find_max_formant_energy_time([(1.0, 0.1), (3.0, 0.2), (2.0, 0.3)]) == 0.2

    signal = sk_formants.generate_varying_bandwidth_signal(
        0.02, 200.0, 400.0, 0.5, 1.0, sample_rate=8_000
    )
    assert signal.dtype == np.int16
    assert signal.shape == (160,)
    assert np.max(np.abs(signal)) > 0


def test_formant_retry_strategy_and_exhaustion(monkeypatch):
    monkeypatch.setattr(sk_formants.pm, "PraatError", RuntimeError)

    class EventuallyWorkingSound:
        def __init__(self):
            self.steps = []

        def to_formant_burg(self, *, time_step, **kwargs):
            self.steps.append(time_step)
            if len(self.steps) < 3:
                raise RuntimeError("Praat failed")
            return "formants"

    sound = EventuallyWorkingSound()
    assert sk_formants.get_formants_with_retries(sound) == "formants"
    assert sound.steps == pytest.approx([0.01, 0.1, 1.0])

    class BrokenSound:
        def to_formant_burg(self, **kwargs):
            raise RuntimeError("Praat failed")

    assert sk_formants.get_formants_with_retries(BrokenSound()) is None


def test_alternative_formant_extractors_and_invalid_method(monkeypatch):
    expected = ([[500.0]], np.array([0.0]), [[80.0]], [60.0])
    monkeypatch.setattr(sk_formants, "formant_frequencies", lambda *args, **kwargs: expected)
    assert sk_formants.analyze_formants_alternative(np.ones(8), 8_000, method="praat") == expected

    monkeypatch.setattr(
        sk_formants,
        "extract_formants_via_lpc",
        lambda *args, **kwargs: ([[510.0]], np.array([0.0, 0.1])),
    )
    frequencies, times, bandwidths, intensities = sk_formants.analyze_formants_alternative(
        np.ones(8), 8_000, method="lpc"
    )
    assert frequencies == [[510.0]]
    np.testing.assert_array_equal(times, [0.0, 0.1])
    assert np.isnan(bandwidths).all()
    assert np.isnan(intensities).all()

    with pytest.raises(ValueError, match="Метод не распознан"):
        sk_formants.analyze_formants_alternative(np.ones(8), 8_000, method="unknown")


def test_extract_formants_averages_series_and_preemphasizes_segment(monkeypatch):
    formants = {
        "frequencies": [
            [400.0, 600.0],
            [np.nan, np.nan],
            [2_000.0],
            [3_000.0],
            [4_000.0],
        ]
    }
    result = sk_formants.extract_formants(np.zeros(4), 16_000, formants=formants)
    assert result[0] == pytest.approx(500.0)
    assert np.isnan(result[1])
    assert result[2:] == pytest.approx([2_000.0, 3_000.0, 4_000.0])

    captured = {}

    def fake_extract(signal, sr, speech=True):
        captured["signal"] = signal
        return [1, 2, 3, 4, 5]

    monkeypatch.setattr(sk_formants, "extract_formants", fake_extract)
    segment = np.array([1.0, 2.0, 4.0])
    assert sk_formants.extract_formants_from_segment(segment, 16_000) == [1, 2, 3, 4, 5]
    np.testing.assert_allclose(captured["signal"], [1.0, 1.03, 2.06])


def test_extract_formants_and_f0_uses_voiced_pitch_only(monkeypatch):
    class FakeFormant:
        def get_value_at_time(self, index, time):
            return np.nan if index == 5 else index * 500.0

    class FakePitch:
        selected_array = {"frequency": np.array([0.0, 110.0, 220.0])}

    class FakeSound:
        def __init__(self, signal, sr):
            pass

        def to_formant_burg(self, **kwargs):
            return FakeFormant()

        def to_pitch(self, **kwargs):
            return FakePitch()

    monkeypatch.setattr(sk_formants.pm, "Sound", FakeSound)
    formants, pitch = sk_formants.extract_formants_and_f0(np.ones(16), 16_000)
    assert formants == [500.0, 1_000.0, 1_500.0, 2_000.0, 0]
    np.testing.assert_array_equal(pitch, [110.0, 220.0])


def test_formant_bandwidth_wrapper_uses_supplied_analysis():
    formants = {"bandwidths": [[20.0, 40.0], [], [], [], []]}
    assert sk_formants.calculate_formant_bandwidth(
        np.zeros(8), 16_000, 1, method="mean", formants=formants
    ) == pytest.approx(30.0)
    with pytest.raises(ValueError, match="между 1 и 5"):
        sk_formants.calculate_formant_bandwidth(np.zeros(8), 16_000, 0)


def test_formant_energy_variants_with_controlled_filters(monkeypatch):
    signal = np.array([1.0, 2.0])
    monkeypatch.setattr(sk_formants, "extract_formants", lambda *args, **kwargs: [500, 1000, 1500, 0, 7900])
    monkeypatch.setattr(sk_formants, "calculate_formant_bandwidth", lambda *args, **kwargs: 200.0)
    monkeypatch.setattr(sk_formants.scipy.signal, "butter", lambda *args, **kwargs: ([1.0], [1.0]))
    monkeypatch.setattr(sk_formants.scipy.signal, "lfilter", lambda b, a, y: np.asarray(y))

    energies = sk_formants.calculate_formant_energy2(signal, 16_000)
    assert energies == pytest.approx([5.0, 5.0, 5.0, 0.0, 0.0])

    analysis = {
        "frequencies": [[500.0, 520.0], [], [], [], []],
        "voiced_times": [0.0, 0.032],
        "bandwidths": [[100.0, 200.0], [], [], [], []],
    }
    monkeypatch.setattr(
        sk_formants.librosa.feature,
        "rms",
        lambda **kwargs: np.array([[4.0, 9.0]]),
    )
    energy_by_time = sk_formants.calculate_formant_energy_arr(signal, 16_000, 1, analysis)
    np.testing.assert_allclose(energy_by_time, [(400.0, 0.0), (1800.0, 0.032)])
    assert sk_formants.calculate_formant_energy3(signal, 16_000, 1, analysis) == pytest.approx(1100.0)
    assert sk_formants.calculate_formant_energy_arr(signal, 16_000, 2, analysis) == []
    assert sk_formants.calculate_formant_energy3(signal, 16_000, 2, analysis) == 0


def test_combined_formant_and_pitch_energy(monkeypatch):
    signal = np.array([1.0, 2.0])
    monkeypatch.setattr(
        sk_formants,
        "extract_formants_and_f0",
        lambda *args: ([500.0, 1_000.0, 0.0, 3_000.0, 7_990.0], np.array([100.0, 200.0])),
    )
    monkeypatch.setattr(sk_formants, "calculate_formant_bandwidth", lambda *args: 200.0)
    monkeypatch.setattr(sk_formants.pt, "calculate_pitch_bandwidth", lambda *args: 40.0)
    monkeypatch.setattr(sk_formants.scipy.signal, "butter", lambda *args, **kwargs: ([1.0], [1.0]))
    monkeypatch.setattr(sk_formants.scipy.signal, "lfilter", lambda b, a, y: np.asarray(y))

    formant_energies, f0_energy = sk_formants.calculate_formant_and_f0_energy(signal, 16_000)
    assert formant_energies == pytest.approx([5.0, 5.0, 0.0, 5.0, 0.0])
    assert f0_energy == pytest.approx(5.0)


def test_pattern_simplification_classification_and_dynamics():
    patterns = [
        ([1, 1, -1], [0, 0, 1], [1, 1, -1]),
        ([0, 0, 1], [1, 1, 0], [0, 0, 1]),
        ([-1, -1, 0], [1, 1, -1], [1, 1, 0]),
    ]
    simplified = sk_formants.simplify_formant_patterns2(
        patterns, [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3)]
    )
    assert len(simplified) == 2
    assert simplified[0][3] == (0.0, 0.2)

    current = [(1, 1, 1), (1, 1, 1), (1, 1, 1)]
    assert sk_formants.compare_patterns(current, ("a", current))
    assert sk_formants.classify_phonemes([current], [("a", current)]) == "a"

    dynamics, segments = sk_formants.calculate_formant_dynamics(
        [np.array([500.0, 700.0, np.nan])],
        np.array([0.0, 0.05, 0.1]),
        [np.array([100.0, 200.0, np.nan])],
        {1: (200.0, 800.0)},
        delta_time=0.05,
    )
    assert segments == [(0, 0.05), (0.05, 0.1)]
    assert dynamics[0][0] == pytest.approx((0.0, 100.0))
    assert dynamics[0][1] == pytest.approx((200.0, 200.0))
