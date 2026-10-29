import random
import math
#import soundfile as sf
import numpy as np
from numpy.polynomial import Polynomial
# подключим пакет интегрирования из библиотеки scipy
from scipy.io import wavfile
from scipy.signal import correlate, fftconvolve
from scipy.interpolate import interp1d
from scipy import integrate
from pydub import AudioSegment
from pydub.effects import speedup
import soundfile as sf
# import pyrubberband as pyrb
from audiostretchy.stretch import stretch_audio
# import pitch
# import time
# import librosa
import parselmouth as pm
from parselmouth.praat import call
from sk_speech import sk_volume as vm
from sk_speech import sk_vocal_cords as vc

import pyworld as pw

# import torch
# from torch_pitch_shift import *

# время паузы без вдоха
not_inhale_time = 0.34
# максимальное кол-во произносимых фонем на выдохе
# Совокупно по всем языкам на земле, человек может произносить от 30 до 35 гласных фонем
# эмпирически установил, что при обычной громкой речи можно произнести 15-20 фонем,
# при увеличении их числа громкость речи падает
max_phoneme_inhale = 18
# максимальный объем легких
max_volume_lungs = 3500
# объем легких во время вдоха (ДО) - 500 см^3
volume_full_inhale = 500
# объем легких во время дополнительного вдоха (РОВ) - 1500 см^3
# это сколько мы можем еще вдохнуть после полного вдоха (резервный объем вдоха и выдоха)
volume_partial_inhale = 1500
# резервный объем легких
volume_reserve_lungs = 1500
# сколько нужно кислорода для полного вдоха
# в полных легких мы можем получить только 6% кислорода
oxygen_full_inhale = volume_full_inhale * 0.06
# кислород нужный для одной фонемы
oxygen_phoneme = oxygen_full_inhale / max_phoneme_inhale
# кислород нужный для одного слова
# максимум можно произнести не более 8 слов
oxygen_word = oxygen_full_inhale / 8
# сколько времени надо на выдох 1 см3 легких
# за 1 сек делаться один вдох, один вдох это 500 см3
# считаем время одного см3
exhaling_lung_time = 1 / volume_full_inhale
# обобщенный радиус всех альвеол, который будет меняться от 0 до R (alveolar_radius)
# (3500*3/(4*Pi))^(1/3) = 9.41874729681
alveolar_radius = (3. * max_volume_lungs / (4. * math.pi)) ** (1./3.)
# максимальное время в спокойном состоянии, чтобы сделать вдох на полный объем легких
alveolar_t_max = 7
# соотношение максимального радиуса альвеолы к времени надувания.
# сферу какого радиуса мы надуем за 1 сек.
r_t = alveolar_radius / alveolar_t_max

options = {"freq": True, "amplitude": True, "period": True,
           "change": {"pitch_freq": True, "pitch_amplitude": False,
                      "formant_freq": False, "formant_amplitude": True,
                      "vowel_freq": False, "vowel_amplitude": False, },
           "pitch": True, "formants": True, "vowels": False, "formant_max": 5}

emotion_word_break = {
    "disappointment": 7,
    "sadness": 7,
    "annoyance": 7,
    "neutral": 7,
    "disapproval": 7,
    "realization": 7,
    "nervousness": 7,
    "approval": 7,
    "joy": 7,
    "anger": 7,
    "embarrassment": 7,
    "caring": 7,
    "remorse": 7,
    "disgust": 7,
    "grief": 7,
    "confusion": 7,
    "relief": 7,
    "desire": 7,
    "admiration": 7,
    "optimism": 7,
    "fear": 7,
    "love": 7,
    "excitement": 7,
    "curiosity": 7,
    "amusement": 7,
    "surprise": 7,
    "gratitude": 7,
    "pride": 7,
}

emotion_break = ('fear', 'anger', 'nervousness', 'disappointment', 'sadness', 'annoyance')
emotion_horror = ('fear',)
horror_words = {
    "en": ("oooh...", "ah...", "ooooh...", "ahh...", "oooooh...", "ahhh...",
           "Oooh...", "Ah...", "Ooooh...", "Ahh...", "Oooooh...", "Ahhh...",),
    "ru": ("оооо...", "аа...", "ооооо...", "ааа...", "оооооо...", "аааа...",
           "Оооо...", "Аа...", "Ооооо...", "Ааа...", "Оооооо...", "Аааа..."),
}

not_break_words = {
    "en": ("i", "the", "a", "and", "or", "on", "in", "is", "of", "are", "as", "an", "yet", "nor", "so", "but",
           "being", "because", "if"),
    "ru": ("и", "или", "не", "для", "в", "из", "из-за", "но", "если", "как", "ни", "о", "с", "во", "со", "по", "про",
           "под", "вне", "на", "у", "это", "так", "как"),
}

break_words = {
#    "en": ("and", "or", "but", "so", "because", "although", "that"),
    "en": ("and", "or", "but", "so", "because", "although"),
    "ru": ("и", "или", "но", "потому", "поэтому", "если", "это", "так"),
}


hop_length = 256
max_padding = 2 * hop_length

def calc_time_phoneme(num_phonemes):
    time_phoneme = 0.46 * (num_phonemes - 0.9) ** (-0.40)

    return time_phoneme

def set_speed(sound, speed):
    sound.export(f'test_new/tmp.wav', format="wav")
    stretch_audio(f'test_new/tmp.wav', f'test_new/tmp.wav', ratio=speed)
    sound = AudioSegment.from_file(f'test_new/tmp.wav')

    return sound


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

# индекс Хильдебрандта
# Q = ЧСС/ЧДД,
# где ЧДД – частота дыхательных движений. Норма Q – 2.9–4.8.
def IndexQ(heart_rate, respiratory_rate):
  return heart_rate / respiratory_rate

# breath array {'begin_time': .0, 'duration': .0}
# кол-во ЧДД в минуту
def count_respiratory_rate(cur_time, breaths):
    milliseconds = cur_time - 60.0 * 1000
    cnt = 0
    t_all = 0
    for idx, breath in enumerate(breaths):
        if breath["begin_time"] + breath["duration"] < milliseconds:
            breaths.pop(idx)
        else:
            cnt = cnt + 1
            t_all = t_all + breath["duration"]
    cnt = 60.0 * 1000 * cnt / t_all
    return cnt, breaths

# МЧСС
def max_heart_rate(gender, age):
    # формула Марты Гулати: МЧСС = 206 — (0,88 * возраст)
    if gender == 'female':
        m = 206 - 0.88 * age
    # Формула Танака: МЧСС = 208 — (0,7 * возраст)
    else:
        m = 208 - 0.7 * age
    return m

def recovery_heart_rate(delta_time, delta_hr):
    if delta_hr > 0:
        k = math.log(1 + delta_hr / (20 * 60)) # 30 минут восстановление
    else:
        k = math.log(1 + delta_hr / (10 * 60)) # 10 минут восстановление
    return delta_time*k

def recovery_respiratory_rate(delta_time, delta_rr):
    if delta_rr > 0:
        k =  math.log(1 + delta_rr / (5 * 60)) # 30 минут восстановление
    else:
        k =  math.log(1 + delta_rr / (3 * 60)) # 10 минут восстановление
    return delta_time*k

# опишем подынтегральную функцию
def hormone_metabolism(t, hormone, k, ad_k, hr_k):
    return max(hormone * ad_k * math.exp(-k*t*hr_k), 0)

def calc_metabolism(state_ai, delta_time):

    # Basal Metabolic Rate (BMR) это минимальное количество энергии, необходимое для обеспечения нормальной жизнедеятельности организма в стандартных условиях.
    # https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%BE%D0%B1%D0%BC%D0%B5%D0%BD
    basal_metabolism = 0.0770256355 # ккал в секунду
    stress = state_ai["hormones"]["adrenalin"]

    energy_need = basal_metabolism * stress
    energy_available_gl = state_ai["metabolism"]["glucose"] * state_ai["hormones"]["cortisol"]
    energy_available_o2 = state_ai["respiratory"]["oxygen"] / 6
    energy_available = min(energy_available_gl, energy_available_o2)
    state_ai["metabolism"]["energy"] += energy_available
       
    delta_oxygen = energy_available / 6
    state_ai["respiratory"]["oxygen"] -= delta_oxygen
    state_ai["respiratory"]["carbon_dioxide"] += delta_oxygen


    # Определить константу скорости метаболизма k
    # Скорость метаболизма k можно найти в литературных источниках. 
    # Например, для адреналина время полураспада в крови составляет около 2 минут. 
    # Это означает, что через 2 минуты уровень адреналина уменьшится вдвое. Исходя из этого, k можно рассчитать как:
    T_half = 2 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (2 минуты)

    # Экспоненциальное снижение
    # Это происходит потому, что поглощение или распад гормона зависит от его текущей концентрации в крови. 
    # Чем больше гормона в крови, тем быстрее его будет поглощать организм, и наоборот.
    state_ai["hormones"]["adrenalin"] *= math.exp(-k*delta_time)

    T_half = 2.5 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (2.5 минуты)
    state_ai["hormones"]["norepinephrine"] *= math.exp(-k*delta_time)

    T_half = 60 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (60 минуты)
    state_ai["hormones"]["cortisol"] *= math.exp(-k*delta_time)

    return state_ai

def calc_arterial_pressure(state_ai, delta_time):
    ad_cur = (state_ai["arterial_pressure"]["systolic"]["cur"] - state_ai["arterial_pressure"]["diastolic"]["cur"])
    ad_norm = (state_ai["arterial_pressure"]["diastolic"]["norm"] - state_ai["arterial_pressure"]["diastolic"]["norm"])
    ad_k = ad_cur / ad_norm
    hr_k = state_ai["heart_rate"]["cur"] / state_ai["heart_rate"]["norm"]

    A = state_ai["hormones"]["adrenalin"]
    N = state_ai["hormones"]["norepinephrine"]
    k = 0.1 # скорость снижения гормона

    # выполним интегрирование
    dA, err = integrate.quad(hormone_metabolism, 0.0, delta_time, args=(abs(A), k, ad_k, hr_k))
    dN, err = integrate.quad(hormone_metabolism, 0.0, delta_time, args=(abs(N), k, ad_k, hr_k))

    # Увеличение адреналина на максимальном уровне (1.0) может увеличить систолическое АД примерно на 20-40 мм рт. ст. и диастолическое АД на 10-20 мм рт. ст..
    alpha = 30.0
    beta = 15.0
    ad_systolic_deltaA = alpha * dA
    ad_systolic_deltaN = beta * dN
    ad_systolic = state_ai["arterial_pressure"]["systolic"]["cur"] + (ad_deltaA + ad_deltaN)
    ad_systolic = max(min(ad_systolic , state_ai["arterial_pressure"]["systolic"]["max"]), state_ai["arterial_pressure"]["systolic"]["min"])

    # Увеличение норадреналина на максимальном уровне (1.0) может привести к увеличению систолического АД примерно на 30-50 мм рт. ст. и диастолического АД на 15-30 мм рт. ст..
    alpha = 40.0
    beta = 20.0
    ad_diastolic_deltaA = alpha * A * (1.0 - math.exp(-k*delta_time) ) / k
    ad_diastolic_deltaN = beta * N * (1.0 - math.exp(-k*delta_time) ) / k
    ad_diastolic = state_ai["arterial_pressure"]["diastolic"]["cur"] + (ad_deltaA + ad_deltaN)
    ad_diastolic = max(min(ad_diastolic , state_ai["arterial_pressure"]["diastolic"]["max"]), state_ai["arterial_pressure"]["diastolic"]["min"])

    k = 0.1 # Константа скорости восстановления
    ad_systolic = state_ai["arterial_pressure"]["systolic"]["norm"] + (ad_systolic - state_ai["arterial_pressure"]["systolic"]["norm"])*math.exp(-k*delta_time)
    ad_diastolic = state_ai["arterial_pressure"]["diastolic"]["norm"] + (ad_diastolic - state_ai["arterial_pressure"]["diastolic"]["norm"])*math.exp(-k*delta_time)

    state_ai["arterial_pressure"]["cur"]["systolic"] = ad_systolic
    state_ai["arterial_pressure"]["cur"]["diastolic"] = ad_diastolic

    # Определить константу скорости метаболизма k
    # Скорость метаболизма k можно найти в литературных источниках. 
    # Например, для адреналина время полураспада в крови составляет около 2 минут. 
    # Это означает, что через 2 минуты уровень адреналина уменьшится вдвое. Исходя из этого, k можно рассчитать как:
    T_half = 2 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (2 минуты)

    # Экспоненциальное снижение
    # Это происходит потому, что поглощение или распад гормона зависит от его текущей концентрации в крови. 
    # Чем больше гормона в крови, тем быстрее его будет поглощать организм, и наоборот.
    A = A * math.exp(-k*delta_time)
    state_ai["hormones"]["adrenalin"] = A

    T_half = 2.5 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (2.5 минуты)
    N = N * math.exp(-k*delta_time)
    state_ai["hormones"]["norepinephrine"] = N

    return state_ai

def calc_heart_rate(state_ai, delta_time):

    ad_cur = (state_ai["arterial_pressure"]["systolic"]["cur"] - state_ai["arterial_pressure"]["diastolic"]["cur"])
    ad_norm = (state_ai["arterial_pressure"]["diastolic"]["norm"] - state_ai["arterial_pressure"]["diastolic"]["norm"])
    ad_k = ad_cur / ad_norm
    hr_k = state_ai["heart_rate"]["cur"] / state_ai["heart_rate"]["norm"]

    A = state_ai["hormones"]["adrenalin"]
    N = state_ai["hormones"]["norepinephrine"]

    # На основании доступных данных можно утверждать, что:
    # Адреналин (A) вызывает значительное увеличение ЧСС. 
    # При максимальном уровне адреналина, он может увеличить ЧСС на 30-50 ударов в минуту в стрессовых или экстренных ситуациях.
    # Норадреналин (N) тоже увеличивает ЧСС, но менее интенсивно по сравнению с адреналином. 
    # Например, норадреналин может увеличить ЧСС на 10-20 ударов в минуту при максимальном уровне.
    alpha = 40.0 # при максимальном уровне адреналина (A = 1), ЧСС может увеличиться на 40 ударов в минуту (среднее значение между 30 и 50).
    beta = 15.0 # для норадреналина, по клиническим данным, максимальный уровень (N = 1) увеличивает ЧСС на 15 ударов в минуту (среднее значение между 10 и 20).
    k = 0.1 # скорость снижения гормона

    dA, err = integrate.quad(hormone_metabolism, 0.0, delta_time, args=(abs(A), k, ad_k, hr_k))
    dN, err = integrate.quad(hormone_metabolism, 0.0, delta_time, args=(abs(N), k, ad_k, hr_k))

    hr_deltaA = alpha * dA
    hr_deltaN = beta * dN

    hr_new = state_ai["heart_rate"]["norm"] + (hr_deltaA + hr_deltaN)
    hr_new = max(min(hr_new, state_ai["heart_rate"]["max"]), state_ai["heart_rate"]["min"])

    hr_new = hr_new - recovery_heart_rate(delta_time, hr_new - state_ai["heart_rate"]["norm"])
    state_ai["cur"] = hr_new

    # Определить константу скорости метаболизма k
    # Скорость метаболизма k можно найти в литературных источниках. 
    # Например, для адреналина время полураспада в крови составляет около 2 минут. 
    # Это означает, что через 2 минуты уровень адреналина уменьшится вдвое. Исходя из этого, k можно рассчитать как:
    T_half = 2 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (2 минуты)

    # Экспоненциальное снижение
    # Это происходит потому, что поглощение или распад гормона зависит от его текущей концентрации в крови. 
    # Чем больше гормона в крови, тем быстрее его будет поглощать организм, и наоборот.
    A = A * math.exp(-k*delta_time)
    state_ai["hormones"]["adrenalin"] = A

    T_half = 2.5 * 60
    k = ln(2)/ T_half # T_half — это время полураспада (2.5 минуты)
    N = N * math.exp(-k*delta_time)
    state_ai["hormones"]["norepinephrine"] = N

    return state_ai


def calc_respiratory_rate(rr, hr, ad, hormones, delta_time):

    if rr_cur > rr_norm:
        k = math.cos(35.1 * math.pi / 180)
        # выполним интегрирование
        dv, err = integrate.quad(delta_impact, 0.0, delta_time, args=(abs(impact_respiratory), k))
        # print(f"integrate respiratory {delta_time} {impact_respiratory} {k} {dv}")

        dv = math.copysign(dv, impact_respiratory)
        k2 = 10.5
        dv2 = dv * k2
        rr_new = rr_cur + dv2
        # print(rr_new, impact_heart, dv, dv2, delta_time)
    else:
        k = math.cos(20.1 * math.pi / 180)
        dv, err = integrate.quad(delta_impact, 0.0, delta_time, args=(abs(impact_respiratory), k))
        dv = math.copysign(dv, impact_respiratory)
        k2 = 6
        dv2 = dv * k2
        rr_new = rr_cur + dv2
        # print(rr_new, impact_respiratory, dv, dv2, delta_time)

    rr_new = max(min(rr_new, rr_max), rr_min)

    rr_new = rr_new - recovery_respiratory_rate(delta_time, rr_new - rr_norm)

    if rr_new >= rr_norm:
        v = (rr_new - rr_norm) / (rr_max - rr_norm)
        if impact_respiratory > 0:
            impact_respiratory = impact_respiratory - (delta_time * v*impact_respiratory / 10)
        else:
            impact_respiratory = impact_respiratory + (delta_time * v*impact_respiratory / 10)
    elif rr_cur < rr_norm:
        v = (rr_norm - rr_new) / (rr_norm - rr_min)
        if impact_respiratory < 0:
            impact_respiratory = impact_respiratory - (delta_time * v*impact_respiratory / 20)
        else:
            impact_respiratory = impact_respiratory + (delta_time * v*impact_respiratory / 20)

    if rr_new > respiratory_rate_norm:
        d_hr = heart_rate_max - heart_rate_norm
        a = d_hr / (respiratory_rate_max - respiratory_rate_norm)
    else:
        d_hr = heart_rate_norm - heart_rate_min
        a = d_hr / (respiratory_rate_norm - respiratory_rate_min)
    d = (rr_new - rr_cur) * a / delta_time

    # impact_heart = impact_heart + d * 0.01
    impact_heart = impact_heart + (d / d_hr)

    return rr_new, impact_respiratory, impact_heart

def count_words(sentence):
    words = sentence.split(' ')
    index = 0
    for idx, word in enumerate(words):
        # last_long_word = len(word) > 2
        last_long_word = number_of_syllables(word) > 1
        if last_long_word:
            index = index + 1
        else:
            index = index + 0.5
    return index


# t_left - сколько воздуха у нас в легких
def time_pause(oxygen, t_left, em_name, em_score, cur_word_count, type_):
    em_time = 0.34
    phoneme_time = 0.22
    t_need = (8 - cur_word_count) * phoneme_time
    t_full = 8 * phoneme_time
    t_em = 2 * em_time
    dO2 = 0
    t_cur = 0
    # f - полный вздох (full), p - дополнительный вдох (partial), n - без вдоха (not)
    # если конец предложения, то делаем полный выдох и полный вдох
    if type_ == 'p' or oxygen < 0.1:
        t = t_full + t_left
        res = f'[pause_p_f_{int(t * 1000)}_{em_name}_{em_score}]'
        t_cur = t_full - t_need
        dO2 = t_full
    # если это знак препинания, то можно сделать дополнительного вдох
    elif type_ == 'm':
        t = t_need - t_left
        # выдыхаем и делаем вдох на нужное кол-во воздуха
        if oxygen < 0.3:
            t = t_need + t_left
            res = f'[pause_m_p_{int(t * 1000)}_{em_name}_{em_score}]'
            dO2 = t_need
        # дополнительно вдыхаем
        elif t - t_em >= 0:
            res = f'[pause_m_p_{int(t * 1000)}_{em_name}_{em_score}]'
            dO2 = t_need
        else:
            # вздоха делать не нужно, пауза это время двух фонем
            t = t_em
            res = f'[pause_m_n_{int(t * 1000)}_{em_name}_{em_score}]'
    # если это внутри предложения, то стараемся все делать без вдоха
    else:
        t = t_need - t_left
        if oxygen < 0.3:
            t = t_need + t_left
            res = f'[pause_n_p_{int(t * 1000)}_{em_name}_{em_score}]'
            dO2 = t_need
        # дополнительного вдыхаем
        elif t - t_em >= 0:
            # дополнительного вдыхаем
            res = f'[pause_n_p_{int(t * 1000)}_{em_name}_{em_score}]'
            dO2 = t
        else:
            # вздоха делать не нужно, пауза это время одной фонем
            t = em_time
            res = f'[pause_n_n_{int(t * 1000)}_{em_name}_{em_score}]'

    t_cur = t_cur * (100 - 10 * math.log(1 + t_cur)) / 100
    oxygen = min(max(oxygen + 2 * (math.exp(dO2) - 1), 0), 10)
    return res, t_cur, oxygen


def adaptation_break(em_name, em_score, text, min_words, max_words, lang):
    global emotion_break
    global emotion_horror
    global horror_words
    global not_break_words
    global break_words
    # logger = logging.getLogger("ray.serve")

    # logger.info(f"adaptation_break {em_name} text: {text}")

    if em_name in emotion_break:
        sentences = []
        sentence = ''
        orig = text

        text = text.replace(",", ".")
        text = text.replace("-", ".")
        # if text[-1] in '!?':
        #     text = text.replace(",", text[-1])
        #     text = text.replace("-", text[-1])
        # else:
        #     text = text.replace(",", ".")
        #     text = text.replace("-", ".")
        is_uppercase = False
        for i in range(0, len(text)):
            if is_uppercase:
                if text[i] in (' ', '.', ',', '!', '?', '-'):
                    continue
                sentence = sentence + text[i].title()
                if text[i] == '+':
                    continue
                is_uppercase = False
            else:
                if (i > 1) and text[i - 1] in ('.', '!', '?', '-'):
                    sentence = sentence + text[i].title()
                else:
                    sentence = sentence + text[i]

            if (text[i] in ('.', '!', '?') and i > 1 and text[max(i - 1, 0)] != '.' and text[max(i - 2, 0)] != '.'):
                if sentence:
                    sentences.append(sentence)
                    if orig[i] == ',':
                        sentences.append('[pause_m]')
                    else:
                        sentences.append('[pause_p]')

                sentence = ""

                if em_name in emotion_horror:
                    if random.randint(0, 100) < 5 * em_score:
                        index = random.randint(0, len(horror_words[lang]) - 1)
                        sentences.append(horror_words[lang][index])
                        sentences.append('[pause_m]')

                is_uppercase = True
        if sentence:
            sentences.append(sentence)
            sentences.append('[pause_p]')

        # print(sentences)
        # break sentence on count word
        if min_words > 0:
            sentences2 = []
            for sentence in sentences:
                word_count = emotion_word_break[em_name]
                count = word_count
                words = sentence.split(' ')
                index = 0.0
                s = ""
                # print(count)
                last_long_word = False
                sentence_finish = False
                word_finish = False
                last_word = ""
                if sentence[0:7] == ('[pause_'):
                    sentences2[-1] = sentence
                    continue

                # max_char_count = random.randint(min_words, max_words)
                for idx, word in enumerate(words):
                    # print(word)
                    # print(word_finish)
                    # if word_finish or ((len(word) >= max_char_count) and (index >= count) and last_long_word):
                    is_break_word = s and word in break_words[lang]
                    is_break_sentence = word_finish or ((index > count + 1) and last_long_word)
                    is_break_sentence = is_break_sentence and last_word not in not_break_words[lang]
                    if is_break_sentence or is_break_word:
                        # print(max_char_count)
                        # print(count)
                        # print(s)
                        s = s.strip()
                        if len(s) > 0:
                            sentence_finish = s[len(s) - 1] in ('.', ',', '!', '?', '-')
                        else:
                            sentence_finish = False
                        # logger.info(f"adaptation_break {s}")
                        sentences2.append(s)
                        if sentence_finish:
                            sentences2.append('[pause_p]')
                        else:
                            sentences2.append('[pause_n]')
                        count = max(word_count + random.randrange(-1, 1 + round(em_score)), 1)
                        # print(count)
                        index = 0
                        s = ''
                    s = s + ' ' + word
                    if word:
                        word_finish = word[len(word) - 1] in ('.', ',', '!', '?', '-')
                    else:
                        word_finish = False
                    # print(word[len(word) - 1])
                    # print(word_finish)
                    last_long_word = number_of_syllables(word) > 1
                    # last_long_word = True
                    if last_long_word:
                        index = index + 1
                    else:
                        index = index + 0.5
                    last_word = word
                s = s.strip()
                if s:
                    # logger.info(f"adaptation_break {s}")
                    # print(s)
                    # print(sentence_finish)
                    if not word_finish and not sentence_finish and index < count and len(sentences2) > 0:
                        sentences2[-1] = sentences2[-1] + ' ' + s
                    else:
                        sentences2.append(s)
                        sentences2.append('[pause_p]')

            sentences = sentences2

    else:
        sentences = [text, '[pause_p]']

    sentences.insert(0, '[pause_p]')
    return sentences

def get_count_phoneme(phonemes):
    cnt = 0
    for phoneme in phonemes.split("-"):
        if phoneme.strip():
            cnt = cnt + 1
    return cnt

def number_of_syllables(text):
    vowels = "аеёийоуыэюяaeiouy"
    is_consonants = False
    is_vowels = False
    is_punctuation_mark = False
    count = 0
    text = text.lower()
    for letter in text:
        n_vowels = letter in vowels
        if letter == ' ':
            if not is_punctuation_mark and is_vowels:
                count += 1
            is_consonants = True
            is_vowels = False
            is_punctuation_mark = True
        elif letter in ('!', '?'):
            # if not is_punctuation_mark:
            #     count += 0.5
            if not is_punctuation_mark and is_vowels:
                count += 1
            is_consonants = True
            is_vowels = False
            is_punctuation_mark = True
        elif is_consonants and n_vowels:
            is_vowels = True
            is_consonants = False
            is_punctuation_mark = False
        elif is_vowels and n_vowels:
            is_vowels = True
            is_consonants = False
            is_punctuation_mark = False
        elif is_vowels and not n_vowels:
            count += 1
            is_consonants = True
            is_vowels = False
            is_punctuation_mark = False
        else:
            is_consonants = not n_vowels
            is_vowels = n_vowels
            is_punctuation_mark = False
        # print(letter, count, is_punctuation_mark, is_consonants, is_vowels, n_vowels)
    if is_vowels:
        count += 1

    return count


# сколько объема легких мы вдохнем за указанное время при условии, что они пустые при нормальном состоянии
def t_to_r(t):
    global r_t
    #r = t * r_t
    k = alveolar_radius / math.log(1+alveolar_t_max)
    r = k * math.log(t/2.1 + 1)
    return r

def r_to_t(r):
    global r_t
    # t = r / r_t
    k = alveolar_radius / math.log(1+alveolar_t_max)
    t = 2.1*math.exp(r / k) - 2.1
    return t

def inhale_time_to_volume_new(t):
    r = t_to_r(t)

    v = (4. * math.pi * r ** 3) / 3.
    return v

def inhale_volume_to_time_new(volume):
    r = (volume * 3. / (4 * math.pi)) ** (1./3.)
    t = r_to_t(r)

    return t

def prob_inhale(prob_full, prob_partial, prob_not):
    is_prob_full = False
    is_prob_partial = False
    is_prob_not = False
    np.random.seed(0)

    if prob_full > 0 and prob_partial == 0 and prob_not == 0:
        is_prob_full = True
    elif prob_partial > 0 and prob_full == 0 and prob_not == 0:
        is_prob_partial = True
    elif prob_not > 0 and prob_partial == 0 and prob_full == 0:
        is_prob_not = True
    elif prob_not == 0:
        prob = prob_full + prob_partial
        prob_val = random.uniform(0, prob)
        is_prob_partial = prob_val < prob_full
        is_prob_full = not is_prob_partial
    elif prob_partial == 0:
        prob = prob_full + prob_not
        prob_val = random.uniform(0, prob)
        is_prob_not = prob_val < prob_full
        is_prob_full = not is_prob_not
    elif prob_full == 0:
        prob = prob_not + prob_partial
        prob_val = random.uniform(0, prob)
        is_prob_not = prob_val < prob_not
        is_prob_full = not is_prob_not
    else:
        prob = prob_full + prob_partial + prob_not
        prob_val = random.uniform(0, prob)

        is_prob_not = (prob_val >= 0) and (prob_val < prob_not)
        is_prob_partial = (prob_val >= prob_not) and (prob_val <= prob - prob_full)
        is_prob_full = (prob_val > prob - prob_full)

    return is_prob_not, is_prob_partial, is_prob_full

# расчет вдоха
def inhale(lung_volumes, oxygen, stress, air_speed_inhale, is_prob_partial, is_prob_full):
    global oxygen_full_inhale
    global volume_full_inhale
    global exhaling_lung_time
    global not_inhale_time
    global max_volume_lungs

    s = (1 + min(stress, 1))
    volume_need = lung_volumes + volume_full_inhale/s
    small_oxygen = oxygen < 0.3
    small_volume_lung = lung_volumes < volume_reserve_lungs
    overflow_volume_lungs = volume_need > max_volume_lungs

    small_oxygen = False
    # small_volume_lung = False

    time_pause = 0
    time_inhale = 0
    # выдыхаем и делаем обычный вдох
    if small_oxygen or small_volume_lung or is_prob_full or overflow_volume_lungs:
        type_inh = 'f'

        # v = volume_full_inhale
        # if lung_volumes < volume_reserve_lungs:
        #     v = v + volume_full_inhale
            # время вдоха текущего объема легких
            # t3 = inhale_volume_to_time_new(lung_volumes)
            # время вдоха резервного объема легких + время обычного вдоха
            # t2 = inhale_volume_to_time_new(volume_reserve_lungs + volume_full_inhale)
            # время вдоха резервного объема легких
            # t1 = inhale_volume_to_time_new(volume_reserve_lungs)
            # k = (t2 - t1) / time_inhale
            # time_inhale = t3*k + time_inhale
        t3 = inhale_volume_to_time_new(lung_volumes)
        t4 = inhale_volume_to_time_new(lung_volumes + volume_full_inhale/s)
        time_inhale = (t4 - t3)

        oxygen = oxygen_full_inhale
        lung_volumes = volume_reserve_lungs + time_inhale*air_speed_inhale
    # если кислорода меньше, чем нужно для произнесения речи
    elif is_prob_partial:
        t3 = inhale_volume_to_time_new(lung_volumes)
        t4 = inhale_volume_to_time_new(lung_volumes + volume_full_inhale/s)
        time_inhale = (t4 - t3)

        # дополнительно вдыхаем
        type_inh = 'p'
        # oxygen_inhale = volume_full_inhale * 0.06

        oxygen = oxygen + oxygen_full_inhale
        lung_volumes = lung_volumes + time_inhale*air_speed_inhale
    else:
        # вздоха делать не нужно, пауза это время двух фонем
        type_inh = 'n'
        time_pause = not_inhale_time

    return type_inh, lung_volumes, oxygen, time_inhale, time_pause

def exhale(lung_volumes, oxygen, time_speech, stress_phoneme, is_block_prob_not, type_):
    # f - полный вздох (full) pause_p, p - дополнительный вдох (partial) pause_m, n - без вдоха (not) pause_n
    # если конец предложения, то делаем до конца выдох и полный вдох
    # if type_ == 'p' or oxygen < 0.1:
    if type_ == 'p':
        if is_block_prob_not:
            prob_not = 0
            prob_partial = 50 * stress
        else:
            prob_not = 5 * stress * stress_phoneme
            prob_partial = 60 * stress
        prob_full = 100 - (prob_partial + prob_not)
    # если это знак препинания, то можно сделать дополнительный вдох
    elif type_ == 'm':
        prob_full = 5 * stress
        prob_not = 45 * stress
        prob_partial = 100 - (prob_full + prob_not)
    # если это внутри предложения, то стараемся все делать без вдоха
    else:
        prob_not = 50 * stress
        prob_partial = 25 * stress
        prob_full = max(100 - (prob_partial + prob_not), 0)

    is_prob_not, is_prob_partial, is_prob_full = prob_inhale(prob_full, prob_partial, prob_not)

    # если конец предложения, то делаем до конца выдох
    if is_prob_full:
        t1 = inhale_volume_to_time_new(lung_volumes)
        t2 = inhale_volume_to_time_new(volume_reserve_lungs)
        time_exhale = (t1 - t2) * 1.3
        oxygen = 0
        lung_volumes = volume_reserve_lungs
    # мы сказали быстрее выдоха
    # мы не будем выдыхать оставшееся
    # поэтому пересчитаем расход кислорода
    else:
        # oxygen_speech = oxygen_speech * speech_time / time_exhale
        # oxygen = oxygen - oxygen_speech
        # volume = oxygen_speech / 0.06
        t0 = inhale_volume_to_time_new(lung_volumes) * 1.3
        t = t0 - time_speech
        t = t / 1.3
        volume = inhale_time_to_volume_new(t)
        oxygen = max(oxygen - (lung_volumes - volume) * 0.06, 0)
        lung_volumes = volume
        time_exhale = 0

    return lung_volumes, oxygen, time_exhale, is_prob_not, is_prob_partial, is_prob_full


em_score = 0

text = ("Yes, I'm crazy. When I realized that the whole world was a terrible black joke, I went crazy! I admit it!... "
        "You are not a fool, you must feel the situation. Do you know how many times we were on the verge of "
        "World War III because of a bunch of geese on a computer screen? Do you know what caused the last world war? "
        "The dispute is about how many telegraph poles Germany owes to its war creditors! Telegraph poles! What a "
        "joke! Everything we love, everything we fight for - everything is doomed! Well, don't you see the funny side "
        "of the situation yet?")
sentences = adaptation_break("nervousness", em_score, text, 3, 4, 'en')
print(sentences)
breath_sentences = sentences

state_ai = {
    "hormones": {"adrenalin": 0.0, "norepinephrine": 0.0, "cortisol": 0.0, "serotonin": 0.0, "oxytocin": 0.0, "dopamine": 0.0, "endorphin": 0.0, },
    "heart_rate": {"cur": 0.0, "norm": 0.0, "max": 0.0, "min": 0.0},
    "respiratory_rate": {"cur": 0.0, "norm": 0.0, "max": 0.0, "min": 0.0},
    "arterial_pressure": {"systolic": {"cur": 0.0, "norm": 0.0, "max": 0.0, "min": 0.0} , 
                          "diastolic": {"cur": 0.0, "norm": 0.0, "max": 0.0, "min": 0.0}
                         },
    "respiratory": {"oxygen": 0.0, "carbon_dioxide": 0.0, "lung_volumes": 0.0, "inhale_time_min": 0.0, "time_inhale": 0.0, "air_speed_inhale": 0.0, "add_time_inhale": 0.0, "time_respiratory": 0.0, },
    "metabolism": {"glucose": 0.0, "energy": 0.0},
    "index_q": 0.0,
    "time_speech_time": 0.0,
    "sex": 'male',
    "height": 175,
    "age": 35,
}

# Норма 60 до 100 ударов в минуту
state_ai["heart_rate"]["norm"] = 72
# Норма от 12 до 20 вдохов в минуту
state_ai["respiratory_rate"]["norm"] = 16
# Норма Q – 2.9–4.8.
state_ai["index_q"] = IndexQ(state_ai["heart_rate"]["norm"], state_ai["respiratory_rate"]["norm"])

state_ai["heart_rate"]["cur"] = state_ai["heart_rate"]["norm"]
state_ai["heart_rate"]["max"] = max_heart_rate(state_ai["sex"], state_ai["age"])
state_ai["heart_rate"]["min"] = 40

state_ai["respiratory_rate"]["max"] = state_ai["heart_rate"]["max"] / state_ai["index_q"]
state_ai["respiratory_rate"]["min"] = state_ai["heart_rate"]["min"] / state_ai["index_q"]

state_ai["respiratory"]["inhale_time_min"] = ((60./state_ai["respiratory_rate"]["norm"])/2.3)/math.log(state_ai["respiratory_rate"]["max"])

state_ai["respiratory"]["lung_volumes"] = volume_reserve_lungs
fn = 0

time_breaths = []
cur_time = 0
state_ai["respiratory_rate"]["cur"] = state_ai["heart_rate"]["cur"] / state_ai["index_q"]
state_ai["respiratory"]["time_respiratory"] = 60. / state_ai["respiratory_rate"]["cur"]
for i in range(round(state_ai["respiratory_rate"]["cur"])):
    time_breaths.append({'begin_time': int(cur_time * 1000), 'duration': int(state_ai["respiratory"]["time_respiratory"] * 1000)})
    cur_time = cur_time + state_ai["respiratory"]["time_respiratory"]

sentences = []
mul_resp_rate = state_ai["respiratory_rate"]["cur"] / state_ai["respiratory_rate"]["norm"]

audio = None
heart_rate_old = state_ai["heart_rate"]["cur"]
phonemes = [
    "Y-EH-S",
    "AY-M- -K-R-EY-Z-IY",
    "-W-EH-N- -AY- -R-IY-AH-L-AY-Z-D- -DH-AE-T- -DH-AH- -HH-OW-L- -W-ER-L-D- -W-AA-Z- -AH- -T-EH-R-AH-B-AH-L- -B-L-AE-K- -JH-OW-K-EY",
    "AY- -W-EH-N-T- -K-R-EY-Z-IY",
    "AY- -AH-D-M-IH-T- -IH-T",
    "Y-UW- -AA-R- -N-AA-T- -AH- -F-UW-L",
    "Y-UW- -M-AH-S-T- -F-IY-L- -DH-AH- -S-IH-CH-UW-EY-SH-AH-N",
    "D-UW- -Y-UW- -N-OW- -HH-AW- -M-EH-N-IY- -T-AY-M-Z- -W-IY- -W-ER- -AA-N- -DH-AH- -V-ER-JH- -AH-V- -W-ER-L-D- -W-AO-R- -AY-AY",
    "B-IH-K-AO-Z- -AH-V- -AH- -B-AH-N-CH- -AH-V- -G-IY-S- -AA-N- -AH- -K-AH-M-P-Y-UW-T-ER- -S-K-R-IY-N",
    "D-UW- -Y-UW- -N-OW- -W-AH-T- -K-AA-Z-D- -DH-AH- -L-AE-S-T- -W-ER-L-D- -W-AO-R",
    "DH-AH- -D-IH-S-P-UW-T- -IH-Z- -AH-B-AW-T- -HH-AW- -M-EH-N-IY- -T-EH-L-AH-G-R-AE-F- -P-OW-L-Z- -JH-ER-M-AH-N-IY",
    "OW-Z- -T-UW- -IH-T-S- -W-AO-R- -K-R-EH-D-AH-T-ER-Z",
    "T-EH-L-AH-G-R-AE-F- -P-OW-L-Z",
    "W-AH-T- -AH- -JH-OW-K-",
    "EH-V-R-IY-TH-IH-NG- -W-IY- -L-AH-V",
    "EH-V-R-IY-TH-IH-NG- -W-IY- -F-AY-T- -F-AO-R",
    "EH-V-R-IY-TH-IH-NG- -IH-Z- -D-UW-M-D",
    "W-EH-L",
    "D-OW-N-T- -Y-UW- -S-IY- -DH-AH- -F-AH-N-IY- -S-AY-D- -AH-V- -DH-AH- -S-IH-CH-UW-EY-SH-AH-N- -Y-EH-T"
    ]

is_prob_not = False
is_prob_partial = False
is_prob_full = True
is_block_prob_not = True
is_block = True

speech = vm.init_speech(f'test_media/norm.wav', options=options)

state_ai["respiratory"]["time_inhale"] = inhale_volume_to_time_new(state_ai["respiratory"]["lung_volumes"] + volume_full_inhale)
state_ai["respiratory"]["air_speed_inhale"] = volume_full_inhale / state_ai["respiratory"]["time_inhale"]

index = 1
index_sentence = 1
index_phoneme = 1
is_next = True
while index_sentence <= len(breath_sentences):
    sentence = breath_sentences[index_sentence - 1]
    if is_next and sentence[0] == '[':
        type_ = sentence[7:8]
        index = index + 1
        index_sentence = index_sentence + 1
        continue

    print(index, index_sentence, sentence)

    is_block_prob_not = sentence[-1] == '?' or is_block
    is_block = sentence[-1] == '?'
    if not is_prob_not:
        state_ai = calc_metabolism(state_ai, state_ai["respiratory"]["time_respiratory"])
        state_ai = calc_arterial_pressure(state_ai, state_ai["respiratory"]["time_respiratory"])
        state_ai = calc_heart_rate(state_ai,state_ai["respiratory"]["time_respiratory"])

    print(f'lung_volumes {lung_volumes} oxygen {oxygen} {is_prob_partial} {is_prob_full}')

    type_inh, lung_volumes, oxygen, time_inhale, time_pause = inhale(lung_volumes, oxygen, stress, air_speed_inhale,
                                                                      is_prob_partial, is_prob_full)
    is_prob_not = time_pause > 0

    time_inhale = time_inhale / stress
    time_exhale = time_inhale * 1.3

    print(f'first heart_rate: {heart_rate:.2f}, respiratory_rate: {respiratory_rate:.2f}')

    sentences.append(f'pause_i_{int(time_inhale * 1000)}')

    num_phonemes = get_count_phoneme(phonemes[index_phoneme-1])
    stress_phoneme = 1./math.log(num_phonemes)
    phoneme_max = 18
    time_phoneme_max = min(7.0 / num_phonemes, 0.8)
    time_phoneme_min = 0.09 + (0.11 - 0.09) / num_phonemes
    time_phoneme = calc_time_phoneme(num_phonemes)
    time_phoneme = time_phoneme / stress
    time_phoneme = min(time_phoneme, time_phoneme_max)
    time_phoneme = max(time_phoneme, time_phoneme_min)
    speech_time = time_phoneme * num_phonemes

    sound = pm.Sound(f'test_media/{index_phoneme}.wav')
    fs = sound.sampling_frequency
    time_step = hop_length / fs
    pitch = sound.to_pitch(time_step=time_step)
    f0 = np.array([p[0] for p in pitch.selected_array])
    compare_mask = f0 > 150
    f0_avg = np.mean(f0[compare_mask])
    f0_max_avg = f0.max()
    f0_min_avg = f0.min()

    sound = AudioSegment.from_file(f'test_media/{index_phoneme}.wav')
    # print("sound.duration_seconds origin", sound.duration_seconds)
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)
    sound = sound[start_trim:duration-end_trim]
    sound.export(f'test_new/{index_phoneme}p.wav', format="wav")

    # print("sound.duration_seconds cut silent", sound.duration_seconds)
    # print("sound.duration_seconds cut silent", duration)
    ratio = speech_time*1000 / duration
    #ratio = min(max(ratio, 0.8), 3)
    print("speed", ratio, "speech_time", speech_time, "num_phonemes", num_phonemes)
    # print("impact_heart", impact_heart, "impact_respiratory", impact_respiratory)
    sound = set_speed(sound, ratio)

    hr_k = (heart_rate - heart_rate_norm) / (heart_rate_max - heart_rate_norm)
    rr_k = (respiratory_rate - respiratory_rate_norm) / (respiratory_rate_max - respiratory_rate_norm)
    f0_norm = 180
    f0_max = 300
    f0_min = 50
    f0 = f0_norm + (f0_max - f0_norm) * rr_k
    # print('f0_avg =', f0_avg)
    # print('f0 =', f0)

    # print("sound.duration_seconds finish", sound.duration_seconds)
    if heart_rate > heart_rate_norm:
        # sound = sound + 5*(math.log(heart_rate - heart_rate_norm+1) / math.log(heart_rate_max - heart_rate_norm))
        sound = sound + math.exp(1.8 * (heart_rate - heart_rate_norm) / (heart_rate_max - heart_rate_norm)) - 1
    elif heart_rate < heart_rate_norm:
        # sound = sound - 5*(math.log(heart_rate_norm - heart_rate+1) / math.log(heart_rate_norm - heart_rate_min))
        sound = sound - math.exp(1.8 * (heart_rate_norm - heart_rate) / (heart_rate_norm - heart_rate_min)) - 1
    sound.export(f'test_new/{index_phoneme}.wav', format="wav")
    speech_time = sound.duration_seconds

    if not is_prob_not:
        oxygen_speech = oxygen_full_inhale * speech_time / time_exhale
    t0 = inhale_volume_to_time_new(max(lung_volumes - volume_reserve_lungs, 0)) * 1.3 / stress

    # не хватает кислорода для речи
    if speech_time > t0:
    # if oxygen_speech > oxygen:
        # не говорим речь, а делаем вдох
        type_ = 'm'
        is_prob_partial = True
        is_prob_full = False
        is_prob_not = False
        is_next = False
        index = index + 1
        add_time_inhale = add_time_inhale + time_inhale
        continue

    sd = f0/f0_norm
    if fn == 0:
        fn = f0_avg
    sentences.append(f'speech_{int(speech_time * 1000)}_{stress:.3f}')
    sentences.append(sentence)

    delta_lung_volumes = lung_volumes
    lung_volumes, oxygen, time_exhale, is_prob_not, is_prob_partial, is_prob_full = exhale(
        lung_volumes, oxygen, speech_time * stress, is_block_prob_not, type_
    )

    # инициализация скорости воздушного потока
    if air_speed_exhale == 0:
        air_speed_exhale = volume_full_inhale / max(speech_time, time_exhale)
    time_exhale = max(time_exhale/stress - speech_time, 0)

    delta_lung_volumes -= lung_volumes
    cur_speech = vm.speech_params(f'test_new/{index_phoneme}.wav', speech)

    f0_norm = speech["params"]["norm"]["f0"]["freq"]
    emotion = rr_k

    air_speed_exhale_old = air_speed_exhale
    # расчитываем объем воздуха для речи
    speech_lung_volumes = air_speed_exhale * speech_time

    if speech_lung_volumes < delta_lung_volumes:
        pause_lung_volumes = delta_lung_volumes - speech_lung_volumes
        air_speed_exhale = pause_lung_volumes / time_exhale
    elif speech_lung_volumes > delta_lung_volumes:
        air_speed_exhale = delta_lung_volumes / speech_time
    air_speed_exhale = min(air_speed, 1.0)
    air_speed_exhale = max(air_speed, 0.1)

    k_air = air_speed_exhale_old / air_speed_exhale
    air_speed_inhale = air_speed_inhale / k_air
    
    stress_fast = impact_heart
    stress_slow = 0
    spl = vc.calculate_spl(height, sex, f0, air_speed, speech_time, stress_fast, stress_slow)

    intensity_avg = spl - 50
    
    if intensity_avg > intensity_norm_avg:
        volume = (intensity_avg - intensity_norm_avg) / (100 - intensity_norm_avg)
    elif intensity_avg < intensity_norm_avg:
        volume = (intensity_avg - intensity_norm_avg) / (intensity_norm_avg - (-50.0))
    else:
        volume = 0.0

    y_new, sr_new = vm.change_speech(speech, cur_speech, volume=volume, emotion=emotion)
    sf.write(f'test_new/{index_phoneme}.wav', y_new, sr_new)
    sound = AudioSegment.from_file(f'test_new/{index_phoneme}.wav')

    print(f"time_inhale {time_inhale:.2f}, time_exhale {time_exhale:.2f}")
    sentences.append(f'pause_e_{int(time_exhale*1000)}')

    if time_pause > 0:
        if audio:
            audio = audio + AudioSegment.silent(duration=int(time_pause * 1000))
        else:
            audio = AudioSegment.silent(duration=int(time_pause * 1000))

    if time_inhale > 0:
        time_inhale = time_inhale + add_time_inhale
        if audio:
            audio = audio + AudioSegment.silent(duration=int(time_inhale * 1000))
        else:
            audio = AudioSegment.silent(duration=int(time_inhale * 1000))

    audio = audio + sound
    if time_exhale > 0:
        sound = sound + AudioSegment.silent(duration=int(time_exhale * 1000))

    if is_prob_not:
        time_speech_time = time_respiratory + time_pause + speech_time
    else:
        time_respiratory = time_inhale + time_pause + speech_time + time_exhale
        time_breaths.append({'begin_time': int(cur_time * 1000), 'duration': int(time_respiratory * 1000)})
        cur_time = cur_time + time_respiratory

        respiratory_rate_avg, time_breaths = count_respiratory_rate(cur_time * 1000, time_breaths)
        # respiratory_rate_avg = respiratory_rate

        respiratory_rate, impact_respiratory, impact_heart = calc_respiratory_rate(respiratory_rate_avg,
                                                                                   respiratory_rate,
                                                                                   respiratory_rate_max,
                                                                                   respiratory_rate_min,
                                                                                   respiratory_rate_norm,
                                                                                   impact_respiratory, impact_heart,
                                                                                   time_respiratory)
        print(
            f'last heart_rate: {heart_rate:.2f}, respiratory_rate: {respiratory_rate:.2f}, current index_q: {heart_rate / respiratory_rate:.2f}')
        time_speech_time = 0

    is_next = True
    index = index + 1
    index_sentence = index_sentence + 1
    index_phoneme = index_phoneme + 1
    time_inhale = 0
    time_pause = 0
    speech_time = 0
    time_exhale = 0
    add_time_inhale = 0

audio.export(f'test_new/out.wav', format="wav")


print(sentences)

