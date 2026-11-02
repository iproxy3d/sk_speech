from types import SimpleNamespace

import numpy as np
import pytest

from sk_speech import sk_filters
from sk_speech import sk_formants
from sk_speech import sk_noise
from sk_speech import sk_pitch
from sk_speech import sk_plot
from sk_speech import sk_vowels
from sk_speech import sk_detection


def test_boost_formants_filter_builds_filtered_signal(monkeypatch):
    y = np.linspace(-0.2, 0.2, 32, dtype=float)

    monkeypatch.setattr(sk_formants, "extract_formants", lambda *_: [200.0])
    monkeypatch.setattr(sk_formants, "calculate_formant_bandwidth", lambda *_: 40.0)
    monkeypatch.setattr(sk_formants.scipy.signal, "butter", lambda *args, **kwargs: (1, 1))
    monkeypatch.setattr(sk_formants.scipy.signal, "lfilter", lambda *args, **kwargs: y * 0.25)
    monkeypatch.setattr(sk_formants.fl, "apply_bandpass_filter", lambda *args, **kwargs: y * 0.25)

    result = sk_formants.boost_formants_filter(y, 16_000, [6.0], 0.0)

    assert result.shape == y.shape
    assert np.isfinite(result).all()


def test_plot_accepts_full_extract_f0_result(monkeypatch):
    time = np.array([0.0, 0.01])
    pitch = np.array([100.0, 110.0])
    monkeypatch.setattr(
        sk_plot.pt,
        "extract_f0_voiced",
        lambda *_: (pitch, time, np.ones(2), time, object(), object(), object()),
    )
    monkeypatch.setattr(sk_plot.fmt, "formant_trajectory", lambda *_: (time, pitch))
    monkeypatch.setattr(sk_plot.plt, "show", lambda: None)

    sk_plot.plot_trajectory_formants_and_pitch(np.zeros(32), 16_000)


def test_remove_short_sequences_uses_absolute_difference():
    f0 = np.array([100.0, 120.0, 180.0, 160.0])

    result = sk_pitch.remove_short_sequences(f0, min_length=2)

    np.testing.assert_array_equal(result, np.array([100.0, 120.0]))


def test_pitch_intensity_avg_handles_missing_pitch(monkeypatch):
    monkeypatch.setattr(sk_pitch, "calculate_pitch_intensity", lambda *args, **kwargs: None)

    assert sk_pitch.calculate_pitch_intensity_avg(np.zeros(32), 16_000) is False


def test_vowel_gradient_returns_empty_result_when_extraction_fails(monkeypatch):
    monkeypatch.setattr(sk_vowels.librosa, "load", lambda *_: (np.zeros(32), 16_000))
    monkeypatch.setattr(sk_vowels.pt, "flatten_pitch", lambda *_: (None, 16_000))

    assert sk_vowels.detect_vowel_boundaries_gradient("missing.wav") == []


def test_penn_backend_is_loaded_lazily(monkeypatch):
    class FakeTensor:
        ndim = 1

        def unsqueeze(self, _):
            self.ndim = 2
            return self

    fake_torch = SimpleNamespace(float32="float32", as_tensor=lambda *args, **kwargs: FakeTensor())
    calls = {}

    def from_audio(audio, sr, **kwargs):
        calls.update(audio=audio, sr=sr, kwargs=kwargs)
        return "pitch", "periodicity"

    fake_penn = SimpleNamespace(from_audio=from_audio)
    monkeypatch.setattr(
        sk_pitch,
        "import_module",
        lambda name: {"penn": fake_penn, "torch": fake_torch}[name],
    )

    result = sk_pitch.extract_f0_penn(np.zeros(32), 16_000)

    assert result == "pitch"
    assert calls["audio"].ndim == 2
    assert calls["kwargs"]["gpu"] is None


def test_optional_backend_error_names_install_extra(monkeypatch):
    def missing(_):
        raise ImportError("missing")

    monkeypatch.setattr(sk_pitch, "import_module", missing)

    with pytest.raises(ImportError, match=r"sk-speech\[penn\]"):
        sk_pitch.extract_f0_penn(np.zeros(32), 16_000)


def test_missing_rubberband_backend_names_install_extra(monkeypatch):
    monkeypatch.setattr(
        sk_pitch,
        "import_module",
        lambda _: (_ for _ in ()).throw(ImportError("missing")),
    )

    with pytest.raises(ImportError, match=r"sk-speech\[rubberband\]"):
        sk_pitch.change_pitch_rubberband(np.zeros(32), 16_000, 2.0)


def test_rubberband_backend_receives_semitones(monkeypatch):
    calls = {}

    def pitch_shift(y, sr, n_steps):
        calls.update(sr=sr, n_steps=n_steps)
        return y

    monkeypatch.setattr(
        sk_pitch,
        "import_module",
        lambda name: SimpleNamespace(pitch_shift=pitch_shift),
    )
    y = np.zeros(32)

    result = sk_pitch.change_pitch_rubberband(y, 16_000, 2.5)

    assert result is y
    assert calls == {"sr": 16_000, "n_steps": 2.5}


def test_filter_conversions_round_trip():
    frequencies = np.array([110.0, 220.0, 440.0, 880.0])

    semitones = sk_filters.hz_to_semitones(frequencies)
    restored = sk_filters.semitones_to_hz(semitones)

    np.testing.assert_allclose(restored, frequencies)


def test_normalize_audio_preserves_input_when_backend_fails(monkeypatch):
    y = np.array([0.0, 1.0])

    def fail(_):
        raise RuntimeError("normalization failed")

    monkeypatch.setattr(sk_filters.librosa.util, "normalize", fail)

    assert sk_filters.normalize_audio(y) is y


def test_noise_reduction_returns_none_when_stft_fails(monkeypatch):
    monkeypatch.setattr(sk_noise.librosa, "stft", lambda *_: (_ for _ in ()).throw(RuntimeError("bad stft")))

    assert sk_noise.noise_reduction_spectral_subtraction_fast(np.zeros(32), 16_000) is None


def test_formant_clarity_skips_failed_frames(monkeypatch):
    class FailingFormant:
        def ts(self):
            return [0.0, 0.01]

        def get_bandwidth_at_time(self, *_):
            raise RuntimeError("Praat frame failed")

    fake_sound = SimpleNamespace(to_formant_burg=lambda **_: FailingFormant())
    monkeypatch.setattr(sk_detection.pm, "Sound", lambda *_: fake_sound)

    result = sk_detection.formant_clarity(np.zeros(32), 16_000)

    assert len(result) == 5
    assert all(np.isnan(value) for value in result)
