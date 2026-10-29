def get_tract_length(gender, age, height):
    # height - рост в метрах
    # age - возраст в годах

    if age <= 3:
        tract_length = 5.5 + 0.5*age
    elif age <= 12:
        tract_length = 5.0 + 0.75 * age + 0.1 * height
    else:
        if gender == 'm':
            tract_length = 17.2 + 0.05 * age + 0.2 * height
        else:
            tract_length = 15.0 + 0.05 * age + 0.2 * height

    return tract_length

def get_frequency_formant(tract_length, index):
    # c = скорость звука в воздухе (примерно 343 м/с при 20°C)
    c = 343
    tract_length = tract_length * 0.01
    frequency = (2*index - 1) * c / (4*tract_length)
    return frequency

def get_tract_length_from_formant(frequencyHz, index):
    if frequencyHz > 0:
        # c = скорость звука в воздухе (примерно 343 м/с при 20°C)
        c = 343
        tract_length = (2 * index - 1) * c / (4 * frequencyHz)
    else:
        tract_length = 0
    return tract_length

def get_tract_length_from_formants(frequencyHz1, frequencyHz2, frequencyHz3, frequencyHz4, frequencyHz5):
    tract_length1 = get_tract_length_from_formant(frequencyHz1, 1)
    tract_length2 = get_tract_length_from_formant(frequencyHz2, 2)
    tract_length3 = get_tract_length_from_formant(frequencyHz3, 3)
    tract_length4 = get_tract_length_from_formant(frequencyHz4, 4)
    tract_length5 = get_tract_length_from_formant(frequencyHz5, 5)
    count = 0
    if frequencyHz1 > 0:
        count = count + 1
    if frequencyHz2 > 0:
        count = count + 1
    if frequencyHz3 > 0:
        count = count + 1
    if frequencyHz4 > 0:
        count = count + 1
    if frequencyHz5 > 0:
        count = count + 1

    if count > 0:
        tract_length = (tract_length1 + tract_length2 + tract_length3 + tract_length4 + tract_length5) / count
    else:
        tract_length = 0
    return tract_length*100
