from __future__ import annotations

import numpy as np


def test_speech_volume_ignores_zero_frequency_components():
    from sk_speech.sk_volume import calculate_speech_volume

    result = calculate_speech_volume([220.0, 0.0], [-30.0, 0.0])
    expected = calculate_speech_volume([220.0], [-30.0])
    assert np.isfinite(result)
    assert result == expected


def test_power_combination_is_available():
    from sk_speech.sk_volume import calculate_speech_volume

    value = calculate_speech_volume(
        [1000.0, 1000.0],
        [-20.0, -20.0],
        combine_mode="power",
    )
    np.testing.assert_allclose(value, -16.989700043360187, atol=1e-8)


def test_removed_vowel_frequency_path_is_a_safe_noop():
    from sk_speech.sk_volume import get_change_speech

    audio = np.array([0.1, -0.1, 0.2], dtype=float)
    muls = {
        "options": {
            "pitch": False,
            "formants": False,
            "vowels": True,
            "change": {
                "vowel_amplitude": False,
                # Старые конфигурации могут всё ещё содержать этот ключ.
                "vowel_freq": True,
            },
        }
    }
    params = {
        "info": {
            "pitch": None,
            "formants": None,
            "vowel_formants": None,
        }
    }
    new_params = {"volume": 1.0}

    changed, sample_rate = get_change_speech(audio, 16_000, muls, new_params, params)

    np.testing.assert_array_equal(changed, audio)
    assert sample_rate == 16_000

