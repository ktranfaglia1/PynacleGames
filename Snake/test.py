import random

poison = 0
gold = 0
silver = 0
green = 0

n = 100000

for i in range(n):
    x = random.randint(0, 24) * 32
    y = random.randint(0, 24) * 32
    if ((x == 12 * 32 or x == 11 * 32 or x == 10 * 32 or x == 13 * 32 or x == 14 * 32) and
            (y == 12 * 32 or y == 11 * 32 or y == 10 * 32 or y == 13 * 32 or y == 14 * 32)):
        poison += 1
    elif x == y or abs(x - y) < 8 * 8:
        silver += 1
    elif y + x == 32 * 32 or y + x == 16 * 16 or y + x == 8 * 8 or y - x == 8 * 8 or x - y == 8 * 8:
        gold += 1
    else:
        green += 1
print(poison / n)
print(gold / n)
print(silver / n)
print(green / n)
