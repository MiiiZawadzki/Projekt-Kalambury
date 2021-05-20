words = [
    "Stół z powyłamywanymi nogami",
    "Gdzie dwóch się bije, tam trzeci korzysta",
    "Nie ma róży bez kolców",
    "Budować zamki na piasku",
    "W marcu jak w garncu",
    "Co za dużo, to niezdrowo",
    "Gdy się człowiek spieszy, to się diabeł cieszy",
    "Idzie luty, podkuj buty",
    "Każdy kij ma dwa końce",
    "Mieć dwie lewe ręce",
    "Nie chwal dnia przed zachodem słońca",
    "Przyszła koza do woza",
    "Przyganiał kocioł garnkowi, a sam smoli",
    "Jedna jaskółka wiosny nie czyni",
    "Raz na wozie, raz pod wozem",
    "Ręka rękę myje",
    "Słuchaj uchem, a nie brzuchem",
    "Gość w dom, Bóg w dom",
    "Nie wywołuj wilka z lasu",
    "Czuć się jak ryba w wodzie",
    "Nie czyń drugiemu, co tobie niemiłe",
    "Nauka nie poszła w las",
    "Strach ma wielkie oczy",
    "Tonący brzytwy się chwyta",
    "W zdrowym ciele zdrowy duch",
    "Z deszczu pod rynnę",
    "Jak kamień w wodę",
    "Im mniej wiesz, tym spokojniej śpisz",
    "Szewc bez butów chodzi",
    "Lepszy rydz niż nic",
    "Kombinuje jak koń pod górę",
    "Co dwie głowy, to nie jedna",
    "Krowa, która dużo ryczy, mało mleka daje",
    "Z dużej chmury mały deszcz",
    "Żeby kózka nie skakała, toby nóżki nie złamała",
    "Ładnemu we wszystkim ładnie",
    "Nie udawaj Greka",
    "Czas to pieniądz",
    "Lepiej dmuchać na zimne",
    "Trafiło się ślepej kurze ziarno",
    "Apetyt rośnie w miarę jedzenia",
    "Jeśli wejdziesz między wrony, musisz krakać jak i one",
    "Jajko mądrzejsze od kury",
    "Zamienił stryjek siekierkę na kijek",
    "Baba z wozu - koniom lżej",
    "Cicha woda brzegi rwie",
    "Darowanemu koniowi nie zagląda się w zęby",
    "Fortuna kołem się toczy",
    "Kłamstwo ma krótkie nogi",
    "Lepiej późno niż wcale",
    "Na bezrybiu i rak ryba",
    "Lepszy wróbel w garści niż gołąb na dachu",
    "Na dwoje babka wróżyła",
    "Pieniądze szczęścia nie dają",
    "Nie dla psa kiełbasa",
    "Pańskie oko konia tuczy",
    "Nie pchaj palca między drzwi",
    "Pierwsze koty za płoty",
    "Nie święci garnki lepią",
    "Dzieci i ryby głosu nie mają",
    "Trafiła kosa na kamień",
    "Uderz w stół, a nożyce sie odezwą",
    "Wyszło szydło z worka",
    "Robić z igły widły",
    "Szczęśliwi czasu nie liczą",
    "Burza w szklance wody",

]

from random import randint

def get_words_string(quantity):
    if quantity > len(words):
        raise ValueError()
    else:
        words_list = words[:]
        drawn_words = []
        for i in range(quantity):
            index = randint(0, len(words_list) - 1)
            drawn_words.append(words_list[index])
            words_list.pop(index)
        words_string = ';'.join(drawn_words)
        return words_string
