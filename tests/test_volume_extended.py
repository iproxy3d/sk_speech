from __future__ import annotations

import numpy as np
import pytest

from sk_speech import sk_volume


def test_empty_value_has_independent_complete_component_records():
    value = sk_volume.create_empty_value(template_speech=True)

    assert value["template_speech"] is True
    assert set(value) >= {"f0", "f1", "f2", "f3", "f4", "f5", "vowels", "amplitude_db"}
    assert value["f0"] is not value["f1"]
    assert value["f0"]["period"] == {"time": 0, "offset": 0, "amplitude": 0}


def test_transition_pitch_shift_and_formant_energy():
    assert sk_volume.transition(10.0, 20.0, 0.25) == 12.5
    assert sk_volume.calculate_pitch_shift_semitones(0) == pytest.approx(0)
    assert sk_volume.calculate_pitch_shift_semitones(440) == pytest.approx(12)
    assert sk_volume.calculate_formant_energy(-20.0, 100.0) == pytest.approx(1.0)


def test_change_volume_clips_and_preserves_sample_rate():
    signal = np.array([-0.75, 0.25, 0.75])
    changed, sr = sk_volume.change_audio_volume(signal, 16_000, 2.0)

    np.testing.assert_array_equal(changed, [-1.0, 0.5, 1.0])
    assert sr == 16_000


def test_mix_audio_uses_shortest_length_and_linear_ratio():
    original = np.zeros(4)
    filtered = np.ones(3)

    result = sk_volume.mix_audio(original, filtered, start_mix_ratio=0.0, end_mix_ratio=1.0)
    np.testing.assert_allclose(result, [0.0, 0.5, 1.0])


def test_loudness_corrections_and_volume_validation():
    corrections = sk_volume.calculate_loudness_corrections(np.array([50, 1_000, 5_500]))
    np.testing.assert_allclose(corrections, [12, 0, -12])

    assert sk_volume.calculate_speech_volume([0, np.nan], [-20, -10]) == -np.inf
    with pytest.raises(ValueError, match="same shape"):
        sk_volume.calculate_speech_volume([100, 200], [-20])
    with pytest.raises(ValueError, match="combine_mode"):
        sk_volume.calculate_speech_volume([1_000], [-20], combine_mode="invalid")


def test_serialization_converts_nested_numpy_values():
    source = {
        "array": np.array([1, 2]),
        "integer": np.int64(3),
        "float": np.float32(4.5),
        "boolean": np.bool_(True),
        "nested": [np.array([5.0])],
    }

    result = sk_volume.convert_params_to_serializable(source)
    assert result == {
        "array": [1, 2],
        "integer": 3,
        "float": 4.5,
        "boolean": True,
        "nested": [[5.0]],
    }


def test_update_param_and_average_params():
    total = sk_volume.create_empty_formant()
    sample = sk_volume.create_empty_formant()
    sample.update(freq=500, bandwidth=100, energy=4, intensity=2, amplitude=-20)
    sample["period"] = {"time": 2, "offset": 4, "amplitude": 6}
    sk_volume.update_param(total, sample)

    assert total["count"] == 1
    assert total["freq"] == 500
    assert total["period"]["offset"] == 4

    params = {"up": {"emotion": sk_volume.create_empty_value()}}
    params["up"]["emotion"]["f0"] = total
    sk_volume.average_params(params)
    assert params["up"]["emotion"]["f0"]["freq"] == 500
    assert np.isfinite(params["up"]["emotion"]["amplitude_db"])


def test_generate_and_mix_signals_have_expected_timing():
    generated = sk_volume.generate_signal(
        frequencies=[100, 100, 100],
        bandwidths=[10, 10, 10],
        intensities=[1, 1, 1],
        times=[0.01, 0.02, 0.03],
        delta_time=0.01,
        sr=1_000,
    )
    assert generated.shape == (30,)
    np.testing.assert_array_equal(generated[:10], np.zeros(10))

    mixed = sk_volume.mix_audio_signals([np.array([1.0, 2.0]), np.array([10.0])])
    np.testing.assert_array_equal(mixed, [11.0, 2.0])
