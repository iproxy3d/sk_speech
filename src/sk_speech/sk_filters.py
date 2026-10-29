import numpy as np
import librosa
import scipy.signal
import soundfile as sf
from scipy import signal as sgn

DEFAULT_FILTER_NUM = 100
DEFAULT_LOW_FREQ = 50
DEFAULT_HIGH_FREQ = 44100/4


def hz_to_semitones(hz, reference_hz=440.0):
    """Convert Hz to semitones relative to a reference frequency (default is A4 = 440 Hz)."""
    return 12 * np.log2(hz / reference_hz)

def semitones_to_hz(semitones, reference_hz=440.0):
    """Convert semitones to Hz relative to a reference frequency (default is A4 = 440 Hz)."""
    return reference_hz * (2 ** (semitones / 12))

def normalize_audio(y):
    try:
       y = librosa.util.normalize(y)
       return y
    except:
       return y

def apply_high_pass_filter(y, sr, cutoff=100):
    sos = scipy.signal.butter(10, cutoff, btype='highpass', fs=sr, output='sos')
    y_filtered = scipy.signal.sosfilt(sos, y)
    return y_filtered

def apply_low_pass_filter(y, sr, cutoff=8000):
    sos = scipy.signal.butter(10, cutoff, btype='lowpass', fs=sr, output='sos')
    y_filtered = scipy.signal.sosfilt(sos, y)
    return y_filtered

def apply_median_filter(y, window_size):
    y_filtered = scipy.signal.medfilt(y, kernel_size=window_size)
    return y_filtered

def apply_moving_average(y, window_size):
    y_filtered = np.convolve(y, np.ones(window_size)/window_size, mode='same')
    return y_filtered

def apply_bandpass_filter(y, sr, lowcut, highcut):
    if np.isscalar(lowcut) and np.isscalar(highcut):
        sos = scipy.signal.butter(10, [lowcut, highcut], btype='band', fs=sr, output='sos')
        y_filtered = scipy.signal.sosfilt(sos, y)
        return y_filtered
    else:
        raise ValueError("Cutoff frequencies must be scalar values after shifting.")

def apply_smoothing_filter(y, sr):
    # Применение сглаживающего фильтра
    nyquist = 0.5 * sr
    cutoff = 3000  # Частота среза в Гц
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(4, normal_cutoff, btype='low', analog=False)
    y_filtered = scipy.signal.filtfilt(b, a, y)
    return y_filtered

def apply_window_function(segment, window_length=2205):
    # Применение оконной функции Хэмминга для плавного перехода
    window = np.hamming(len(segment))
    if len(segment) < window_length:
        # Создание окна той же длины, что и сегмент
        window = np.hamming(len(segment))
    else:
        # Применение окна к последним частям сегмента
        window[-window_length:] = np.hamming(window_length)
    return segment * window

# Function to apply dynamic range compression
def apply_compression(y, compression_factor=2):
    y_compressed = np.tanh(compression_factor * y) / np.tanh(compression_factor)
    return y_compressed

# Function to apply distortion/overdrive
def apply_distortion(y, distortion_factor=0.5):
    y_distorted = np.sign(y) * (1 - np.exp(-distortion_factor * np.abs(y)))
    return y_distorted

def apply_reverb(y, sr, reverb_factor=0.5, delay_ms=50, attenuation=0.5):
    """
    Применяет реверберационный эффект к аудиосигналу.

    Parameters:
    y (numpy array): Аудиосигнал
    sr (int): Частота дискретизации
    reverb_factor (float): Коэффициент реверберации (0 до 1)
    delay_ms (int): Задержка в миллисекундах (по умолчанию 50 мс)
    attenuation (float): Коэффициент ослабления для реверберации (по умолчанию 0.5)

    Returns:
    numpy array: Аудиосигнал с реверберацией
    """
    delay_samples = int(sr * (delay_ms / 1000.0))
    reverb = np.zeros_like(y)

    for i in range(delay_samples, len(y)):
        reverb[i] = y[i] + reverb_factor * attenuation * y[i - delay_samples]

    return reverb


def apply_harmonic(y, harmonic_factor=1.0):
    y_harmonic_adjusted = y * harmonic_factor
    return y_harmonic_adjusted

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

class LMSFilter:
    def __init__(self, order, step_size):
        self.order = order
        self.step_size = step_size
        self.weights = np.zeros(order)
        self.error = 0.0

    def update(self, input_signal, desired_signal):
        # Delay line
        # delay_line = np.roll(input_signal, self.order)[::-1][:self.order]
        delay_line = input_signal[::-1]

        # Filter output
        output = np.dot(self.weights, delay_line)

        # Error
        self.error = desired_signal - output

        # Update weights
        self.weights += self.step_size * self.error * delay_line

        return output, self.error

def train_adaptive_filter(reference_file, order=50, step_size=0.01):
    # Load reference audio file
    y_ref, sr_ref = librosa.load(reference_file, sr=None)

    # Normalize audio
    y_ref = normalize_audio(y_ref)

    # Initialize LMS filter
    lms_filter = LMSFilter(order=order, step_size=step_size)

    # Train the filter
    for i in range(order, len(y_ref)):
        input_chunk = y_ref[i-order:i]
        desired_signal = y_ref[i]

        lms_filter.update(input_chunk, desired_signal)

    return lms_filter

def apply_adaptive_filter(input_file, output_file, lms_filter, order=50):
    # Load noisy audio file
    y_noisy, sr_noisy = librosa.load(input_file, sr=None)

    # Normalize audio
    y_noisy = normalize_audio(y_noisy)

    # Process audio in chunks and apply the adaptive filter
    output_signal = np.zeros_like(y_noisy)

    for i in range(order, len(y_noisy)):
        input_chunk = y_noisy[i-order:i]

        filtered_chunk, _ = lms_filter.update(input_chunk, y_noisy[i])
        output_signal[i] = filtered_chunk

    # Save filtered audio
    sf.write(output_file, output_signal, sr_noisy)


def erb_point(low_freq, high_freq, fraction):
    """
    Calculates a single point on an ERB scale between ``low_freq`` and
    ``high_freq``, determined by ``fraction``. When ``fraction`` is ``1``,
    ``low_freq`` will be returned. When ``fraction`` is ``0``, ``high_freq``
    will be returned.

    ``fraction`` can actually be outside the range ``[0, 1]``, which in general
    isn't very meaningful, but might be useful when ``fraction`` is rounded a
    little above or below ``[0, 1]`` (eg. for plot axis labels).
    """
    # Change the following three parameters if you wish to use a different ERB
    # scale. Must change in MakeERBCoeffs too.
    # TODO: Factor these parameters out
    ear_q = 9.26449  # Glasberg and Moore Parameters
    min_bw = 24.7
    order = 1

    # All of the following expressions are derived in Apple TR #35, "An
    # Efficient Implementation of the Patterson-Holdsworth Cochlear Filter
    # Bank." See pages 33-34.
    erb_point = (
            -ear_q * min_bw
            + np.exp(
        fraction * (
                -np.log(high_freq + ear_q * min_bw)
                + np.log(low_freq + ear_q * min_bw)
        )
    ) *
            (high_freq + ear_q * min_bw)
    )
    return erb_point


def erb_space(
        low_freq=DEFAULT_LOW_FREQ,
        high_freq=DEFAULT_HIGH_FREQ,
        num=DEFAULT_FILTER_NUM):
    """
    This function computes an array of ``num`` frequencies uniformly spaced
    between ``high_freq`` and ``low_freq`` on an ERB scale.

    For a definition of ERB, see Moore, B. C. J., and Glasberg, B. R. (1983).
    "Suggested formulae for calculating auditory-filter bandwidths and
    excitation patterns," J. Acoust. Soc. Am. 74, 750-753.
    """
    return erb_point(
        low_freq,
        high_freq,
        np.arange(1, num + 1) / num
    )


def centre_freqs(fs, num_freqs, cutoff=DEFAULT_LOW_FREQ):
    """
    Calculates an array of centre frequencies (for :func:`make_erb_filters`)
    from a sampling frequency, lower cutoff frequency and the desired number of
    filters.

    :param fs: sampling rate
    :param num_freqs: number of centre frequencies to calculate
    :type num_freqs: int
    :param cutoff: lower cutoff frequency
    :return: same as :func:`erb_space`
    """
    return np.array(sorted(erb_space(cutoff, fs / 2, num_freqs)))

def MEL_centre_freqs(n_gammatone, fmin = 0, fmax = 8000):

    # Равномерное распределение точек по мел-шкале:
    mel_points = np.linspace(librosa.hz_to_mel(fmin),
                             librosa.hz_to_mel(fmax),
                             n_gammatone + 2)
    # Перевод этих точек обратно в Гц:
    hz_points = librosa.mel_to_hz(mel_points)

    center_freqs = hz_points[1:-1]
    bandwidths = hz_points[2:] - hz_points[:-2]

    return center_freqs, bandwidths

def centre_bandwidths(centre_freqs, width=1.0):
    ear_q = 9.26449  # Glasberg and Moore Parameters
    min_bw = 24.7
    order = 1

    erb = width * ((centre_freqs / ear_q) ** order + min_bw ** order) ** (1 / order)
    return erb

def make_erb_filters(fs, centre_freqs, width=1.0):
    """
    This function computes the filter coefficients for a bank of
    Gammatone filters. These filters were defined by Patterson and Holdworth for
    simulating the cochlea.

    The result is returned as a :class:`ERBCoeffArray`. Each row of the
    filter arrays contains the coefficients for four second order filters. The
    transfer function for these four filters share the same denominator (poles)
    but have different numerators (zeros). All of these coefficients are
    assembled into one vector that the ERBFilterBank can take apart to implement
    the filter.

    The filter bank contains "numChannels" channels that extend from
    half the sampling rate (fs) to "lowFreq". Alternatively, if the numChannels
    input argument is a vector, then the values of this vector are taken to be
    the center frequency of each desired filter. (The lowFreq argument is
    ignored in this case.)

    Note this implementation fixes a problem in the original code by
    computing four separate second order filters. This avoids a big problem with
    round off errors in cases of very small cfs (100Hz) and large sample rates
    (44kHz). The problem is caused by roundoff error when a number of poles are
    combined, all very close to the unit circle. Small errors in the eigth order
    coefficient, are multiplied when the eigth root is taken to give the pole
    location. These small errors lead to poles outside the unit circle and
    instability. Thanks to Julius Smith for leading me to the proper
    explanation.

    Execute the following code to evaluate the frequency response of a 10
    channel filterbank::

        fcoefs = MakeERBFilters(16000,10,100);
        y = ERBFilterBank([1 zeros(1,511)], fcoefs);
        resp = 20*log10(abs(fft(y')));
        freqScale = (0:511)/512*16000;
        semilogx(freqScale(1:255),resp(1:255,:));
        axis([100 16000 -60 0])
        xlabel('Frequency (Hz)'); ylabel('Filter Response (dB)');

    | Rewritten by Malcolm Slaney@Interval.  June 11, 1998.
    | (c) 1998 Interval Research Corporation
    |
    | (c) 2012 Jason Heeris (Python implementation)
    """
    T = 1 / fs
    # Change the followFreqing three parameters if you wish to use a different
    # ERB scale. Must change in ERBSpace too.
    # TODO: factor these out
    ear_q = 9.26449  # Glasberg and Moore Parameters
    min_bw = 24.7
    order = 1

    erb = width * ((centre_freqs / ear_q) ** order + min_bw ** order) ** (1 / order)
    B = 1.019 * 2 * np.pi * erb

    arg = 2 * centre_freqs * np.pi * T
    vec = np.exp(2j * arg)

    A0 = T
    A2 = 0
    B0 = 1
    B1 = -2 * np.cos(arg) / np.exp(B * T)
    B2 = np.exp(-2 * B * T)

    rt_pos = np.sqrt(3 + 2 ** 1.5)
    rt_neg = np.sqrt(3 - 2 ** 1.5)

    common = -T * np.exp(-(B * T))

    # TODO: This could be simplified to a matrix calculation involving the
    # constant first term and the alternating rt_pos/rt_neg and +/-1 second
    # terms
    k11 = np.cos(arg) + rt_pos * np.sin(arg)
    k12 = np.cos(arg) - rt_pos * np.sin(arg)
    k13 = np.cos(arg) + rt_neg * np.sin(arg)
    k14 = np.cos(arg) - rt_neg * np.sin(arg)

    A11 = common * k11
    A12 = common * k12
    A13 = common * k13
    A14 = common * k14

    gain_arg = np.exp(1j * arg - B * T)

    gain = np.abs(
        (vec - gain_arg * k11)
        * (vec - gain_arg * k12)
        * (vec - gain_arg * k13)
        * (vec - gain_arg * k14)
        * (T * np.exp(B * T)
           / (-1 / np.exp(B * T) + 1 + vec * (1 - np.exp(B * T)))
           ) ** 4
    )

    allfilts = np.ones_like(centre_freqs)

    fcoefs = np.column_stack([
        A0 * allfilts, A11, A12, A13, A14, A2 * allfilts,
        B0 * allfilts, B1, B2,
        gain
    ])

    return fcoefs


def make_erb_filters_ex(fs, centre_freqs, bandwidths=None, width=1.0):
    """
    Computes filter coefficients for a bank of Gammatone filters.

    Если bandwidths не переданы, используются стандартные расчёты ERB:

        erb = width * ((centre_freqs / ear_q)**order + min_bw**order)**(1/order)

    Если bandwidths переданы (как, например, рассчитанные по mel-фильтрам):

        erb = bandwidths  (возможно, умноженные на width, если требуется масштабирование)

    Аргументы:
      fs: частота дискретизации (Hz)
      centre_freqs: массив центральных частот фильтров (в Гц)
      bandwidths: (опционально) массив желаемых ширин фильтров (в Гц). Если None,
                  вычисляются по стандартной формуле ERB.
      width: масштабный коэффициент (по умолчанию 1.0)

    Возвращает:
      fcoefs: матрица коэффициентов фильтров, где каждая строка содержит 10 коэффициентов,
              необходимые для формирования гамматон фильтра.
    """
    T = 1 / fs
    ear_q = 9.26449  # параметр Glasberg and Moore
    min_bw = 24.7
    order = 1

    # Если bandwidths не заданы, рассчитываем ERB по стандартной формуле
    if bandwidths is None:
        erb = width * ((centre_freqs / ear_q) ** order + min_bw ** order) ** (1 / order)
    else:
        # Если bandwidths заданы, можно считать их желаемой шириной фильтра.
        # При необходимости можно применить масштабирование width.
        erb = width * bandwidths

    # Преобразуем ERB в параметр фильтра B
    B = 1.019 * 2 * np.pi * erb

    arg = 2 * np.pi * centre_freqs * T
    vec = np.exp(2j * arg)

    A0 = T
    A2 = 0
    B0 = 1
    B1 = -2 * np.cos(arg) / np.exp(B * T)
    B2 = np.exp(-2 * B * T)

    rt_pos = np.sqrt(3 + 2 ** 1.5)
    rt_neg = np.sqrt(3 - 2 ** 1.5)

    common = -T * np.exp(-B * T)

    k11 = np.cos(arg) + rt_pos * np.sin(arg)
    k12 = np.cos(arg) - rt_pos * np.sin(arg)
    k13 = np.cos(arg) + rt_neg * np.sin(arg)
    k14 = np.cos(arg) - rt_neg * np.sin(arg)

    A11 = common * k11
    A12 = common * k12
    A13 = common * k13
    A14 = common * k14

    gain_arg = np.exp(1j * arg - B * T)
    # Вычисляем gain так, чтобы компенсировать амплитудные эффекты фильтра
    gain = np.abs(
        (vec - gain_arg * k11) *
        (vec - gain_arg * k12) *
        (vec - gain_arg * k13) *
        (vec - gain_arg * k14) *
        (T * np.exp(B * T) / (-1 / np.exp(B * T) + 1 + vec * (1 - np.exp(B * T)))) ** 4
    )

    allfilts = np.ones_like(centre_freqs)

    fcoefs = np.column_stack([
        A0 * allfilts,
        A11, A12, A13, A14,
        A2 * allfilts,
        B0 * allfilts, B1, B2,
        gain
    ])

    return fcoefs


def erb_filterbank(wave, coefs):
    """
    :param wave: input data (one dimensional sequence)
    :param coefs: gammatone filter coefficients

    Process an input waveform with a gammatone filter bank. This function takes
    a single sound vector, and returns an array of filter outputs, one channel
    per row.

    The fcoefs parameter, which completely specifies the Gammatone filterbank,
    should be designed with the :func:`make_erb_filters` function.

    | Malcolm Slaney @ Interval, June 11, 1998.
    | (c) 1998 Interval Research Corporation
    | Thanks to Alain de Cheveigne' for his suggestions and improvements.
    |
    | (c) 2013 Jason Heeris (Python implementation)
    """
    output = np.zeros((coefs[:, 9].shape[0], wave.shape[0]))

    gain = coefs[:, 9]
    # A0, A11, A2
    As1 = coefs[:, (0, 1, 5)]
    # A0, A12, A2
    As2 = coefs[:, (0, 2, 5)]
    # A0, A13, A2
    As3 = coefs[:, (0, 3, 5)]
    # A0, A14, A2
    As4 = coefs[:, (0, 4, 5)]
    # B0, B1, B2
    Bs = coefs[:, 6:9]

    # Loop over channels
    for idx in range(0, coefs.shape[0]):
        # These seem to be reversed (in the sense of A/B order), but that's what
        # the original code did...
        # Replacing these with polynomial multiplications reduces both accuracy
        # and speed.
        y1 = sgn.lfilter(As1[idx], Bs[idx], wave)
        y2 = sgn.lfilter(As2[idx], Bs[idx], y1)
        y3 = sgn.lfilter(As3[idx], Bs[idx], y2)
        y4 = sgn.lfilter(As4[idx], Bs[idx], y3)
        output[idx, :] = y4 / gain[idx]

    return output

