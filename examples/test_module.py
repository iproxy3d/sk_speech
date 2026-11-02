import random
import math
#import soundfile as sf
from numpy.polynomial import Polynomial
# подключим пакет интегрирования из библиотеки scipy
from scipy import integrate
from pydub import AudioSegment
from pydub.effects import speedup

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
# (1500*3/(4*Pi))^(1/3) = 7.10124042307
# (2000*3/(4*Pi))^(1/3) = 7.81592641797
# (7.81592641797 - 7.10124042307) * r_t = 2.5
# r_t = alveolar_t_max / (((volume_reserve_lungs + volume_full_inhale)*3./(4.*math.pi))**(1./3.) - ((volume_reserve_lungs)*3./(4.*math.pi))**(1./3.))

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

# time to pronounce a syllable
emotion_time_syl = {
    "disappointment": 0.34,
    "sadness": 0.31,
    "annoyance": 0.31,
    "neutral": 0.32,
    "disapproval": 0.32,
    "realization": 0.34,
    "nervousness": 0.32,
    "approval": 0.31,
    "joy": 0.35,
    "anger": 0.33,
    "embarrassment": 0.305,
    "caring": 0.32,
    "remorse": 0.34,
    "disgust": 0.31,
    "grief": 0.30,
    "confusion": 0.30,
    "relief": 0.335,
    "desire": 0.32,
    "admiration": 0.34,
    "optimism": 0.34,
    "fear": 0.32,
    "love": 0.34,
    "excitement": 0.31,
    "curiosity": 0.36,
    "amusement": 0.34,
    "surprise": 0.34,
    "gratitude": 0.34,
    "pride": 0.36,
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

def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    # convert the sound with altered frame rate to a standard frame rate
    # so that regular playback programs will work right. They often only
    # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

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

# время в радиус альвеолы (сколько времени чтобы надуть альвеолу)
def time_to_radius(t):
    return t*r_t

# опишем подынтегральную функцию объема легких от 0 до alveolar_radius
def lung_function_f(r):
    return (4. * math.pi * r ** 3) / 3.

# height - cm
# age - year
# result cm^3
def init_lugs(gender, age, height):
    global volume_full_inhale
    global volume_partial_inhale
    global oxygen_full_inhale
    global not_inhale_time
    global max_phoneme_inhale
    global oxygen_phoneme
    global oxygen_word
    global exhaling_lung_time

    # максимальный объем легких
    if gender == 'm':
        max_volume_lungs = (27.63 - 0.112 * age) * height
    elif gender == 'w':
        max_volume_lungs = (21.78 - 0.101 * age) * height
    else:
        max_volume_lungs = 3500

    # объем легких во время вдоха (ДО) - 500 см^3
    volume_full_inhale = max_volume_lungs * 0.15  # 15%
    # объем легких во время дополнительного вдоха (РОВ) - 1500 см^3
    # это сколько мы можем еще вдохнуть после полного вдоха (резервный объем вдоха и выдоха)
    volume_partial_inhale = max_volume_lungs * 0.40  # 40%
    # сколько нужно кислорода для полного вдоха
    # в полных легких мы можем получить только 6% кислорода
    oxygen_full_inhale = volume_full_inhale * 0.06

    # время паузы без вдоха
    not_inhale_time = 0.34
    # максимальное кол-во произносимых фонем на выдохе
    # Совокупно по всем языкам на земле, человек может произносить от 30 до 35 гласных фонем
    # эмпирически установил, что при обычной громкой речи можно произнести 15-20 фонем,
    # при увеличении их числа громкость речи падает
    max_phoneme_inhale = 18
    # кислород нужный для одной фонемы
    oxygen_phoneme = oxygen_full_inhale / max_phoneme_inhale
    # кислород нужный для одного слова
    # максимум можно произнести не более 8 слов
    oxygen_word = oxygen_full_inhale / 8
    # сколько времени надо на выдох 1 см3 легких
    # за 1 сек делается один вдох, один вдох это 500 см3
    # считаем время одного см3
    exhaling_lung_time = 1 / volume_full_inhale

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
    return cnt

# МЧСС
def max_heart_rate(gender, age):
    # формула Марты Гулати: МЧСС = 206 — (0,88 * возраст)
    if gender == 'w':
        m = 206 - 0.88 * age
    # Формула Танака: МЧСС = 208 — (0,7 * возраст)
    else:
        m = 208 - 0.7 * age
    return m

#  на сколько восстановится ЧСС в норму, за указанный промежуток времени
def recovery_heart_rate(delta_time):
    return delta_time * 0.1

# расчет ЧСС
def calc_heart_rate(hr_cur, hr_max, hr_min, hr_norm, impact, delta_time):
    if impact > 0:
        hr_cur = min(hr_cur + (hr_max - hr_norm) * impact, hr_max)
    else:
        hr_cur = max(hr_cur + (hr_norm - hr_min) * impact, hr_min)

    if hr_cur > hr_norm:
        hr_cur = hr_cur - recovery_heart_rate(delta_time)
    else:
        hr_cur = hr_cur + recovery_heart_rate(delta_time)

    return hr_cur


def  average_respiratory_rate(breaths):
    total = sum(breath['duration'] for breath in breaths)
    return total / len(total)

def inhole_exhole_time(respiratory_rate_time, speech_time):
    # respiratory_rate_time = inhale_time + speech_time + exhale_time
    # exhale_time = 1.3 * inhale_time
    inhale_time = (respiratory_rate_time - speech_time)
    exhale_time = 1.3 * inhale_time
    return inhale_time, exhale_time

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

        if text[len(text) - 1] in '!?':
            text = text.replace(",", text[len(text) - 1])
            text = text.replace("-", text[len(text) - 1])
        else:
            text = text.replace(",", ".")
            text = text.replace("-", ".")
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
                    sentences2[len(sentences2) - 1] = sentence
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
                        sentences2[len(sentences2) - 1] = sentences2[len(sentences2) - 1] + ' ' + s
                    else:
                        sentences2.append(s)
                        sentences2.append('[pause_p]')

            sentences = sentences2

    else:
        sentences = [text, '[pause_p]']

    sentences.insert(0, '[pause_p]')
    return sentences

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


# сколько воздуха нужно на произнесение текста
def text_to_oxygen(text, em_name, em_score):
    global oxygen_phoneme

    phoneme_count = number_of_syllables(text)
    oxygen = phoneme_count * oxygen_phoneme

    stress = (1 + em_score)
    oxygen = oxygen * stress

    return oxygen


# сколько воздуха нужно на произнесение слов
def get_oxygen_by_word(word_count, em_name, em_score):
    global oxygen_word

    oxygen = oxygen_word * word_count

    stress = (1 + em_score)
    oxygen = oxygen * stress

    return oxygen

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
    t = 2.1*math.exp(r / k) - 1
    return t

def inhale_time_to_volume(t):
    global r_t
    r = t_to_r(t)

    v = (4. * math.pi * r ** 3) / 3.
    return v

def inhale_volume_to_time(volume, em_name, em_score):
    global r_t
    r = (volume * 3. / (4 * math.pi)) ** (1./3.)
    t = r_to_t(r)

    stress = (1 + em_score)

    t = t / stress
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
        is_prob_not = prob_val < prob_partial
        is_prob_full = not is_prob_not
    else:
        prob = prob_full + prob_partial + prob_not
        prob_val = random.uniform(0, prob)

        is_prob_not = (prob_val >= 0) and (prob_val < prob_not)
        is_prob_partial = (prob_val >= prob_partial) and (prob_val <= prob - prob_full)
        is_prob_full = (prob_val > prob - prob_full) and (prob_val <= prob)

    return is_prob_not, is_prob_partial, is_prob_full


# расчет вдоха
def inhale(lung_volumes, oxygen, oxygen_need, em_name, em_score, type_, prob_full, prob_partial, prob_not):
    global oxygen_full_inhale
    global volume_full_inhale
    global exhaling_lung_time
    global not_inhale_time
    global max_volume_lungs

    is_prob_not, is_prob_partial, is_prob_full = prob_inhale(prob_full, prob_partial, prob_not)

    volume_need = abs(lung_volumes) + oxygen_need / 0.06

    # выдыхаем и делаем вдох на нужное кол-во воздуха
    if oxygen < 0.3 or lung_volumes < volume_reserve_lungs or ((is_prob_full or volume_need > max_volume_lungs or (
            type_ == 'p' and lung_volumes > max_volume_lungs / 2)) and (type_ == 'p')):
        type_inh = 'f'

        if lung_volumes < volume_reserve_lungs:
            # время вдоха текущего объема легких + время обычного вдоха
            t = inhale_volume_to_time(volume_reserve_lungs + volume_full_inhale, em_name, em_score)
            t = t - inhale_volume_to_time(lung_volumes, em_name, em_score)
        else:
            # t_exhale_left - сколько времени надо, чтобы выдохнуть весь объем легких
            t_exhale_left = (lung_volumes - volume_reserve_lungs) * exhaling_lung_time
            # время выдоха остатка + время обычного вдоха
            t = inhale_volume_to_time(volume_reserve_lungs + volume_full_inhale, em_name, em_score)
            t = t - inhale_volume_to_time(volume_reserve_lungs, em_name, em_score)
            t = t + t_exhale_left

        oxygen = oxygen_full_inhale
        lung_volumes = volume_reserve_lungs + volume_full_inhale
    # если кислорода меньше, чем нужно для произнесения речи
    elif oxygen < oxygen_need or is_prob_partial:
        # дополнительно вдыхаем
        type_inh = 'p'
        if oxygen < oxygen_need:
          oxygen_need = oxygen_need - oxygen
        volume_need = oxygen_need / 0.06
        # время нужное, чтобы дополнительно вдохнуть данный объем
        # так как время вдоха легких не линейное, то рассчитываем разницу времени вдоха текущего объема и нового
        t = (inhale_volume_to_time(lung_volumes + volume_need, em_name, em_score) -
             inhale_volume_to_time(lung_volumes, em_name, em_score))
        lung_volumes = lung_volumes + volume_need
        oxygen = oxygen + oxygen_need
    else:
        # вздоха делать не нужно, пауза это время двух фонем
        type_inh = 'n'
        t = not_inhale_time

    return int(t * 1000), type_inh, lung_volumes, oxygen


# lung_volumes - объем легких
# oxygen - запас кислорода
def oxygen_time_pause(lung_volumes, oxygen, em_name, em_score, text, type_):
    # кол-во слов
    word_count = count_words(text)

    # сколько надо кислорода для произнесения текста
    oxygen_need = get_oxygen_by_word(word_count, em_name, em_score)

    stress = 1 + em_score

    # f - полный вздох (full), p - дополнительный вдох (partial), n - без вдоха (not)
    # если конец предложения, то делаем до конца выдох и полный вдох
    if type_ == 'p' or oxygen < 0.1:
        prob_not = 25 * stress
        prob_partial = 25 * stress
        prob_full = 100 - (prob_partial + prob_not)
    # если это знак препинания, то можно сделать дополнительный вдох
    elif type_ == 'm':
        prob_full = 25 * stress
        prob_not = 25 * stress
        prob_partial = 100 - (prob_full + prob_not)
    # если это внутри предложения, то стараемся все делать без вдоха
    else:
        prob_not = 50 * stress
        prob_partial = 25 * stress
        prob_full = max(100 - (prob_partial + prob_not), 0)

    p_t, type_inh, lung_volumes, oxygen = inhale(lung_volumes, oxygen, oxygen_need, em_name, em_score, type_,
                                                 prob_full, prob_partial, prob_not)
    res = f'[pause_{type_}_{type_inh}_{p_t}_{em_name}_{em_score}]'

    return res, lung_volumes, oxygen


# вызываем после произнесения речи, чтобы рассчитать реальный расход кислорода
def change_lungs(text, speech_time, em_name, em_score, lung_volumes, oxygen):
    global emotion_time_syl

    # уровень стресса
    stress = (1 + em_score)

    # кол-во фонем в тексте
    phoneme_count = number_of_syllables(text)

    # расчетное время произнесения текста
    speech_time_cal = phoneme_count * emotion_time_syl[em_name] * stress

    # сколько реально израсходовали кислорода
    oxygen_need = oxygen_phoneme * phoneme_count * speech_time / speech_time_cal

    oxygen = oxygen - oxygen_need

    volume = oxygen_need / 0.06
    lung_volumes = lung_volumes - volume

    return lung_volumes, oxygen


def fill_tag_pause(oxygen, t_left, em_name, em_score, sentences):
    l = len(sentences)
    for idx, sentence in enumerate(sentences):
        if sentence in ('[pause_p]', '[pause_m]', '[pause_n]'):
            if idx + 1 < l:
                sentences[idx], t_left, oxygen = time_pause(oxygen, t_left, em_name, em_score,
                                                            count_words(sentences[idx + 1]), sentence[7:8])
                oxygen = max(oxygen - number_of_syllables(sentences[idx + 1]) * 0.34, 0)
    sentences.pop(l - 1)
    return sentences, oxygen, t_left


def get_pause_time(text):
    params = text[1:-1].split('_')
    silent_time = float(params[3])
    em_name = params[4]
    em_score = float(params[5])
    return silent_time

def oxygen_time(time_inhale, lung_volumes, oxygen, mul_resp_rate, type_):
    if lung_volumes < volume_reserve_lungs:
        t = inhale_volume_to_time_new(volume_reserve_lungs)
        v2 = inhale_time_to_volume_new(t + time_inhale)
        v1 = volume_reserve_lungs - lung_volumes + v2
        k_rate = v1 / v2
        oxygen_oxygen = (volume_reserve_lungs - lung_volumes) * 0.06
        lung_volumes = volume_reserve_lungs
    else:
        k_rate = 1.0
        oxygen_oxygen = 0

    volume_time = inhale_volume_to_time_new(lung_volumes)
    time_inhale = time_inhale * mul_resp_rate

    d_vol = inhale_time_to_volume_new(volume_time + time_inhale)
    d_vol = d_vol - inhale_time_to_volume_new(volume_time)
    oxygen_inhale = d_vol * 0.06
    oxygen = oxygen + oxygen_inhale + oxygen_oxygen
    lung_volumes = lung_volumes + d_vol

    return lung_volumes, oxygen, oxygen_inhale, k_rate

def exhale(lung_volumes, oxygen, oxygen_inhale, speech_time, time_exhale, type_):
    # oxygen_exhale = oxygen_inhale * speech_time / time_exhale
    oxygen_exhale = oxygen_inhale
    oxygen = oxygen - oxygen_exhale
    volume = oxygen_exhale / 0.06
    lung_volumes = lung_volumes - volume

    # если конец предложения, то делаем до конца выдох
    if (type_ == 'p' or lung_volumes > max_volume_lungs - volume_full_inhale) and lung_volumes > volume_reserve_lungs:
        time_exhale = inhale_volume_to_time_new(lung_volumes) - inhale_volume_to_time_new(volume_reserve_lungs)
    else:
        time_exhale = max(time_exhale - speech_time, 0)

    return lung_volumes, oxygen, time_exhale


em_score = 0

# sentences = "Do you know how many times we??"
# sentences = "I admit it!!!!"
# sentences = "Do you know what caused the last world"
# sentences = "длинный текст русских слов имеющих корни фамилии"
# sentences = "The dispute is about how many telegraph poles"
# sentences = "of World War III because of a bunch of geese"
# sentences = "Do you know how many times we were on the verge"
sentences = "of World War III because of a bunch of geese on a computer"
res = number_of_syllables(sentences)
print(res)

# text = "Everything we love, everything we fight for - everything is doomed!"
# text = "Do you know what caused the last world war?"
# text = ("Do you know how many times we were on the verge of World War III because of a bunch of geese on a computer "
#         "screen?")
text = ("Yes, I'm crazy. When I realized that the whole world was a terrible black joke, I went crazy! I admit it!... "
        "You are not a fool, you must feel the situation. Do you know how many times we were on the verge of "
        "World War III because of a bunch of geese on a computer screen? Do you know what caused the last world war? "
        "The dispute is about how many telegraph poles Germany owes to its war creditors! Telegraph poles! What a "
        "joke! Everything we love, everything we fight for - everything is doomed! Well, don't you see the funny side "
        "of the situation yet?")
sentences = adaptation_break("nervousness", em_score, text, 3, 4, 'en')
print(sentences)
breath_sentences = sentences

oxygen = 0
t_left = 0
sentences, oxygen, t_left = fill_tag_pause(oxygen, t_left, "nervousness", em_score, sentences)
print(sentences)

print(get_pause_time(sentences[0]))

text = "When I realized that the whole world was a terrible black joke?"
lung_volumes = volume_reserve_lungs
oxygen = 0
type_ = 'p'

for sentence in sentences:
    if sentence[0] == '[':
        type_ = sentence[7:8]
        continue
    print(sentence)
    res, lung_volumes, oxygen = oxygen_time_pause(lung_volumes, oxygen, "nervousness", em_score, sentence, type_)
    print(res)
    print("before lung_volumes, oxygen: ", lung_volumes, oxygen)
    speech_time = max(number_of_syllables(sentence) * 0.34 + 0.1 * random.randint(-10, 10), 1)  # sec
    print("speech_time: ", speech_time)
    lung_volumes, oxygen = change_lungs(sentence, speech_time, "nervousness", em_score, lung_volumes, oxygen)
    print("after lung_volumes, oxygen: ", lung_volumes, oxygen)
    print("----")

# выполним интегрирование
print("alveolar_radius: ", alveolar_radius)

print(inhale_time_to_volume(alveolar_t_max))
print(inhale_volume_to_time(3500, '', em_score))
t1 = inhale_volume_to_time(2000, '', em_score)
t2 = inhale_volume_to_time(1500, '', em_score)
print(t1-t2)


# Норма 60 до 100 ударов в минуту
heart_rate_norm = 72
# Норма от 12 до 20 вдохов в минуту
respiratory_rate_norm = 16
# Норма Q – 2.9–4.8.
index_q = IndexQ(heart_rate_norm, respiratory_rate_norm)

heart_rate = heart_rate_norm
heart_rate_max = max_heart_rate('m', 35)
heart_rate_min = 40

respiratory_rate = respiratory_rate_norm
respiratory_rate_max = heart_rate_max / index_q
respiratory_rate_min = heart_rate_min / index_q

impact = 0.0
oxygen = 0
lung_volumes = volume_reserve_lungs

time_breaths = []
cur_time = 0
time_respiratory = 60. / respiratory_rate
for i in range(respiratory_rate):
    time_breaths.append({'begin_time': int(cur_time * 1000), 'duration': int(time_respiratory * 1000)})
    cur_time = cur_time + time_respiratory

sentences = []
time_respiratory = 0
mul_resp_rate = respiratory_rate / respiratory_rate_norm

index = 1
audio = None
for sentence in breath_sentences:
    if sentence[0] == '[':
        type_ = sentence[7:8]
        continue

    print(index, sentence)

    heart_rate = calc_heart_rate(heart_rate, heart_rate_max, heart_rate_min, heart_rate_norm, impact, time_respiratory)
    respiratory_rate = heart_rate / index_q
    time_breath = 60. / respiratory_rate
    time_inhale = time_breath / 2.3
    time_exhale = 1.3 * time_inhale
    mul_resp_rate = respiratory_rate / respiratory_rate_norm

    sentences.append(f'pause_i_{int(time_inhale * 1000)}')

    lung_volumes, oxygen, oxygen_inhale, k_rate = oxygen_time(time_inhale, lung_volumes, oxygen, mul_resp_rate, type_)
    # speech_time = max(number_of_syllables(sentence) * 0.34 + 0.1 * random.randint(-10, 10), 1)  # sec
    #with sf.SoundFile(f'test_media/{index}.wav') as f:
    #    speech_time = f.frames / f.samplerate
    num_phonemes = number_of_syllables(sentence)
    ratio_hr = heart_rate/heart_rate_norm
    ratio_rr = respiratory_rate / respiratory_rate_norm    
    speech_time = num_phonemes * 0.34 * ratio_rr

    sound = AudioSegment.from_file(f'test_media/{index}.wav')
    print("sound.duration_seconds origin", sound.duration_seconds)
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)
    sound = sound[start_trim:duration-end_trim]

    print("sound.duration_seconds cut silent", sound.duration_seconds)
    speed = sound.duration_seconds / speech_time
    speed = min(max(speed, 0.8), 3)
    print("speed", speed, "speech_time", speech_time, "duration_seconds", sound.duration_seconds, "num_phonemes", num_phonemes, "time_exhale", time_exhale)
    if speed > 1.0:        
        sound = speedup(sound, playback_speed=speed)
    elif speed < 1.0:
        sound = speed_change(sound, speed)

    print("sound.duration_seconds finish", sound.duration_seconds)
    if heart_rate > heart_rate_norm:
        sound = sound + 10*((heart_rate - heart_rate_norm) / (heart_rate_max - heart_rate_norm))
    else:
        sound = sound - 10*((heart_rate_norm - heart_rate) / (heart_rate_norm - heart_rate_min))
    sound.export(f'test_new/{index}.wav', format="wav")
    speech_time = sound.duration_seconds

    # if time_exhale < speech_time:
    #     speech_time = random.uniform(time_exhale, speech_time)
    # else:
    #     speech_time = random.uniform(speech_time, time_exhale)
    sentences.append(f'speech_{int(speech_time * 1000)}_{ratio_hr:.3f}_{ratio_rr:.3f}')
    sentences.append(sentence)

    print("lung_volumes", lung_volumes)
    print("oxygen", oxygen)
    lung_volumes, oxygen, time_exhale = exhale(lung_volumes, oxygen, oxygen_inhale, speech_time, time_exhale, type_)
    print("time_inhale", time_inhale)
    print("time_exhale", time_exhale)
    print("new lung_volumes", lung_volumes)
    print("new oxygen", oxygen)
    sentences.append(f'pause_e_{int(time_exhale*1000)}')

    if audio:
        audio = audio + AudioSegment.silent(duration=int(time_inhale * 1000))
    else:
        audio = AudioSegment.silent(duration=int(time_inhale * 1000))
    audio = audio + sound
    sound = sound + AudioSegment.silent(duration=int(time_exhale * 1000))

    time_respiratory = time_inhale + speech_time + time_exhale
    time_breaths.append({'begin_time': int(cur_time * 1000), 'duration': int(time_respiratory * 1000)})
    cur_time = cur_time + time_respiratory
    respiratory_rate = count_respiratory_rate(cur_time * 1000, time_breaths) * k_rate
    heart_rate = index_q * respiratory_rate
    print(f'respiratory_rate: {respiratory_rate}, heart_rate: {heart_rate}')

    # if impact > 0:
    #     impact = 0.5
    # elif impact < 0:
    #     impact = impact + 0.1
    #impact = 0
    index = index + 1

audio.export(f'test_new/out.wav', format="wav")

#sound = AudioSegment.from_file(f'test_media/6.wav')
#start_trim = detect_leading_silence(sound)
#end_trim = detect_leading_silence(sound.reverse())

#duration = len(sound)
#sound = sound[start_trim:duration-end_trim]
#sound = speedup(sound, playback_speed=0.9)
#sound = speed_change(sound, 0.9)
#sound.export(f'test_new/6n.wav', format="wav")

print(sentences)
