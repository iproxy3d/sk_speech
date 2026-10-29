from scipy.integrate import quad
import numpy as np
import math

# Примерное значение для трахеи
friction_factor_trachea = 0.02

# Примерное значение для бронхов
friction_factor_bronchi = 0.025
friction_factor_bronchioles = 0.03

def calculate_base_S0(Base0, height, height_gender):
    return Base0 * (1 + (height - height_gender) / height_gender)

def calculate_min_S_fast(Base_min, height, height_gender, factor_fast):
    return Base_min * (1 + (height - height_gender) / height_gender) * factor_fast

def calculate_min_S_slow(Base_min, height, height_gender, factor_slow):
    return Base_min * (1 + (height - height_gender) / height_gender) * factor_slow

def get_S(gender=None, height=None):
    # Определяем базовые параметры
    Base0_men = 0.000035  # м² (среднее значение для мужчин)
    Base_min_men = 0.00002  # м² (среднее значение для мужчин)
    Base0_women = 0.000030  # м² (среднее значение для женщин)
    Base_min_women = 0.00001  # м² (среднее значение для женщин)
    
    height_gender_men = 180  # Средний рост мужчин в см
    height_gender_women = 170  # Средний рост женщин в см
    
    factor_fast_men = 0.9  # Коэффициент для быстрой реакции у мужчин
    factor_slow_men = 1.1  # Коэффициент для медленной реакции у мужчин
    factor_fast_women = 0.85  # Коэффициент для быстрой реакции у женщин
    factor_slow_women = 1.05  # Коэффициент для медленной реакции у женщин

    if gender == 'male':
        Base0 = Base0_men
        Base_min = Base_min_men
        height_gender = height_gender_men
        factor_fast = factor_fast_men
        factor_slow = factor_slow_men
    elif gender == 'female':
        Base0 = Base0_women
        Base_min = Base_min_women
        height_gender = height_gender_women
        factor_fast = factor_fast_women
        factor_slow = factor_slow_women
    else:
        raise ValueError("Gender must be 'male' or 'female'")

    if height is None:
        height = height_gender

    # Расчет базовой площади голосовой щели (S0)
    S0 = calculate_base_S0(Base0, height, height_gender)

    # Расчет минимальной площади голосовой щели для быстрой и медленной реакции
    S_min_fast = calculate_min_S_fast(Base_min, height, height_gender, factor_fast)
    S_min_slow = calculate_min_S_slow(Base_min, height, height_gender, factor_slow)

    return S0, S_min_fast, S_min_slow

def fS_t1(t, T0, alpha):
    return np.sin(1.5 * np.pi * t / T0)**alpha

def fS_t2(t, T0, beta):
    return np.cos(0.5 * np.pi * (3.0 * t - T0) / T0)**beta

# alpha, beta эти параметры регулируют с какой скоростью голосовая щель открывается и закрывается
# S_max — максимальная площадь открытия голосовой щели
# 𝑇0 — период основного тона (длительность одного цикла вибрации)
def calculate_dynamic_area(S_max, T0, alpha, beta):
    t1 = T0 / 3.0
    t2 = T0 * 2.0 / 3.0
    S1, _ = quad(lambda t: fS_t1(t, T0, alpha), 0.0, t1) # раскрытие голосовой щели
    S2, _ = quad(lambda t: fS_t2(t, T0, beta), t1, t2) # закрытие голосовой щели    S3 = 0  # когда голосовая щель закрыта
    S3 = 0  # когда голосовая щель закрыта
    S_avg = S_max*(S1 + S2 + S3) / T0
    return S_avg

def calculate_S(T0, S0, Stress_fast, Stress_slow, alpha, beta, w, S_min_fast, S_min_slow):
    """
    Рассчитывает площадь голосовой щели с учетом быстрого и медленного стресса, с корректировками для более мягкого изменения.

    :param S0: Базовая площадь голосовой щели при спокойной речи (м²)
    :param Stress_fast: Значение стресса для быстрой реакции (от 0 до 1)
    :param Stress_slow: Значение стресса для медленной реакции (от 0 до 1)
    :param alpha: Коэффициент для экспоненциальной функции для медленного стресса
    :param beta: Пороговое значение стресса для медленного стресса
    :param w: Весовой коэффициент для перехода между быстрым и медленным стрессом
    :param S_min_fast: Минимальная площадь голосовой щели при быстром стрессе (м²)
    :param S_min_slow: Минимальная площадь голосовой щели при медленном стрессе (м²)
    :return: Площадь голосовой щели (м²)
    """
    # a и b эти параметры регулируют с какой скоростью голосовая щель открывается и закрывается
    a = 1.0 - 0.5 * Stress_fast + 1.5 * Stress_slow
    b = 1.0 + 3.0 * Stress_slow - 1.0 * Stress_fast
    S0 = calculate_dynamic_area(S0, T0, a, b)
    
    # Корректируем влияние медленного стресса
    st_slow = 1 / (1 + np.exp(-alpha * (Stress_slow - beta)))

    # Расчет площади голосовой щели для медленного стресса
    S_slow = S0 * (1 - st_slow) + S_min_slow * st_slow

    # Уменьшим влияние быстрого стресса на уменьшение площади голосовой щели
    # Скорректируем формулу для быстрого стресса
    S_fast = S0 * (1 - Stress_fast * 0.8) + S_min_fast * Stress_fast * 0.8

    # Итоговая площадь голосовой щели
    S = S_fast * (1 - w) + S_slow * w

    return S

def calculate_diameter(height, sex):
    """
    Рассчитывает диаметр дыхательных путей на основе роста и пола.
    
    :param height: Рост человека (см)
    :param sex: Пол человека ('male' или 'female')
    :return: Диаметр дыхательных путей (м)
    """
    # https://en.wikipedia.org/wiki/Trachea
    # An adult's trachea has an inner diameter of about 1.5 to 2 centimetres
    # and a length of about 10 to 11 cm, wider in males than females
    if sex == 'male':
        base_diameter = 0.0175  # Средний диаметр трахеи для мужчин (м)
        growth_factor = 0.0001  # Фактор роста для мужчин (м/см)
    else:
        base_diameter = 0.015  # Средний диаметр трахеи для женщин (м)
        growth_factor = 0.00008  # Фактор роста для женщин (м/см)
        
    return base_diameter + growth_factor * (height - 170) / 100  # 170 см - средний рост

def calculate_length(height):
    """
    Рассчитывает длину дыхательных путей на основе роста.
    
    :param height: Рост человека (см)
    :return: Длина дыхательных путей (м)
    """
    # https://www.scielo.cl/pdf/ijmorphol/v34n1/art33.pdf
    # The 2008 edition of Gray's Anatomy states that the trachea is 10–11 cm long....
    base_length = 0.11  # Средняя длина трахеи (м)
    growth_factor = 0.0002  # Фактор роста для длины (м/см)
    
    return base_length + growth_factor * (height - 170) / 100  # 170 см - средний рост

def hagen_poiseuille_resistance(length, radius, viscosity=1.8e-5):
    """
    Рассчитывает сопротивление по формуле Хагена-Пуазейля для ламинарного потока.

    :param viscosity: Вязкость воздуха (Па·с)
    :param length: Длина трубы (м)
    :param radius: Радиус трубы (м)
    :return: Сопротивление (Па·с/м³)
    """
    resistance = (8 * viscosity * length) / (math.pi * radius**4)
    return resistance

def darcy_weisbach_resistance(friction_factor, length, diameter):
    """
    Рассчитывает сопротивление по формуле Дарси-Уэйсбаха для турбулентного потока.

    :param friction_factor: Коэффициент трения
    :param length: Длина трубы (м)
    :param diameter: Диаметр трубы (м)
    :return: Сопротивление (Па·с/м³)
    """
    resistance = (friction_factor * length) / diameter
    return resistance

def reynolds_number(flow_rate, diameter, viscosity=1.81e-5, rho=1.225):
    """
    Рассчитывает число Рейнольдса для оценки типа потока.

    :param flow_rate: Скорость потока (м³/с)
    :param diameter: Диаметр трубы (м)
    :param viscosity: Вязкость воздуха (Па·с) ~ 1.81e-5
    :param density: Плотность воздуха (кг/м³)
    :return: Число Рейнольдса
    """
    # Площадь поперечного сечения
    area = math.pi * (diameter / 2)**2
    
    # Средняя скорость
    velocity = flow_rate / area
    
    # Число Рейнольдса
    re_number = (rho * velocity * diameter) / viscosity
    return re_number

# Функция для расчета скорости воздушного потока
def calculate_flow(V, T, S):
    return V / (T * S)

def calculate_subglottic_pressure(flow_rate, rho=1.225):
    """
    Рассчитывает субглотическое давление на основе скорости воздушного потока.

    :param flow_rate: Скорость воздушного потока (м/с)
    :param resistance: Общее сопротивление (Па·с/м³)
    :param rho: Плотность воздуха (кг/м³)    
    :return: Субглотическое давление (Па)
    """
    # Давление в области голосовой щели
    P_sub = 0.5 * rho * (flow_rate ** 2)
    return P_sub

def calculate_spl(height, sex, F0, volume_air, time_speech, Stress_fast, Stress_slow):
    # Параметры человека
    # height см
    # sex male/famale пол
    # F0 частота тона Гц
    # volume_air объем воздуха (л)
    # time_speech время речи в секундах
    # Stress_fast Значение стресса для быстрой реакции
    # Stress_slow Значение стресса для медленной реакции

    global friction_factor_trachea
    global friction_factor_bronchi
    global friction_factor_bronchioles

    # Расчет диаметров и длин
    trachea_diameter = calculate_diameter(height, sex)
    bronchi_diameter = trachea_diameter * 0.8
    bronchioles_diameter = bronchi_diameter * 0.05

    trachea_radius = trachea_diameter / 2
    bronchi_radius = bronchi_diameter / 2
    bronchioles_radius = bronchioles_diameter / 2

    trachea_length = calculate_length(height)
    bronchi_length = trachea_length * 0.4
    bronchioles_length = bronchi_length * 0.2

    # период основного тона (длительность одного цикла вибрации).
    T0 = 1.0 / F0 # частотоа тона F0 в Гц, T0 в секундах

    V = volume_air * 0.001 # м3

    S0, S_min_fast, S_min_slow = get_S(gender=sex, height=height)

    alpha = 8  # Коэффициент для экспоненциальной функции
    beta = 0.1  # Пороговое значение стресса
    w = 0.1  # Весовой коэффициент

    # Расчет площади голосовой щели
    S = calculate_S(T0, S0, Stress_fast, Stress_slow, alpha, beta, w, S_min_fast, S_min_slow)

    # Рассчитаем скорость потока воздуха для спокойной речи и стресса
    flow = calculate_flow(V, time_speech, S)

    re_number = reynolds_number(flow, trachea_diameter)
    # Определение типа потока
    if re_number < 2000:
        # Расчет сопротивления
        trachea_resistance = hagen_poiseuille_resistance(trachea_length, trachea_radius)
    else:
        # Расчет сопротивления
        trachea_resistance = darcy_weisbach_resistance(friction_factor_trachea, trachea_length, trachea_diameter)

    re_number = reynolds_number(flow, bronchi_diameter)
    # Определение типа потока
    if re_number < 2000:
        # Расчет сопротивления
        bronchi_resistance = hagen_poiseuille_resistance(bronchi_length, bronchi_radius)
    else:
        # Расчет сопротивления
        bronchi_resistance = darcy_weisbach_resistance(friction_factor_bronchi, bronchi_length, bronchi_diameter)

    re_number = reynolds_number(flow, bronchioles_diameter)
    # Определение типа потока
    if re_number < 2000:
        # Расчет сопротивления
        bronchioles_resistance = hagen_poiseuille_resistance(bronchioles_length, bronchioles_radius)
    else:
        # Расчет сопротивления
        bronchioles_resistance = darcy_weisbach_resistance(friction_factor_bronchioles, bronchioles_length, bronchioles_diameter)

    # Общее сопротивление
    total_resistance = trachea_resistance + bronchi_resistance + bronchioles_resistance

    # Расчет субглотического давления
    P_sub = calculate_subglottic_pressure(flow)
    P_sub = P_sub * total_resistance
    P_sub = P_sub * 0.001

    SPL = 20 * math.log10(P_sub/0.00002)

    return SPL

if __name__ == '__main__':
    spl = calculate_spl(175, 'male', 120, 0.5, 2.0, 0.3, 0.3)
    print(spl)
