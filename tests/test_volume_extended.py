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


def test_generate_signal_preserves_timeline_for_nan_and_gaps():
    generated = sk_volume.generate_signal(
        frequencies=[100, np.nan, 100],
        bandwidths=None,
        intensities=[1, 1, 1],
        times=[0.0, 0.01, 0.03],
        delta_time=0.01,
        sr=1_000,
    )

    assert generated.shape == (30,)
    np.testing.assert_array_equal(generated, np.zeros(30))

    invalid_bandwidth = sk_volume.generate_signal(
        frequencies=[100, 100],
        bandwidths=[10, 0],
        intensities=[1, 1],
        times=[0.0, 0.01],
        delta_time=0.01,
        energy_correction=1,
        sr=1_000,
    )
    np.testing.assert_array_equal(invalid_bandwidth, np.zeros(10))


def test_generate_signal_validates_time_axis_and_component_lengths():
    assert sk_volume.generate_signal([], None, [], [], 0.01, sr=1_000).size == 0

    with pytest.raises(ValueError, match="non-decreasing"):
        sk_volume.generate_signal([100, 100], None, [1, 1], [0.02, 0.01], 0.01, sr=1_000)
    with pytest.raises(ValueError, match="non-negative"):
        sk_volume.generate_signal([100], None, [1], [-0.01], 0.01, sr=1_000)
    with pytest.raises(ValueError, match="cover every time point"):
        sk_volume.generate_signal([100], None, [1], [0.0, 0.01], 0.01, sr=1_000)
    with pytest.raises(ValueError, match="bandwidths"):
        sk_volume.generate_signal([100, 100], None, [1, 1], [0.0, 0.01], 0.01,
                                  energy_correction=1, sr=1_000)


def test_load_vectors_from_json_and_default_structure(tmp_path):
    file_path = tmp_path / "vectors.json"
    file_path.write_text('{"value": 42}', encoding="utf-8")
    assert sk_volume.load_vectors_from_json(file_path) == {"value": 42}

    default = sk_volume.load_vectors_from_json(tmp_path / "missing.json")
    assert set(default) == {"params", "vectors", "files"}
    assert default["params"]["norm"]["template_speech"] is True


def test_trim_silence_optional_denoising_and_librosa_trim(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sk_volume.ns,
        "noise_reduction_spectral_subtraction_fast",
        lambda y, sr: np.asarray(y) * 2,
    )
    monkeypatch.setattr(
        sk_volume.librosa.effects,
        "trim",
        lambda y, top_db: (calls.append((np.asarray(y).copy(), top_db)) or (np.asarray(y)[1:], None)),
    )

    result = sk_volume.trim_silence(np.array([1.0, 2.0, 3.0]), 16_000, top_db=30, apply_noise_reduction=True)
    np.testing.assert_array_equal(calls[0][0], [2.0, 4.0, 6.0])
    assert calls[0][1] == 30
    np.testing.assert_array_equal(result, [4.0, 6.0])


class _FakeAudio:
    def __init__(self, levels):
        self.levels = list(levels)

    def __len__(self):
        return len(self.levels) * 10

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = (item.start or 0) // 10
            stop = len(self.levels) if item.stop is None else item.stop // 10
            return _FakeAudio(self.levels[start:stop])
        raise TypeError

    @property
    def dBFS(self):
        return self.levels[0] if self.levels else 0.0

    def reverse(self):
        return _FakeAudio(reversed(self.levels))


def test_pydub_silence_detection_and_trimming():
    audio = _FakeAudio([-80.0, -70.0, -10.0, -20.0, -80.0])
    assert sk_volume.detect_leading_silence(audio) == 20
    trimmed = sk_volume.trim_silence_pydub(audio)
    assert trimmed.levels == [-10.0, -20.0]
    with pytest.raises(AssertionError):
        sk_volume.detect_leading_silence(audio, chunk_size=0)


def test_combined_intensity_statistics(monkeypatch):
    monkeypatch.setattr(sk_volume.pt, "calculate_pitch_intensity", lambda *args: np.array([1.0, 3.0]))
    monkeypatch.setattr(
        sk_volume.fmt,
        "calculate_formant_intensity",
        lambda y, sr, index: np.array([2.0, 4.0]) if index < 5 else np.array([]),
    )
    assert sk_volume.calculate_intensity_avg(np.ones(8), 16_000) == pytest.approx(2.8)
    assert sk_volume.calculate_intensity_max(np.ones(8), 16_000) == pytest.approx(3.0)


@pytest.mark.parametrize(
    ("volume", "shift_sign", "pitch_relation"),
    [(0.5, 1, 1), (-0.5, -1, -1), (2.0, 1, 1), (-2.0, -1, -1)],
)
def test_energy_speech_covers_all_voice_modes(volume, shift_sign, pitch_relation):
    pitch_factor, pitch_shift, bandwidths, energies, shifts, vowels = sk_volume.energy_speech(volume)
    assert len(bandwidths) == len(energies) == len(shifts) == 5
    assert set(vowels) == {"a", "e", "i", "o", "u"}
    assert np.sign(shifts[0]) == shift_sign
    assert np.sign(pitch_shift) == pitch_relation
    assert pitch_factor > 0


def test_change_volume_noop_and_transition_mix(monkeypatch):
    signal = np.array([1.0, 2.0])
    assert sk_volume.change_volume(signal, 16_000, 0, 0) is signal

    monkeypatch.setattr(sk_volume, "change_speech_volume", lambda y, sr, volume, *args: np.asarray(y) * 2)
    captured = {}

    def fake_mix(original, filtered, start, end):
        captured.update(start=start, end=end)
        return filtered

    monkeypatch.setattr(sk_volume, "mix_audio", fake_mix)
    result = sk_volume.change_volume(signal, 16_000, 0.25, 0.5)
    np.testing.assert_array_equal(result, signal * 2)
    assert captured == {"start": 0.5, "end": 1.0}


def test_spectral_slope_returns_one_value_per_complete_window():
    signal = np.sin(2 * np.pi * 100 * np.arange(32) / 8_000)
    times, slopes = sk_volume.compute_spectral_slope(signal, 8_000, window_size=16, hop_size=8)
    assert len(times) == len(slopes) == 3
    assert np.isfinite(slopes).all()


def test_vocal_tract_length_helpers(monkeypatch):
    monkeypatch.setattr(
        sk_volume.fmt,
        "get_formant_frequency_by_index",
        lambda y, sr, index: index * 1_000.0,
    )
    monkeypatch.setattr(
        sk_volume.vk,
        "get_tract_length_from_formant",
        lambda frequency, index: frequency / (index * 10_000.0),
    )
    result = sk_volume.get_tract_length(np.ones(8), 16_000)
    assert result["avg"] == pytest.approx(10.0)
    assert result["f5"] == pytest.approx(10.0)

    frequencies = [[index * 1_000.0] for index in range(1, 8)]
    monkeypatch.setattr(
        sk_volume.fmt,
        "formant_frequencies_expended",
        lambda *args, **kwargs: (frequencies, [], [], []),
    )
    expanded = sk_volume.get_tract_length_expended(np.ones(8), 16_000)
    assert expanded["avg"] == pytest.approx(10.0)
    assert expanded["f6"] == pytest.approx(10.0)
    assert expanded["f7"] == pytest.approx(10.0)


def test_update_and_average_vowel_profiles():
    total = sk_volume.create_empty_value(True)["vowels"]
    observed = {
        "vowel_boundaries": [(100, "a"), (200, "a")],
        "amplitude": {f"f{i}": [float(i), float(i + 2)] for i in range(1, 6)},
        "energy": {f"f{i}": [float(i * 10), float((i + 2) * 10)] for i in range(1, 6)},
        "freq": {f"f{i}": [float(i * 100), float((i + 2) * 100)] for i in range(1, 6)},
    }
    sk_volume.update_vowels(total, observed)
    count = dict((vowel, count) for count, vowel in total["vowel_boundaries"])
    assert count["a"] == 2

    params = {"up": {"emotion": {"vowels": total}}}
    sk_volume.average_vowels(params)
    assert total["amplitude"]["a"]["f1"] == pytest.approx(2.0)
    assert total["energy"]["a"]["f5"] == pytest.approx(60.0)
    assert total["freq"]["a"]["f3"] == pytest.approx(400.0)


def test_speech_vector_and_reconstruction_for_pitch_only():
    norm = sk_volume.create_empty_value(True)
    params = sk_volume.create_empty_value(True)
    options = {"pitch": True, "formants": False, "formant_max": 0, "freq": True}
    norm["options"] = options
    params["options"] = options
    norm["f0"].update(freq=100.0, freq_min=80.0, freq_max=120.0, amplitude_slope=0.0)
    params["f0"].update(freq=120.0, amplitude_slope=0.0)
    norm["amplitude_db"] = -20.0
    params["amplitude_db"] = -10.0

    vector = sk_volume.get_speech_vector(params, norm)
    assert vector["emotion"] == 1.0
    assert vector["volume"] == 1.0
    assert vector["f0"]["freq"] == pytest.approx(20.0)

    reconstructed = sk_volume.get_speech_new(norm, params, vector, volume=0.5, emotion=0.5)
    assert reconstructed["f0"]["freq"] == pytest.approx(110.0)
    assert reconstructed["volume"] == 0.5
    assert reconstructed["emotion"] == 0.5


def test_change_speech_volume_runs_full_processing_pipeline(monkeypatch):
    signal = np.array([0.1, -0.1])
    calls = []

    monkeypatch.setattr(
        sk_volume.ns,
        "noise_reduction_spectral_subtraction",
        lambda y, sr, **kwargs: calls.append("noise") or np.asarray(y),
    )
    monkeypatch.setattr(
        sk_volume.vw,
        "detect_vowel_boundaries",
        lambda *args, **kwargs: calls.append("detect") or [(1, "a")],
    )
    monkeypatch.setattr(
        sk_volume.fmt,
        "change_formant_bandwidth",
        lambda y, sr, factors: calls.append("bandwidth") or np.asarray(y),
    )
    monkeypatch.setattr(
        sk_volume.fmt,
        "change_formant_energy4",
        lambda y, sr, factors: calls.append("formant_energy") or np.asarray(y),
    )
    monkeypatch.setattr(
        sk_volume.fmt,
        "change_formants_shifts3",
        lambda y, sr, shifts: (calls.append("formant_shift") or np.asarray(y), sr),
    )
    monkeypatch.setattr(
        sk_volume.vw,
        "energy_vowels",
        lambda y, sr, boundaries, factors, duration: calls.append("vowel_energy") or np.asarray(y),
    )
    monkeypatch.setattr(
        sk_volume.vw,
        "apply_formant_shifts_vowels",
        lambda y, sr, boundaries, shifts, duration: calls.append("vowel_shift") or np.asarray(y),
    )
    monkeypatch.setattr(
        sk_volume.pt,
        "change_pitch_energy",
        lambda y, sr, factor: (calls.append("pitch_energy") or np.asarray(y), sr),
    )

    result = sk_volume.change_speech_volume(
        signal, 16_000, volume=0.5, is_noise=True, is_shift=True
    )
    np.testing.assert_array_equal(result, signal)
    assert calls == [
        "noise",
        "detect",
        "bandwidth",
        "formant_energy",
        "formant_shift",
        "vowel_energy",
        "vowel_shift",
        "pitch_energy",
    ]
