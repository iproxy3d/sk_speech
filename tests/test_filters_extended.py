from __future__ import annotations

import numpy as np
import pytest

from sk_speech import sk_filters


def _tone(frequency: float, sr: int = 16_000, seconds: float = 1.0):
    time = np.arange(round(sr * seconds)) / sr
    return np.sin(2 * np.pi * frequency * time)


def test_high_and_low_pass_filters_separate_low_and_high_tones():
    low = _tone(100)
    high = _tone(2_000)
    start = 2_000  # пропускаем переходный процесс IIR-фильтра

    assert np.std(sk_filters.apply_low_pass_filter(low, 16_000, 500)[start:]) > 10 * np.std(
        sk_filters.apply_low_pass_filter(high, 16_000, 500)[start:]
    )
    assert np.std(sk_filters.apply_high_pass_filter(high, 16_000, 500)[start:]) > 10 * np.std(
        sk_filters.apply_high_pass_filter(low, 16_000, 500)[start:]
    )


def test_bandpass_filter_validates_cutoffs_and_keeps_shape():
    signal = _tone(1_000) + _tone(4_000)
    filtered = sk_filters.apply_bandpass_filter(signal, 16_000, 800, 1_200)

    assert filtered.shape == signal.shape
    with pytest.raises(ValueError, match="scalar"):
        sk_filters.apply_bandpass_filter(signal, 16_000, [800], 1_200)


def test_moving_average_and_median_filter_remove_local_spike():
    signal = np.array([0.0, 0.0, 9.0, 0.0, 0.0])

    np.testing.assert_allclose(
        sk_filters.apply_moving_average(signal, 3),
        [0.0, 3.0, 3.0, 3.0, 0.0],
    )
    np.testing.assert_array_equal(sk_filters.apply_median_filter(signal, 3), np.zeros(5))


def test_window_compression_and_distortion_are_bounded():
    signal = np.linspace(-1.0, 1.0, 101)

    windowed = sk_filters.apply_window_function(np.ones(8), window_length=8)
    assert windowed[0] == pytest.approx(0.08)
    assert windowed[-1] == pytest.approx(0.08)

    compressed = sk_filters.apply_compression(signal)
    distorted = sk_filters.apply_distortion(signal)
    assert np.max(np.abs(compressed)) <= 1.0
    assert np.max(np.abs(distorted)) < 1.0
    np.testing.assert_allclose(compressed, -compressed[::-1])
    np.testing.assert_allclose(distorted, -distorted[::-1])


def test_reverb_adds_delayed_copy_and_harmonic_scales():
    impulse = np.zeros(20)
    impulse[0] = 1.0

    reverberated = sk_filters.apply_reverb(
        impulse, sr=1_000, reverb_factor=0.5, delay_ms=10, attenuation=0.5
    )
    assert reverberated[10] == pytest.approx(0.25)
    np.testing.assert_array_equal(sk_filters.apply_harmonic(impulse, 2.0), impulse * 2.0)


def test_lms_filter_updates_error_and_weights():
    adaptive = sk_filters.LMSFilter(order=3, step_size=0.1)
    output, error = adaptive.update(np.array([1.0, 2.0, 3.0]), desired_signal=2.0)

    assert output == 0.0
    assert error == 2.0
    np.testing.assert_allclose(adaptive.weights, [0.6, 0.4, 0.2])


def test_erb_endpoints_and_space_order():
    assert sk_filters.erb_point(100, 8_000, 1) == pytest.approx(100)
    assert sk_filters.erb_point(100, 8_000, 0) == pytest.approx(8_000)
    points = sk_filters.erb_space(100, 8_000, 8)
    assert len(points) == 8
    assert np.all(np.diff(points) < 0)
