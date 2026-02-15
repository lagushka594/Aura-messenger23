# Вспомогательные функции (например, для генерации discriminator)
import random

def generate_discriminator():
    return f'{random.randint(1000, 9999)}'