# -*- coding: utf-8 -*-
import struct 
import mmap
import numpy as np
import os

class InvalidFormatError(IOError):
    pass


def load_data(filename):

    """

    Funkcja ładuje dane z pliku binarnego. Plik ma następującą strukturę:

    * Nagłówek
    * Następnie struktury z danymi

    Nagłówek ma następującą strukturę:

    0. 16 "magicznych" bajtów te bajty to b'6o\xfdo\xe2\xa4C\x90\x98\xb2t!\xbeurn'
    1. 2 bajty wersji "głównej"
    2. 2 bajty wersji "pomniejszej"
    3. 2 bajty określające rozmiar pojedyńczej struktury danych
    4. 4 bajty określających ilość struktur
    5. 4 bajty określających offset między początkiem pliku a danymi
    6. Następnie mamy tyle struktur ile jest określone w nagłówku

    Struktura danych ma taką postać:

    * event_id: uint16 numer zdarzenia
    * particle_position: 3*float32 we współrzędnych kartezjańskich [m]
    * particle mass: float32 współrzędne kartezjańskie [kg]
    * particle_velocity: 3*float32 współrzędne kartezjańskie [m/s]

    Struktura i nagłówek nie mają paddingu i są zapisani little-endian!

    Ten format pliku jest kompatybilny wstecznie i do przodu w ramach wersji
    "pomniejszej". W następujący sposób:

    * Jeśli potrzebuję dodać jakieś nowe pola do nagłówka to je dodaję,
      i odpowiednio modyfikuję offset między początkiem pliku a danymi.
      Program czytający te pliki który nie jest przystosowany do pracy ze
      starszą wersją może te pola zignorować.
    * Jeśli chce dodać jakieś pola do struktury z danymi to zwiększam pole rozmiar
      jednej struktury danych i dodaje pola. Dane są dodawane do końca struktury,
      więc program czytający dane będzie wiedział że następna struktura zaczyna
      się np. 82 bajty od początku poprzedniej.

    Funkcja ta musi zgłosić wyjątek InvalidLoadError w następujących przypadkach:

    * W pliku nie zgadzają się magiczne bajty
    * Główna wersja pliku nie równa się 3
    * Rozmiar pliku jest nieodpowiedni. Tj rozmiar pliku nie wynosi:
      "offset między początkiem pliku a danymi" + "ilość struktur" * "rozmiar pojedyńczej struktury danych"


    Rada:

    * Proszę załadować nagłówek za pomocą modułu ``struct``  odczytać go,
      a następnie załadować resztę pliku (offset! za pomocą ``np.memmap``).

    Funkcja zwraca zawartość pliku w dowolnym formacie. Testy tego zadania będą
    sprawdzać czy funkcja zgłasza błędy dla niepoprawnych plików.

    W zadaniu 3 będziecie na tym pliku robić obliczenia.
    """
    #sprawdzenie rozmiaru magicznych bajtow i naglowka
    statinfo = os.stat(filename)
    if statinfo.st_size < 30:
        raise InvalidFormatError
    
    #odczytanie magicznych bajtow i naglowka
    s = struct.Struct("<16s3H2I") #little endian, 16 char, 3 unsigned short, 2 unsigned int
    with open(filename, 'rb') as f:
        data = mmap.mmap(f.fileno(), 30, mmap.MAP_SHARED, mmap.PROT_READ)
    h = s.unpack(data)
    mbytes, ver1, ver2, size, number, offset = h
    
    #zglaszanie bledu
    if mbytes != b'6o\xfdo\xe2\xa4C\x90\x98\xb2t!\xbeurn' or ver1 != 3 or statinfo.st_size != offset + number*size:
        raise InvalidFormatError
    
    #definiowanie struktury danych
    dtype = np.dtype([
    ("event_id", 'uint16'),
    ("particle_position", '3float32'),
    ("particle_mass", 'float32'),
    ('particle_velocity', '3float32'),
    ('empty', 'a98')]) #padding = size-30 = 98
    
    #załadowanie reszty pliku
    return np.memmap(filename, dtype, offset = offset)
    
