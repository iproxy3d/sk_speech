import threading
import time
import queue
import numpy as np
import math
from scipy import integrate
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pygame

from . import sk_vocal_cords as vc

hormone_half_lives = {
    "adrenalin": 2.0,
    "norepinephrine": 2.5,
    "cortisol": 60.0,
    "serotonin": 10.0,
    "oxytocin": 3.0,
    "dopamine": 3.0,
    "endorphin": 5.0,
    "melatonin": 45.0,
    "acetylcholine": 3.0,
}

hormone_increment = {
    "adrenalin": 0.2,
    "norepinephrine": 1.0,
    "cortisol": 0.50,
    "serotonin": 0.1,
    "oxytocin": 0.1,
    "dopamine": 0.1,
    "endorphin": 0.1,
    "melatonin": 0.1,
    "acetylcholine": 0.1,
}

# Класс сообщения
class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content
        self.timestamp = time.time()

# Класс гормона с временем жизни
class Hormone:
    def __init__(self, name, initial_level):
        """
        Инициализация гормона.
        
        :param name: Название гормона.
        :param initial_level: Начальный уровень гормона. пг/мл (пикограмм на миллилитр)
        :param half_life: Время полураспада гормона (в секундах).
        """
        global hormone_half_lives

        self.name = name
        self.level = initial_level
        self.half_life = hormone_half_lives[name]

        
    def decay(self, delta_time):
        """
        Обновление уровня гормона с учетом времени полураспада.

        Процесс распада гормона происходит по экспоненциальному закону, где гормон уменьшается
        пропорционально своему текущему уровню. Формула распада основана на постоянной полураспада.

        Экспоненциальное снижение
        Это происходит потому, что поглощение или распад гормона зависит от его текущей концентрации в крови.
        Чем больше гормона в крови, тем быстрее его будет поглощать организм, и наоборот.
        
        Формула для распада:
        уровень_гормона = начальный_уровень * (2 ** (-t / T_half))

        Где:
        - t — время, прошедшее с последнего обновления (delta_time).
        - T_half — время полураспада гормона, за которое уровень гормона уменьшается вдвое.
        - 0.693 — это натуральный логарифм 2 (ln(2)), который используется для связи времени полураспада с экспоненциальным процессом уменьшения.
        
        :param delta_time: Время, прошедшее с последнего обновления (в секундах).
        """
        if self.level > 0:
            # Константа скорости распада, основанная на времени полураспада
            # Формула скорости распада: k = ln(2) / T_half, где T_half — время полураспада
            decay_rate = 0.693 / self.half_life
            
            # Экспоненциальное уменьшение уровня гормона за время delta_time
            # self.level *= (2 ** (-delta_time / self.half_life))
            self.level *= math.exp(-0.693 * delta_time / self.half_life)

    def increase(self, amount):
        """
        Увеличение уровня гормона.
        
        :param amount: Количество, на которое нужно увеличить уровень гормона.
        """
        self.level += amount
        if self.level < 0:
            self.level = 0  # Гормон не может быть отрицательным

    def draw(self, x, y, background_color, screen):
        """Рисует представление гормона."""
        font = pygame.font.Font(None, 18)
        text = font.render(f"{self.name}: {self.level:.2f}", True, (255, 255, 255))
        screen.blit(text, (x, y))

    def __repr__(self):
        return f"{self.name}: {self.level:.2f}"

# Класс сердечно-сосудистой системы
class Heart:
    def __init__(self, cur_rate, norm_rate, max_rate, min_rate, regulator, ad_norm):
        self.cur_rate = cur_rate  # Текущая частота сердечных сокращений
        self.norm_rate = norm_rate  # Нормальная ЧСС
        self.max_rate = max_rate  # Максимальная ЧСС
        self.min_rate = min_rate  # Минимальная ЧСС
        self.regulator = regulator  # Регулятор для взаимодействия с другими системами
        self.ad_cur = 0
        self.ad_norm = ad_norm  # Нормальное артериальное давление
        self.cur_time = 0
        self.pulse_history = [70] * 50  # Инициализируем исторические данные

    def calculate_baroreflex_effect(self, new_pressure):
        # Учёт барорефлекса — реакция на изменение давления
        if new_pressure > self.ad_norm:
            return - (new_pressure - self.ad_norm) * 5  # Уменьшение ЧСС при повышенном давлении
        else:
            return (self.ad_norm - new_pressure) * 5  # Увеличение ЧСС при пониженном давлении

    def calculate_dV(self, dT, SBP, DBP):
        """
        dQ — объемный поток,
        D - диаметр сосуда капиляров у альвеол, 0.0001 м
        R — радиус сосуда, R = D / 2
        L — длина сосуда, 2000-3000 км
        n — вязкость крови, 4-5 мПа*с
        dP — разница давлений по длине сосуда,
        SBP - Систолическое давление
        DBP - Диастолическое давление
        dV - объем крови перекачиваемый через сосуды в легких, за время dT
        dT - время одного сердечного сокращения

        dP = SBP−DBP
        dQ = pi*(R^4) * dP / (8*n*L)
        dV = dQ * dT
        """
        # Константы
        D = 0.0001  # Диаметр сосуда капилляров в метрах (100 мкм)
        R = D / 2  # Радиус сосуда
        L = 2000000  # Длина сосуда в метрах (2000 км)
        n = 0.004  # Вязкость крови в Па·с (4 мПа·с)

        # Разница давлений
        dP = SBP - DBP

        # Расчет объемного потока (dQ)
        dQ = (math.pi * (R ** 4) * dP) / (8 * n * L)

        # Расчет объема крови (dV)
        dV = dQ * dT

        return dV

    def calculate_recovery_heart_rate(self, delta_time, delta_hr):
        # Логика восстановления ЧСС
        if delta_hr > 0:
            k = math.log(1 + delta_hr / (20 * 60))  # 30 минут восстановление
        else:
            k = math.log(1 + delta_hr / (10 * 60))  # 10 минут восстановление
        return delta_time * k

    # Функция для расчета ЧСС с учетом влияния адреналина и барорефлекса
    def calc_heart_rate(self, hormones, arterial_pressure):
        self.ad_cur = (arterial_pressure.systolic["cur"] - arterial_pressure.diastolic["cur"])
        self.ad_norm = (arterial_pressure.systolic["norm"] - arterial_pressure.diastolic["norm"])

        # Рассчитываем текущее давление (разница между систолическим и диастолическим)
        ad_k = self.ad_cur / self.ad_norm  # Коэффициент отношения текущего давления к норме

        # Увеличение ЧСС под действием адреналина
        A = hormones["adrenalin"].level
        alpha = 40.0  # Максимальное увеличение ЧСС на 40 ударов в минуту при максимальном уровне адреналина
        hr_deltaA = alpha * A  # Прямое воздействие адреналина на ЧСС

        # Рассчитываем новое давление под действием увеличенной ЧСС из-за адреналина
        pressure_increase_due_to_hr = hr_deltaA * 0.1  # Коэффициент влияния ЧСС на давление
        new_pressure = self.ad_cur + pressure_increase_due_to_hr

        # Рассчитываем эффект барорефлекса
        baroreflex_effect = self.calculate_baroreflex_effect(new_pressure)

        # Новое значение ЧСС с учетом влияния адреналина и барорефлекса
        hr_new = self.norm_rate + hr_deltaA + baroreflex_effect

        # Ограничение ЧСС минимальным и максимальным значениями
        hr_new = max(min(hr_new, self.max_rate), self.min_rate)

        return hr_new

    # Основной метод обновления сердечного ритма
    def update(self, hormones, arterial_pressure, respiratory, delta_time):
        # Обновляем ЧСС на основе гормонов и артериального давления
        hr_delta = self.cur_rate - self.norm_rate
        recovery_effect = self.calculate_recovery_heart_rate(delta_time, hr_delta)
        self.cur_rate = self.calc_heart_rate(hormones, arterial_pressure) - recovery_effect

        hr_time = 60.0 / self.cur_rate
        self.cur_time += delta_time
        if self.cur_time >= hr_time:
            # расчитываем объем крови прокачки сердца
            dV = self.calculate_dV(hr_time, arterial_pressure.systolic["cur"], arterial_pressure.diastolic["cur"])
            respiratory.update_blood(dV, arterial_pressure)
            self.cur_time -= hr_time

            self.pulse_history.append(self.cur_rate)
            self.pulse_history.pop(0)  # Удаляем старейшее значение

        # Проверяем уровень адреналин для вывода предупреждения
        if hormones["adrenalin"].level < 0.2:  # Низкий уровень адреналина
            self.regulator.send_message('adrenalin', 'adjust_hormone')

        # Вывод текущего состояния сердечного ритма
        print(f"Сердечный ритм: текущий {self.cur_rate}, нормальный {self.norm_rate}")

    def draw(self, x, y, background_color, screen):
        """Рисует сердце."""
        pygame.draw.circle(screen, (255, 0, 0), (x+60, y), 50*self.cur_rate/self.max_rate)
        font = pygame.font.Font(None, 18)
        text = font.render(f"Heart Rate (bpm): {self.cur_rate:.1f}", True, (255, 255, 255))
        screen.blit(text, (x, y+60))

        # Рисуем историю пульса как график
        history_height = 50  # Высота графика
        history_width = 100  # Ширина графика
        # start_x = x - history_width // 2  # Начальная координата X для графика
        start_x = x  # Начальная координата X для графика
        start_y = y + 100  # Начальная координата Y для графика

        # Фон для истории пульса
        pygame.draw.rect(screen, background_color, (start_x, start_y, history_width, history_height))

        # Масштабирование значений истории пульса
        min_pulse = min(self.pulse_history)
        max_pulse = max(self.pulse_history)
        if max_pulse == min_pulse:
            max_pulse += 1  # Избегаем деления на 0
        scaled_history = [
            history_height - int((pulse - min_pulse) / (max_pulse - min_pulse) * history_height)
            for pulse in self.pulse_history
        ]

        # Рисуем линии графика
        for i in range(1, len(scaled_history)):
            x1 = start_x + (i - 1) * (history_width // len(self.pulse_history))
            y1 = start_y + scaled_history[i - 1]
            x2 = start_x + i * (history_width // len(self.pulse_history))
            y2 = start_y + scaled_history[i]
            pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2), 2)

        # Подпись графика
        graph_label = font.render("Pulse History", True, (255, 255, 255))
        screen.blit(graph_label, (start_x, start_y - 20))

# Класс дыхательной системы
class Respiratory:
    E = 1e6  # Модуль Юнга, Па (1 МПа)
    rho = 1000  # Плотность, кг/м³ (плотность легочной ткани)
    R = 8.314  # Универсальная газовая постоянная, Дж/(моль·К)
    atmospheric_pressure = 101325 # атмосферное давление 101325Па = 101.325кПа.

    # константы Генри
    # Коэффициент растворимости кислорода в крови 0.003 мл O₂ / (мм рт. ст. мл крови).
    k_O2 = 0.003
    # Коэффициент растворимости углекислого газа в крови 0.07 мл O₂ / (мм рт. ст. мл крови).
    k_CO2 = 0.07


    def __init__(self, oxygen, carbon_dioxide, lung_volumes, regulator):
        
        self.norm_rate = 16
        self.max_rate = 40
        self.min_rate = 8
        self.inhale_time_min = 0.7

        # Базовые диаметры в нормальном состоянии
        self.base_trachea_diameter = 1.8  # см, примерное значение для трахеи
        self.base_bronchi_diameter = 1.44  # см, примерное значение для бронхов
        self.base_bronchioles_diameter = 0.072  # см, примерное значение для бронхиол

        self.breath_rate = 0  # Текущий дыхательный ритм (вдохов в минуту)
        self.inhale_duration = 0  # Продолжительность вдоха в секундах
        self.exhale_duration = 0  # Продолжительность выдоха в секундах
        self.inhaled_volume = 0  # Объем вдыхаемого воздуха в м³
        self.pressure_alv = 0 # Альвеолярное давление Па
        self.pressure_pl = 0 # Плевральное давление Па
        self.transpulmonary_pressure = 0 # Транспульмональное давление Па
        self.transrespiratory_pressure = 0 # Трансреспираторное давление

        self.blood_volume_lungs = 0 # сколько крови было перекачено через легкие
        self.blood_index_lungs = 0 # индекс участка крови в легких
        self.blood_delta = 0 # сколько индексов занимает blood_volume_lungs
        self.partial_pressure_blood_oxygen = 0
        self.partial_pressure_blood_carbon_dioxide = 0

        # Tuple format: (time, duration, volume, type: 'inhale', 'exhale', 'pause')
        self.breath_history = []
        
        # Параметры дыхания
        self.oxygen = oxygen  # Уровень кислорода
        self.carbon_dioxide = carbon_dioxide  # Уровень углекислого газа
        self.lung_volumes = lung_volumes  # Объем легких
        # максимальный объем легких
        self.max_volume_lungs = 3500
        # объем легких во время вдоха (ДО) - 500 см^3
        self.volume_full_inhale = 500
        # объем легких во время дополнительного вдоха (РОВ) - 1500 см^3
        # это сколько мы можем еще вдохнуть после полного вдоха (резервный объем вдоха и выдоха)
        self.volume_partial_inhale = 1500
        # резервный объем легких
        self.volume_reserve_lungs = 1500
        self.air_speed_inhale = 0  # Скорость воздуха при вдохе
        self.air_speed_exhale = 0  # Скорость воздуха при выдохе
        self.time_respiratory = 0  # Время дыхательного цикла
        self.state = 'inhale' # inhale/exhale/pause/speech

        self.add_time_inhale = 0
        self.regulator = regulator

        # Константы
        self.d0 = 0.002  # начальная толщина стенки альвеолы
        self.R0 = 0.1  # начальный радиус альвеолы
        self.dDiff = 0.01  # коэффициент диффузии газа
        self.pi = math.pi
        '''
        В норме парциальное давление кислорода в артериальной крови (PaO2) у здорового 
        взрослого составляет около 75-100 мм рт. ст.. Это значение принято как референтный 
        уровень при дыхании на уровне моря.
        '''
        self.PaO2 = 100
        '''
        В норме парциальное давление углекислого газа (CO₂) в артериальной крови составляет 35-45 мм рт. ст.
        '''
        self.PaCO2 = 40

        self.R_cur = self.R0
        self.temperature = 310  # Температура тела в К
        # Создаем словарь legs_n
        self.legs_n = {}
        # Объем азота
        self.legs_n['nitrogen'] = lung_volumes * 0.78
        # Объем кислорода с учетом замещения
        self.legs_n['oxygen'] = lung_volumes * 0.21
        # Объем углекислого газа с учетом замещения
        self.legs_n['carbon_dioxide'] = lung_volumes * 0.0004
        # Объем аргона
        self.legs_n['argon'] = lung_volumes * 0.0093

        # Объем кислорода с учетом замещения
        V_O2 = self.lung_volumes * 0.21
        # Объем углекислого газа с учетом замещения
        V_CO2 = self.lung_volumes * 0.0004
        self.partial_pressure_legs_oxygen = (self.legs_n['oxygen'] * self.R * self.temperature) / V_O2  # Давление O₂
        self.partial_pressure_legs_carbon_dioxide = (self.legs_n['carbon_dioxide'] * self.R * self.temperature) / V_CO2  # Давление CO₂

    def calculate_radius(self, Gaz, d0, R0, dDiff):
        """
        Рассчитывает радиус альвеолы R(t) на основе уровня газа,
        начальной толщины стенки, начального радиуса, модуля Юнга, коэффициента диффузии и плотности.
        """
        return (Gaz * d0 * (R0 ** 3) * math.sqrt(2 * self.E * d0) / (math.sqrt(self.rho) * (16 * math.pi ** 2 * dDiff))) ** (1 / 9)

    def calculate_V_t(self, R_t):
        """
        Рассчитывает объем легких V(t), исходя из радиуса R(t).
        """
        V_t = (4/3) * self.pi * R_t**3
        return V_t

    def calculate_inhale_speed(self, R, d):
        """
        Рассчитывает скорость вдоха
        """
        return (2 * self.E * d / (self.rho * R**2)) ** 0.5

    def calculate_time_inhalation(self, U, Gaz):
        """
        Рассчитывает время вдоха t_inhal.
        """
        R_t = self.calculate_R_t(U, Gaz)
        V_t = self.calculate_V_t(R_t)
        t_inhal = V_t / U
        return t_inhal

    def calculate_pressure(self, oxygen_replaced_volume, carbon_dioxide_replaced_volume):
        """
        Альвеолярным давлением называют давление газа внутри альвеол лёгких. Оно определяет
        обмен газов между воздухом в лёгочных альвеолах и кровью в капиллярах, окружающих
        эти альвеолы. В нормальных условиях при вдохе альвеолярное давление ниже атмосферного,
        а при выдохе – выше. Это обеспечивает движение воздуха внутрь и наружу лёгких.

        Рассчитывает давление в легких с учетом диффузии O2 и CO2.
        
        :param oxygen_replaced_volume: Объем O2, который заменяется CO2 в м³.
        """
        # Объемы каждого компонента с учетом замещения O2 на CO2
        # Объем азота
        V_N2 = self.inhaled_volume * 0.78
        # Объем кислорода с учетом замещения
        V_O2 = self.inhaled_volume * 0.21 - oxygen_replaced_volume
        # Объем углекислого газа с учетом замещения
        V_CO2 = self.inhaled_volume * 0.0004 + carbon_dioxide_replaced_volume
        # Объем аргона
        V_Ar = self.inhaled_volume * 0.0093

        # Проверка, чтобы объем O2 не стал отрицательным
        if V_O2 < 0:
            V_O2 = 0

        # Рассчитываем общее количество вещества для каждого компонента
        n_N2 = V_N2 / 22.4  # моль N₂ (при нормальных условиях)
        n_O2 = V_O2 / 32  # моль O₂
        n_CO2 = V_CO2 / 44  # моль CO₂
        n_Ar = V_Ar / 40  # моль Ar

        # Общее количество вещества
        n_total = n_N2 + n_O2 + n_CO2 + n_Ar

        # Рассчитываем давление в легких
        V_m3 = (self.lung_volumes + self.inhaled_volume) / 1e6  # Преобразуем объем в м³
        P_alv = (n_total * self.R * self.temperature) / V_m3  # Давление в альвеолах, Па
        return P_alv

    def calculate_pleural_pressure(self, P_alv, oxygen_replaced_volume, carbon_dioxide_replaced_volume):
        """
        Плевральным давлением называется давление в плевральной полости, которая находится
        между двумя плеврами: висцеральной (прилегающей к легким) и париетальной
        (прилежащей к стенке грудной клетки). В норме оно всегда отрицательное
        относительно атмосферного давления. Отрицательное значение этого давления помогает
        удерживать легкие в растянутом состоянии и способствует их расширению  при вдохе.
        """
        n_O2 = oxygen_replaced_volume / 32  # моль O₂ для объема oxygen_replaced_volume
        n_CO2 = carbon_dioxide_replaced_volume / 44  # моль CO₂ для объема carbon_dioxide_replaced_volume

        P_O2 = (n_O2 * self.R * self.temperature) / oxygen_replaced_volume  # Давление O₂
        P_CO2 = (n_CO2 * self.R * self.temperature) / carbon_dioxide_replaced_volume  # Давление CO₂

        delta_P = P_CO2 - P_O2  # Изменение давления из-за диффузии
        P_pl = P_alv - delta_P  # Плевральное давление
        return P_pl

    def calculate_transpulmonary_pressure(self, oxygen_replaced_volume, carbon_dioxide_replaced_volume):
        """
        Транспульмональным давлением, также называемым трансреспираторным давлением,
        является разница между альвеолярным и плевральным давлениями. Это давление
        отражает силу, необходимую для расширения лёгких против эластической тяги
        тканей лёгких и стенок грудной клетки.
        """
        P_alv = self.calculate_pressure(oxygen_replaced_volume, carbon_dioxide_replaced_volume)
        P_pl = self.calculate_pleural_pressure(P_alv, oxygen_replaced_volume, carbon_dioxide_replaced_volume)

        TPP = P_alv - P_pl
        return TPP

    def calculate_diameter_with_hormones(self, base_diameter, hormones):
        """
        Рассчитывает диаметр дыхательных путей с учетом воздействия гормонов.

        :param base_diameter: базовый диаметр дыхательных путей в нормальном состоянии (без учета гормонов).
        :param hormones: словарь с уровнями гормонов: {"adrenaline": 0-1, "acetylcholine": 0-1, "cortisol": 0-1}.
        :return: модифицированный диаметр дыхательных путей с учетом гормонов.
        """
        # Извлекаем уровни гормонов
        adrenaline_level = hormones["adrenalin"].level  # Уровень адреналина (0-1)
        acetylcholine_level = hormones["acetylcholine"].level  # Уровень ацетилхолина (0-1)
        cortisol_level = hormones["cortisol"].level  # Уровень кортизола (0-1)

        # Применяем коэффициенты влияния гормонов на диаметр дыхательных путей
        modified_diameter = base_diameter * (
            1 + 0.3 * adrenaline_level  # Увеличение диаметра от адреналина
            - 0.2 * acetylcholine_level  # Уменьшение диаметра от ацетилхолина
            + 0.1 * cortisol_level  # Незначительное увеличение диаметра от кортизола
        )
    
        return modified_diameter

    def calculate_gas_diffusion(self, Diff, S, T, P1, P2):
        """
        Рассчитывает скорость диффузии газа между альвеолами и кровью.

        Параметры:
        Diff (float): Коэффициент диффузии газа (м²/с).
        S (float): Площадь поверхности обмена газов (м²).
        T (float): Толщина мембраны (м).
        P1 (float): Парциальное давление газа в альвеолах (Па).
        P2 (float): Парциальное давление газа в капиллярах (Па).

        Возвращает:
        float: Скорость диффузии газа (моль/с).
        """
        return (Diff * S / T) * (P1 - P2)

    def update_blood(self, blood_volume, arterial_pressure):
        self.blood_delta = self.blood_volume_lungs / arterial_pressure.blood_dV_min
        # смещение индекса участка крови с легкими
        self.blood_index_lungs += self.blood_delta
        self.blood_index_lungs %= arterial_pressure.blood_count

        self.blood_volume_lungs = blood_volume

    def diffusion(self, arterial_pressure):
        blood_next_lungs = self.blood_index_lungs + self.blood_delta
        blood_index = int(self.blood_index_lungs)
        blood_index_next = int(blood_next_lungs % arterial_pressure.blood_count)

        # расчет молярной массы кислорода и углекислого газа в участках крови dV
        v1 = 1.0 - (self.blood_index_lungs % 1)
        v3 = 1.0 - v1
        v2 = int(blood_next_lungs) - blood_index

        blood_oxygen = v1 * arterial_pressure.bloods[int(blood_index)][0]
        blood_carbon_dioxide = v1 * arterial_pressure.bloods[int(blood_index)][1]

        for index in range(v2):
            blood_index_full = (blood_index + index + 1) % arterial_pressure.blood_count
            blood_oxygen += arterial_pressure.bloods[blood_index_full][0]
            blood_carbon_dioxide += arterial_pressure.bloods[blood_index_full][1]

        if blood_index != blood_index_next:
            blood_oxygen += v3 * arterial_pressure.bloods[blood_index_next][0]
            blood_carbon_dioxide += v3 * arterial_pressure.bloods[blood_index_next][1]

        # Парциальное давление кислорода в крови
        self.partial_pressure_blood_oxygen = blood_oxygen
        # Парциальное давление углекислого газа в крови
        self.partial_pressure_blood_carbon_dioxide = blood_oxygen

        # диффузия газов
        self.pressure_alv = self.calculate_pressure(blood_oxygen, blood_carbon_dioxide)
        self.pressure_pl = self.calculate_pleural_pressure(self.pressure_alv, blood_oxygen, blood_carbon_dioxide)
        self.transpulmonary_pressure = self.calculate_transpulmonary_pressure(blood_oxygen, blood_carbon_dioxide)
        self.transrespiratory_pressure = self.pressure_alv - self.atmospheric_pressure

        print(f"Альвеолярное давление: {self.pressure_alv} Па")
        print(f"Плевральное давление: {self.pressure_pl} Па")
        print(f"Транспульмональное давление: {self.transpulmonary_pressure} Па")

    def replace_partial_pressure(self, arterial_pressure, pressure_oxygen, pressure_carbon_dioxide):

        blood_next_lungs = self.blood_index_lungs + self.blood_delta
        blood_index = int(self.blood_index_lungs)
        blood_index_next = int(blood_next_lungs % arterial_pressure.blood_count)

        # расчет молярной массы кислорода и углекислого газа в участках крови dV
        v1 = 1.0 - (self.blood_index_lungs % 1)
        v3 = 1.0 - v1
        v2 = int(blood_next_lungs) - blood_index

        blood_oxygen = v1 * arterial_pressure.bloods[int(blood_index)][0]
        blood_carbon_dioxide = v1 * arterial_pressure.bloods[int(blood_index)][1]

        for index in range(v2):
            blood_index_full = (blood_index + index + 1) % arterial_pressure.blood_count
            blood_oxygen += arterial_pressure.bloods[blood_index_full][0]
            blood_carbon_dioxide += arterial_pressure.bloods[blood_index_full][1]

        if blood_index != blood_index_next:
            blood_oxygen += v3 * arterial_pressure.bloods[blood_index_next][0]
            blood_carbon_dioxide += v3 * arterial_pressure.bloods[blood_index_next][1]

        # во сколько раз изменилось давление
        k_oxygen = pressure_oxygen / blood_oxygen
        k_carbon_dioxide = pressure_carbon_dioxide / blood_carbon_dioxide

        # изменяем давление у кислорода в начальном участки крови
        blood_oxygen = arterial_pressure.bloods[int(blood_index)][0]
        blood_oxygen = v1 * blood_oxygen * k_oxygen + v3 * blood_oxygen
        arterial_pressure.bloods[int(blood_index)][0] = blood_oxygen

        # изменяем давление у углекислого газа в начальном участки крови
        blood_carbon_dioxide = arterial_pressure.bloods[int(blood_index)][1]
        blood_carbon_dioxide = v1 * blood_carbon_dioxide * k_carbon_dioxide + v3 * blood_carbon_dioxide
        arterial_pressure.bloods[int(blood_index)][1] = blood_carbon_dioxide

        for index in range(v2):
            blood_index_full = (blood_index + index + 1) % arterial_pressure.blood_count

            # изменяем давление у кислорода в центральных участках крови
            blood_oxygen = arterial_pressure.bloods[blood_index_full][0]
            blood_oxygen = blood_oxygen * k_oxygen
            arterial_pressure.bloods[blood_index_full][0] = blood_oxygen

            # изменяем давление у углекислого газа в центральных участках крови
            blood_carbon_dioxide = arterial_pressure.bloods[blood_index_full][1]
            blood_carbon_dioxide = blood_carbon_dioxide * k_carbon_dioxide
            arterial_pressure.bloods[blood_index_full][1] = blood_carbon_dioxide

        if blood_index != blood_index_next:
            # изменяем давление у кислорода в конечном участки крови
            blood_oxygen = arterial_pressure.bloods[blood_index_next][0]
            blood_oxygen = v3 * blood_oxygen * k_oxygen + v1 * blood_oxygen
            arterial_pressure.bloods[blood_index_next][0] = blood_oxygen

            # изменяем давление у углекислого газа в начальном участки крови
            blood_carbon_dioxide = arterial_pressure.bloods[blood_index_next][1]
            blood_carbon_dioxide = v3 * blood_carbon_dioxide * k_carbon_dioxide + v1 * blood_carbon_dioxide
            arterial_pressure.bloods[blood_index_next][1] = blood_carbon_dioxide

    def inhale(self, hormones, arterial_pressure, delta_time):
        self.diffusion(arterial_pressure)

        # для расчета диффузии газов между альвеолами и капиллярами в легких обычно используется уравнение Фика, которое описывает скорость диффузии газа через мембрану.
        # U газ = A*D*(P альвеолы − P кровь) / T
        # U газ — скорость диффузии газа (объем газа, диффундирующего за единицу времени),
        # A — площадь поверхности обмена (альвеолярная поверхность),
        # D — коэффициент диффузии для конкретного газа (в зависимости от его растворимости и молекулярной массы),
        # P альвеолы и P кровь — парциальные давления газа в альвеолах и крови соответственно,
        # T — толщина мембраны, через которую происходит диффузия.

        # Разность парциальных давлений (P альвеолы − P кровь): Чем больше разность парциальных давлений, тем интенсивнее диффузия.
        # Площадь поверхности обмена A:** Увеличение площади обмена, как в альвеолах, способствует большей диффузии.
        # Толщина мембраны T:** Чем тоньше мембрана, тем выше скорость диффузии.
        # Коэффициент диффузии D:** Он зависит от типа газа: кислород и углекислый газ имеют разные коэффициенты диффузии, так как CO2 легче растворяется в крови, чем O2 , и, следовательно, имеет более высокий D.

        # Рассчитаем диффузию газа
        S_t = 4 * math.pi * (self.R_cur ** 2)  # площадь альвеол
        d_t = self.d0 * ((self.R_cur / self.R0)**2)
        Diff_t = self.dDiff * S_t / d_t

        diffusion_rate_oxygen = self.calculate_gas_diffusion(Diff_t, S_t, self.temperature,
                                                             self.partial_pressure_blood_oxygen,
                                                             self.partial_pressure_legs_oxygen)
        diffusion_rate_carbon_dioxide = self.calculate_gas_diffusion(Diff_t, S_t, self.temperature,
                                                                     self.partial_pressure_blood_carbon_dioxide,
                                                                     self.partial_pressure_legs_carbon_dioxide)
        print(f"Скорость диффузии кислорода: {diffusion_rate_oxygen:.6f} моль/с")
        print(f"Скорость диффузии углекислого газа: {diffusion_rate_carbon_dioxide:.6f} моль/с")

        n_oxygen = diffusion_rate_oxygen * delta_time
        n_carbon_dioxide = diffusion_rate_carbon_dioxide * delta_time

        # Рассчитываем общее количество вещества для каждого компонента
        self.legs_n['oxygen'] -= n_oxygen
        self.legs_n['carbon_dioxide'] += n_carbon_dioxide

        # Общее количество вещества
        n_total = 0
        for name in self.legs_n:
            n_total += self.legs_n[name]

        # Рассчитываем давление в легких
        V_m3 = (n_total * self.R * self.temperature) / self.pressure_alv
        dV_legs = V_m3 - self.lung_volumes

        # кровь
        self.partial_pressure_blood_oxygen += (n_oxygen * self.R * self.temperature) / self.blood_volume_lungs
        self.partial_pressure_blood_carbon_dioxide -= (n_carbon_dioxide * self.R * self.temperature) / self.blood_volume_lungs

        self.replace_partial_pressure(arterial_pressure,
                                      self.partial_pressure_blood_oxygen, self.partial_pressure_blood_carbon_dioxide)

        # легкие
        self.partial_pressure_legs_oxygen -= (self.legs_n['oxygen'] * self.R * self.temperature) / dV_legs
        self.partial_pressure_legs_carbon_dioxide += (self.legs_n['carbon_dioxide'] * self.R * self.temperature) / dV_legs

        self.R_cur = ((3*V_m3) / (4*math.pi))**(1/3.)

        if dV_legs > 0:
            # Объем азота
            self.legs_n['nitrogen'] += dV_legs * 0.78
            # Объем кислорода с учетом замещения
            self.legs_n['oxygen'] += dV_legs * 0.21
            # Объем углекислого газа с учетом замещения
            self.legs_n['carbon_dioxide'] += dV_legs * 0.0004
            # Объем аргона
            self.legs_n['argon'] += dV_legs * 0.0093

            # Вычисляем скорость вдоха
            self.air_speed_inhale = self.calculate_inhale_speed(self.R_cur, self.d0)
        elif dV_legs < 0:
            # Объем азота
            self.legs_n['nitrogen'] += dV_legs * self.legs_n['nitrogen'] / self.lung_volumes
            # Объем кислорода с учетом замещения
            self.legs_n['oxygen'] += dV_legs * self.legs_n['oxygen'] / self.lung_volumes
            # Объем углекислого газа с учетом замещения
            self.legs_n['carbon_dioxide'] += dV_legs * self.legs_n['carbon_dioxide'] / self.lung_volumes
            # Объем аргона
            self.legs_n['argon'] += dV_legs * self.legs_n['argon'] / self.lung_volumes

            self.exhale(hormones, arterial_pressure, delta_time)

        self.lung_volumes = V_m3

        # Gaz = 0
        #
        # # Рассчитываем текущий радиус альвеолы
        # R_t = self.calculate_radius(Gaz, self.d0, self.R0, self.dDiff)
        # self.inhaled_volume = self.calculate_V_t(R_t)
        #
        # # Вычисляем скорость вдоха
        # self.air_speed_inhale = self.calculate_inhale_speed(R_t, self.d0)
        #
        # # Рассчитываем текущее время вдоха
        # self.inhale_duration = self.calculate_time_inhalation(self.air_speed_inhale, carbon_dioxide_replaced_volume)

        # Логируем историю вдохов
        self.breath_history.append((self.time_respiratory, self.inhale_duration, self.lung_volumes, 'inhale'))


    def exhale(self, hormones, arterial_pressure, delta_time):
        # Рассчитаем диаметры с учетом воздействия гормонов
        trachea_diameter = self.calculate_diameter_with_hormones(self.base_trachea_diameter, hormones)
        bronchi_diameter = self.calculate_diameter_with_hormones(self.base_bronchi_diameter, hormones)
        bronchioles_diameter = self.calculate_diameter_with_hormones(self.base_bronchioles_diameter, hormones)

        trachea_length = vc.calculate_length(self.regulator.height)
        bronchi_length = trachea_length * 0.4
        bronchioles_length = bronchi_length * 0.2

        # Расчет сопротивления
        trachea_resistance = vc.darcy_weisbach_resistance(vc.friction_factor_trachea, trachea_length, trachea_diameter)
        bronchi_resistance = vc.darcy_weisbach_resistance(vc.friction_factor_bronchi, bronchi_length, bronchi_diameter)
        bronchioles_resistance = vc.darcy_weisbach_resistance(vc.friction_factor_bronchioles, bronchioles_length, bronchioles_diameter)

        # Общее сопротивление
        total_resistance = trachea_resistance + bronchi_resistance + bronchioles_resistance

        # Транспульмональное давление (Ptp): Это разница между альвеолярным давлением (Palv) и плевральным давлением (Ppl):
        # Ptp = Palv - Ppl
        # Трансреспираторное давление (Ptr): Это разница между альвеолярным давлением (Palv) и давлением в атмосфере (Patm):
        # Ptr = Palv - Patm
        # Оно непосредственно участвует в создании воздушного потока во время выдоха.

        # Скорость выдоха определяется трансреспираторным давлением (Ptr), так как это давление
        # создаёт поток воздуха из лёгких наружу.
        # Транспульмональное давление (Ptp) отвечает за удержание лёгких в раскрытом
        # состоянии, но не напрямую за поток.
        # Для описания скорости выдоха правильнее использовать трансреспираторное давление.

        # Вычисляем скорость выдоха
        self.air_speed_exhale = self.transrespiratory_pressure / total_resistance
        # self.air_speed_exhale = self.transpulmonary_pressure / total_resistance

        # Рассчитываем текущее время выдоха
        self.exhale_duration = (self.lung_volumes - self.volume_reserve_lungs) / self.air_speed_exhale


    def pause(self, hormones, arterial_pressure, delta_time):
        '''
        При избытке CO₂ — пауза между вдохом и выдохом сокращается или исчезает, увеличивается частота дыхания.
        При недостатке O₂ — увеличивается объём вдоха и продолжительность самого вдоха, иногда увеличивая паузу,
        но эффект менее выражен, чем от CO₂.
        В условиях спокойного дыхания (называемого «нормальным» или эвпноэ) пауза может составлять от 0,5 до 2 секунд.
        '''
        # парциальное давление кислорода
        partial_pressure_O2 = self.k_O2 * self.oxygen
        # парциальное давление углекислого газа
        partial_pressure_CO2 = self.k_CO2 * self.carbon_dioxide
        self.pause_duration = 1.0 * (partial_pressure_O2 / self.PaO2) * (self.PaCO2 / partial_pressure_CO2)

        return

    def speech(self, hormones, arterial_pressure, delta_time):
        return

    def update(self, hormones, arterial_pressure, delta_time):
        # Пример влияния гормонов на дыхание
        if hormones["serotonin"].level > 15:
            self.breath_rate = min(self.max_rate, self.breath_rate + 1)  # Увеличиваем частоту дыхания
        elif hormones["cortisol"].level > 20:
            self.breath_rate = max(self.min_rate, self.breath_rate - 1)  # Уменьшаем частоту дыхания

        # Проверка уровня кислорода
        if self.oxygen < 90:  # Условие для низкого уровня кислорода
            self.regulator.send_message('Respiratory', 'Низкий уровень кислорода!')

        if self.state == 'inhale':
            self.inhale(hormones, arterial_pressure, delta_time)
        elif self.state == 'exhale':
            self.exhale(hormones, arterial_pressure, delta_time)
        elif self.state == 'pause':
            self.pause(hormones, arterial_pressure, delta_time)
        else:
            self.speech(hormones, arterial_pressure, delta_time)

        print(f"Обновленная продолжительность вдоха: {self.inhale_duration:.4f} сек")
        print(f"Обновленная история дыхания: {self.breath_history}")

    def update_breath_history(self, time, duration, volume, breath_type):
        # Remove entries older than the last 60 seconds
        self.breath_history = [(t, d, v, bt) for t, d, v, bt in self.breath_history if t >= time - 60]
        
        # Add new entry
        self.breath_history.append((time, duration, volume, breath_type))

        # Пересчёт дыхательной частоты (количество вдохов за последние 60 секунд)
        inhale_count = sum(1 for t, d, v, bt in self.breath_history if bt == 'inhale')
        self.breath_rate = inhale_count * 60 // 60  # Частота дыхания в "вдохов в минуту"

    def draw(self, x, y, background_color):
        # Создание фигуры
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(background_color)
        ax.set_facecolor(background_color)

        # Извлечение времени и объема из истории дыхания
        times = [entry[0] for entry in self.breath_history]
        volumes = [entry[2] for entry in self.breath_history]
        types = [entry[3] for entry in self.breath_history]

        # Отрисовка объема дыхания
        ax.plot(times, volumes, label="Breath Volume", color="blue", marker="o")

        # Подпись текущего состояния дыхания по центру
        current_breath = self.breath_history[-1]
        ax.text(times[-1], volumes[-1], f"{current_breath[3].capitalize()}: {current_breath[2]} ml", va='center', color='white', fontsize=12)

        # Вывод параметров дыхания справа
        ax.text(1.05, 0.8, f"Breath Rate: {self.breath_rate} breaths/min", transform=ax.transAxes, color='white')
        ax.text(1.05, 0.7, f"Oxygen: {self.oxygen}%", transform=ax.transAxes, color='white')
        ax.text(1.05, 0.6, f"CO2: {self.carbon_dioxide}%", transform=ax.transAxes, color='white')
        ax.text(1.05, 0.5, f"Lung Volumes: {self.lung_volumes} ml", transform=ax.transAxes, color='white')
        ax.text(1.05, 0.4, f"Air Speed Inhale: {self.air_speed_inhale} L/s", transform=ax.transAxes, color='white')
        ax.text(1.05, 0.3, f"Air Speed Exhale: {self.air_speed_exhale} L/s", transform=ax.transAxes, color='white')
        ax.text(1.05, 0.2, f"Respiratory Time: {self.time_respiratory} s", transform=ax.transAxes, color='white')

        # Настройка заголовка и подписей осей
        ax.set_title("Respiratory Cycle History", color='white')
        ax.set_xlabel("Time (s)", color='white')
        ax.set_ylabel("Volume (ml)", color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        plt.show()

# Класс артериального давления
class ArterialPressure:
    def __init__(self, systolic_cur, systolic_norm, systolic_max, systolic_min, 
                 diastolic_cur, diastolic_norm, diastolic_max, diastolic_min,
                 respiratory, regulator):
        self.systolic = {"cur": systolic_cur, "norm": systolic_norm, "max": systolic_max, "min": systolic_min}
        self.diastolic = {"cur": diastolic_cur, "norm": diastolic_norm, "max": diastolic_max, "min": diastolic_min}
        # базовый уровень давления
        self.base_pressure = {"sys": self.systolic["min"], "dia": self.diastolic["min"]}
        self.regulator = regulator
        # объем крови
        # У мужчин: от 5000 до 6000 мл
        # У женщин: от 4500 до 5500 мл
        self.blood_volume = 5000
        self.blood_count = 5000  # кол-во участков крови (уровень детализации)
        self.blood_dV_min = self.blood_volume / self.blood_count  # объем участка крови
        dO2 = respiratory.oxygen / self.blood_count
        dCO2 = respiratory.carbon_dioxide / self.blood_count
        self.bloods = [[dO2, dCO2] for _ in range(self.blood_count)]  # кровь

    def calc_arterial_pressure(self, adrenalin, norepinephrine, delta_time):
        # Рассчитаем текущее артериальное давление
        ad_cur = (self.systolic["cur"] - self.diastolic["cur"]) / (self.systolic["norm"] - self.diastolic["norm"])
        hr_k = 1  # Предполагаем, что влияние частоты сердечных сокращений уже учтено или не изменяется
        
        # delta_time /= 60

        # Скорость метаболизма гормонов
        k = 0.5
        dA, err = integrate.quad(self.hormone_metabolism, 0.0, delta_time, args=(adrenalin, k, ad_cur, hr_k))
        k = 0.1  # Константа скорости метаболизма
        dN, err = integrate.quad(self.hormone_metabolism, 0.0, delta_time, args=(norepinephrine, k, ad_cur, hr_k))

        # Влияние гормонов на систолическое и диастолическое давление
        # Исследования и литературные источники
        # Адреналин: Исследования показывают, что у людей повышение уровня адреналина увеличивает
        # систолическое давление на 20-40 мм рт. ст., в то время как диастолическое давление может
        # изменяться на 10-20 мм рт. ст. в зависимости от дозы.
        # Норадреналин: Повышение уровня норадреналина, напротив, вызывает увеличение систолического
        # давления на 30-50 мм рт. ст., а диастолического давления — на 15-30 мм рт. ст. Это связано
        # с его сосудосуживающим действием.
        alpha_sys = 30.0
        beta_sys = 15.0
        alpha_dia = 40.0
        beta_dia = 20.0

        # увеличение систолического
        delta_systolic = alpha_sys * dA + beta_sys * dN
        # увеличение диастолического
        delta_diastolic = alpha_dia * dA + beta_dia * dN

        # Применяем масштабирование
        delta_systolic *= 1.0
        delta_diastolic *= 0.5

        # Давление всегда стремится к базовому уровню, а гормоны отклоняют его от этого состояния
        # Обновляем систолическое давление
        self.systolic["cur"] = self.base_pressure["sys"] + delta_systolic
        self.systolic["cur"] = max(min(self.systolic["cur"], self.systolic["max"]), self.systolic["min"])

        # Обновляем диастолическое давление
        self.diastolic["cur"] = self.base_pressure["dia"] + delta_diastolic
        self.diastolic["cur"] = max(min(self.diastolic["cur"], self.diastolic["max"]), self.diastolic["min"])

    def hormone_metabolism(self, t, hormone, k, ad_k, hr_k):
        # Модель метаболизма гормонов
        return max(hormone * ad_k * math.exp(-k*t*hr_k), 0)

    def update(self, hormones, delta_time):
        # Передаем адреналин и норадреналин в функцию обновления давления
        self.calc_arterial_pressure(hormones["adrenalin"].level,
                                    hormones["norepinephrine"].level, delta_time)

        # Проверяем уровень норадреналина для вывода предупреждения
        if hormones["norepinephrine"].level < 2.0:  # Низкий уровень норадреналина
            self.regulator.send_message('norepinephrine', 'adjust_hormone')

        # Вывод текущего состояния артериального давления
        print(f"Артериальное давление: систолическое {self.systolic['cur'] }, диастолическое {self.diastolic['cur']} нормальное {self.systolic['norm'] } / {self.diastolic['norm']}")

    def draw(self, x, y, background_color, screen):
        """Рисует параметры давления и визуализацию кровообращения."""
        font = pygame.font.Font(None, 24)

        # Вывод значений давления
        pressure_text = f"Систолическое: {self.systolic['cur']:.1f} / Диастолическое: {self.diastolic['cur']:.1f}"
        text_surface = font.render(pressure_text, True, (255, 255, 255))
        screen.blit(text_surface, (x, y - 50))

        # Кровообращение (визуализация цепочки крови)
        radius = 150
        center_x, center_y = x + radius, y + radius
        blood_count = len(self.bloods)
        angle_step = 2 * math.pi / blood_count

        for i, blood in enumerate(self.bloods):
            angle = i * angle_step
            blood_x = center_x + radius * math.cos(angle)
            blood_y = center_y + radius * math.sin(angle)

            # Цвет крови в зависимости от уровня O2 и CO2
            oxygen_level = blood[0] / 0.05
            carbon_dioxide_level = blood[1] / 0.02
            red = 255
            green = min(255, int(oxygen_level * 255))
            blue = min(255, int(carbon_dioxide_level * 255))

            # Рисуем частицы крови
            pygame.draw.circle(screen, (red, green, blue), (int(blood_x), int(blood_y)), 5)

# Класс метаболизма
class Metabolism:
    def __init__(self, glucose, energy, regulator):
        self.glucose = glucose
        self.energy = energy
        self.regulator = regulator

    def update(self, hormones, arterial_pressure, respiratory, delta_time):

        self.hormones = hormones

        # Проверка уровня глюкозы
        #if self.glucose < 70:  # Условие для низкого уровня глюкозы
        #    self.regulator.send_message('Metabolism', 'Низкий уровень глюкозы!')

        self.calculate_energy(arterial_pressure, respiratory)   # Расчёт энергии

        print(f"Метаболизм: глюкоза {self.glucose}, энергия {self.energy}")

    def calculate_energy(self, arterial_pressure, respiratory):
        """
        Расчёт энергии, необходимой для поддержания основного метаболизма,
        с учётом уровня глюкозы, кислорода и гормонов.
        Basal Metabolic Rate (BMR) это минимальное количество энергии, необходимое для обеспечения нормальной жизнедеятельности организма в стандартных условиях.
        https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%BE%D0%B1%D0%BC%D0%B5%D0%BD
        """
        # Основной обмен веществ (BMR) в ккал/сек
        basal_metabolism = 0.0770256355

        # Уровень стресса, основанный на уровне адреналина
        stress = self.hormones["adrenalin"].level

        # Потребность в энергии увеличивается в зависимости от стресса
        energy_need = basal_metabolism * (1 + stress)
        self.energy -= energy_need
        energy_need -= min(self.energy, 0)

        # Доступная энергия из глюкозы, зависящая от уровня кортизола
        energy_available_gl = self.glucose #* self.hormones["cortisol"].level

        # Доступная энергия из кислорода
        partial_pressure_blood_oxygen = 0
        for blood in arterial_pressure.bloods:
            partial_pressure_blood_oxygen += blood[0]

        n_oxygen = partial_pressure_blood_oxygen * arterial_pressure.blood_volume / respiratory.k_O2
        energy_available_o2 = n_oxygen / 6.0 # Каждая молекула глюкозы требует 6 молекул O2

        # Доступная энергия ограничена минимумом из доступной глюкозы и кислорода
        energy_available = min(energy_available_gl, energy_available_o2)

        if energy_need > energy_available:
            if energy_available_gl > energy_available_o2:
                self.regulator.send_message('Metabolism', 'Низкий уровень кислорода!')
            elif energy_available_gl < energy_available_o2:
                self.regulator.send_message('Metabolism', 'Низкий уровень глюкозы!')

        # Прибавляем доступную энергию
        self.energy += energy_available

        # Коррекция дыхательной системы: уменьшаем уровень кислорода, увеличиваем CO2
        n_oxygen = energy_available / 6
        n_carbon_dioxide = n_oxygen

        # кровь
        partial_pressure_blood_oxygen = respiratory.k_O2 * n_oxygen / arterial_pressure.blood_volume
        partial_pressure_blood_carbon_dioxide = respiratory.k_CO2 * n_carbon_dioxide / arterial_pressure.blood_volume

        dP_oxygen = partial_pressure_blood_oxygen / arterial_pressure.blood_count
        dP_carbon_dioxide = partial_pressure_blood_carbon_dioxide / arterial_pressure.blood_count

        # остаток
        transfer_oxygen = 0
        transfer_carbon_dioxide = 0

        # обходим все участки крови и изменяем содержимое давления кислорода и углекислого газа
        for blood in arterial_pressure.bloods:
            blood[0] -= (dP_oxygen + transfer_oxygen)
            blood[1] += (dP_carbon_dioxide + transfer_carbon_dioxide)
            if blood[0] < 0:
                transfer_oxygen = abs(blood[0])
                transfer_carbon_dioxide = dP_carbon_dioxide * (transfer_oxygen / dP_oxygen)
                blood[0] = 0
                blood[1] -= transfer_carbon_dioxide

    def draw(self, x, y, background_color):
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor(background_color)
        ax.set_facecolor(background_color)
        
        # Параметры для визуализации глюкозы и энергии
        bar_width = 0.4
        labels = ['Glucose', 'Energy']
        values = [self.glucose, self.energy]
        
        # Отрисовка значений глюкозы и энергии
        ax.bar(labels, values, width=bar_width, color=['orange', 'blue'])
        
        # Подпись текущих значений
        for i, v in enumerate(values):
            ax.text(i, v + 0.2, f"{v}", ha='center', color='white', fontsize=10)
        
        # Подписи осей и заголовок
        ax.set_title('Metabolism Levels', color='white')
        ax.set_ylabel('Level', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        plt.show()

# Центральный регулятор
class CentralRegulator:
    def __init__(self, delta_time):
        # Задаём размеры экрана
        self.screen_width = 800
        self.screen_height = 600
        self.screen = None  # Канва будет инициализирована позже

        self.delta_time = delta_time
        self.message_queue = queue.Queue()
        self.eps = 0.001
        
        # Инициализация гормонов
        self.hormones = {
            "adrenalin": Hormone("adrenalin", 0.3),
            "norepinephrine": Hormone("norepinephrine", 3.0),
            "cortisol": Hormone("cortisol", 2.0),
            "serotonin": Hormone("serotonin", 1.0),
            "oxytocin": Hormone("oxytocin", 0.03),
            "dopamine": Hormone("dopamine", 0.05),
            "endorphin": Hormone("endorphin", 0.01),
            "acetylcholine": Hormone("acetylcholine", 0.35)
        }

        # Сердечно-сосудистая система
        self.heart = Heart(cur_rate=70, norm_rate=60, max_rate=150, min_rate=40, regulator=self, ad_norm=120)

        # Дыхательная система
        self.respiratory = Respiratory(
            oxygen=95.0, carbon_dioxide=40.0, lung_volumes=500.0, regulator=self
        )
        self.respiratory.update_breath_history(70, 2.5, 480, 'inhale')
        
        # Артериальное давление
        self.arterial_pressure = ArterialPressure(
            systolic_cur=120.0, systolic_norm=120.0, systolic_max=140.0, systolic_min=90.0,
            diastolic_cur=80.0, diastolic_norm=80.0, diastolic_max=90.0, diastolic_min=60.0,
            respiratory=self.respiratory, regulator=self
        )

        # Метаболизм
        self.metabolism = Metabolism(glucose=90.0, energy=1000.0, regulator=self)

        # Инициализация первого ЧСС
        self.heart.update(self.hormones, self.arterial_pressure, self.respiratory, 60)

        # Прочие параметры
        self.time_speech_time = 0.0
        self.sex = 'male'
        self.height = 175
        self.age = 35

    def receive_message(self, message):
        print(f"Получено сообщение от {message.sender}: {message.content}")
        if message.content == 'adjust_hormone':
            hormone_name = message.sender
            if hormone_name in self.hormones:
                self.hormones[hormone_name].increase(hormone_increment[hormone_name])

    def send_message(self, recipient, content):
        message = Message(sender=recipient, content=content)
        self.message_queue.put(message)

    """Мониторинг состояния"""
    def monitor_state(self):
        self.create_canvas()

        previous_time = time.time()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            current_time = time.time()
            delta = current_time - previous_time
            effective_delta = max(self.delta_time, delta)

            # Обновляем состояние гормонов
            for hormone in self.hormones.values():
                hormone.decay(effective_delta)
            
            # Обновляем состояния
            # self.respiratory.update(self.hormones, self.arterial_pressure, self.delta_time)  # Сначала дыхательная система
            self.arterial_pressure.update(self.hormones, effective_delta)  # Затем артериальное давление
            # Обновление сердечного ритма
            self.heart.update(self.hormones, self.arterial_pressure, self.respiratory, effective_delta)
            self.metabolism.update(self.hormones, self.arterial_pressure, self.respiratory, effective_delta)   # Наконец, метаболизм

            # Отрисовка систем
            self.draw()
        
            # Обработка сообщений
            while not self.message_queue.empty():
                message = self.message_queue.get()
                self.receive_message(message)

            previous_time = time.time()

            if delta < self.delta_time:
                time.sleep(self.delta_time - delta)

        pygame.quit()

    def create_canvas(self):
        """Инициализирует канву через pygame."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Симуляция Центрального Регулятора")

    def draw(self):
        """Передаёт канву подклассам для отрисовки."""
        if not self.screen:
            raise RuntimeError("Канва не была инициализирована. Вызовите create_canvas().")

        # Заливаем экран фоновым цветом
        self.screen.fill((0, 0, 0))  # Чёрный фон

        y = 10
        for hormone in self.hormones.values():
            hormone.draw(50, y, 'black', self.screen)
            y += 20

        self.heart.draw(200, 50, 'black', self.screen)
        # self.respiratory.draw(0.5, 0.5, background_color='black')
        self.arterial_pressure.draw(400, 70, 'black', self.screen)
        # self.metabolism.draw(0.5, 0.5, background_color='black')

        # Обновляем экран
        pygame.display.flip()

        return

# Запуск мониторинга состояния
if __name__ == "__main__":
    delta_time = 1.0  # Время в секундах для каждого цикла
    regulator = CentralRegulator(delta_time)

    # Запуск в отдельном потоке
    monitoring_thread = threading.Thread(target=regulator.monitor_state)
    monitoring_thread.start()

    # Пример отправки сообщения для изменения уровня гормона
    time.sleep(5)
    regulator.send_message('adrenalin', 'adjust_hormone')
