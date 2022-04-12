
def getFuncName():
    import inspect
    return inspect.stack()[1][3]


def createRandomChn(n):
    import random
    common, rare = range(0x4e00, 0xa000), range(0x3400, 0x4e00)
    chars = list(map(chr, list(common)))
    random_word = u''.join([random.choice(chars)
                            for _ in range(n)])  # 3 letters
    return random_word
