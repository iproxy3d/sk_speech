"""Fast extraction of aligned F0 and broadband intensity tracks."""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from pathlib import Path

import numpy as np
import parselmouth as pm
import soundfile as sf
from scipy.signal import resample_poly

from .models import PitchTrack


@dataclass(frozen=True, slots=True)
class PitchConfig:
    """Configuration of the Praat-backed feature extractor."""

    sample_rate: int | None = 16_000
    frame_step_s: float = 0.01
    pitch_floor_hz: float = 50.0
    pitch_ceiling_hz: float = 800.0
    minimum_voiced_frames: int = 1

    def __post_init__(self) -> None:
        if self.sample_rate is not None and self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive or None")
        if self.frame_step_s <= 0:
            raise ValueError("frame_step_s must be positive")
        if self.pitch_floor_hz <= 0 or self.pitch_ceiling_hz <= self.pitch_floor_hz:
            raise ValueError("pitch limits must satisfy 0 < floor < ceiling")
        if self.minimum_voiced_frames < 1:
            raise ValueError("minimum_voiced_frames must be at least 1")


def _mono_float(signal: np.ndarray) -> np.ndarray:
    value = np.asarray(signal, dtype=np.float64)
    if value.ndim == 2:
        value = value.mean(axis=1)
    elif value.ndim != 1:
        raise ValueError("audio must be a mono vector or a (samples, channels) matrix")
    if not np.all(np.isfinite(value)):
        raise ValueError("audio contains NaN or infinite samples")
    return np.ascontiguousarray(value)


def _resample(signal: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate:
        return signal
    divisor = gcd(source_rate, target_rate)
    return resample_poly(signal, target_rate // divisor, source_rate // divisor)


def _remove_short_runs(mask: np.ndarray, minimum_length: int) -> np.ndarray:
    if minimum_length <= 1 or not mask.any():
        return mask
    result = mask.copy()
    padded = np.pad(mask.astype(np.int8), (1, 1))
    transitions = np.flatnonzero(np.diff(padded))
    for start, stop in transitions.reshape(-1, 2):
        if stop - start < minimum_length:
            result[start:stop] = False
    return result


class PitchExtractor:
    """Extract F0 and intensity from files or in-memory audio."""

    def __init__(self, config: PitchConfig | None = None) -> None:
        self.config = config or PitchConfig()

    def from_file(self, path: str | Path) -> PitchTrack:
        signal, sample_rate = sf.read(path, always_2d=False)
        return self.extract(signal, int(sample_rate))

    def extract(self, signal: np.ndarray, sample_rate: int) -> PitchTrack:
        if sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        audio = _mono_float(signal)
        target_rate = self.config.sample_rate or sample_rate
        audio = _resample(audio, sample_rate, target_rate)
        duration_s = len(audio) / target_rate

        if audio.size == 0:
            empty = np.empty(0, dtype=float)
            return PitchTrack(empty, empty, empty, np.empty(0, dtype=bool), target_rate, self.config.frame_step_s, 0.0)

        sound = pm.Sound(audio, sampling_frequency=target_rate)
        pitch = sound.to_pitch(
            time_step=self.config.frame_step_s,
            pitch_floor=self.config.pitch_floor_hz,
            pitch_ceiling=self.config.pitch_ceiling_hz,
        )
        time_s = np.asarray(pitch.xs(), dtype=float)
        raw_f0 = np.asarray(pitch.selected_array["frequency"], dtype=float)
        voiced = np.isfinite(raw_f0) & (raw_f0 > 0)
        voiced = _remove_short_runs(voiced, self.config.minimum_voiced_frames)
        f0_hz = np.where(voiced, raw_f0, np.nan)

        intensity = sound.to_intensity(
            minimum_pitch=self.config.pitch_floor_hz,
            time_step=self.config.frame_step_s,
        )
        intensity_times = np.asarray(intensity.xs(), dtype=float)
        intensity_values = np.asarray(intensity.values, dtype=float).reshape(-1)
        if intensity_times.size:
            # Praat's intensity grid can begin a few frames after the pitch
            # grid.  Use the nearest boundary estimate at those short edges so
            # every pitch frame still has an aligned intensity value.
            intensity_db = np.interp(time_s, intensity_times, intensity_values)
        else:
            intensity_db = np.full_like(time_s, np.nan)

        return PitchTrack(
            time_s=time_s,
            f0_hz=f0_hz,
            intensity_db=intensity_db,
            voiced=voiced,
            sample_rate=target_rate,
            frame_step_s=self.config.frame_step_s,
            duration_s=duration_s,
        )

