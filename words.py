words = [
    "Koń bez rąk",
    "Koń bez nóg",
    "Żółty ananas",
    "Legia w koronie",
    "Monke in da club",
    "Słowacja",
    "Zebra",
    "997",
    "Stół z powyłamywanymi nogami",
    "Okoń"

]

from random import randint

def get_words_string(quantity):
    if quantity > len(words):
        return("error")
    else:
        words_list = words[:]
        drawn_words = []
        for i in range(quantity):
            index = randint(0, len(words_list) - 1)
            drawn_words.append(words_list[index])
            words_list.pop(index)
        words_string = ';'.join(drawn_words)
        return words_string
