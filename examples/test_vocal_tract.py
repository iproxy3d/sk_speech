from sk_speech import sk_vocal_tract as vk

tract_length = vk.get_tract_length('m', 25, 1.78)
print('tract length (cm)', tract_length)
frequencyHz1 = vk.get_frequency_formant(tract_length, 1)
print('F1 Hz', frequencyHz1)
frequencyHz2 = vk.get_frequency_formant(tract_length, 2)
print('F2 Hz', frequencyHz2)
frequencyHz3 = vk.get_frequency_formant(tract_length, 3)
print('F3 Hz', frequencyHz3)
frequencyHz4 = vk.get_frequency_formant(tract_length, 4)
print('F4 Hz', frequencyHz4)
frequencyHz5 = vk.get_frequency_formant(tract_length, 5)
print('F5 Hz', frequencyHz5)

tract_length = vk.get_tract_length_from_formants(frequencyHz1, frequencyHz2, frequencyHz3, frequencyHz4, frequencyHz5)
print('tract length (cm)', tract_length)
