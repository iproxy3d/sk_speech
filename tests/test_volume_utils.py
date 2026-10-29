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

