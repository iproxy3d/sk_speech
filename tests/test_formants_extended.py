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


def test_segment_duration_is_finite_for_zero_and_large_shifts():
    assert sk_formants.calculate_segment_duration([0, 0, 0]) == pytest.approx(0.0025)
    value = sk_formants.calculate_segment_duration([500, -200])
    assert np.isfinite(value)
    assert 0.0007 <= value <= 0.0025


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
