import random

poison = 0
gold = 0
silver = 0
green = 0

for i in range(100000):
    x = random.randint(0, 24) * 32
    y = random.randint(0, 24) * 32
    if (x == 12 * 32 or x == 11 * 32) and (y == 12 * 32 or y == 11 * 32):
        poison += 1
    elif x == y:
        silver += 1
    elif y + x == 32 * 32:
        gold += 1
    else:
        green += 1
print(poison)
print(gold)
print(silver)
print(green)
