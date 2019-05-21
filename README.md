# 2D Persistent Homology visualizer

Za dati skup nasumično generisanih tačaka u Euklidskoj ravni izračunava
homologiju stepena 0, koja opisuje povezanost tačaka, i homologiju stepena 1 koja detektuje rupe.

Sa leve strane prikazan je Viretoris-Rips complex koji se dobija za zadati parametar epsilon.

Sa desne strane prikazan je generisan Barcode koje predstavlja diagram perzistencije gde je za svako epislon prikazan trenutak 'radjanja' i 'umiranja' komponente.

![persistence](screenshots/1.png)

### Plan projekta

Projekat je napravljen u programskom jeziku Python (3.7). Korišćene biblioteke:
* [dionysus2](https://mrzv.org/software/dionysus2/) - od [Dmitriy Morozov](https://www.mrzv.org/). Za konstruisanje Vietoris–Rips Complexe-a od datog skupa tačaka, računanje persistentne homologije i generisanje diagrama persistencije.
* [PyQt5](https://pypi.org/project/PyQt5/) - crtanje GUI-a
* [matplotlib](https://matplotlib.org/) - iscrtavanje Vietoris-Rips Complex i dijagrama persistencije
* [numpy](https://www.numpy.org/) - reprezentacija i generisanje tačaka
* [shapely](https://pypi.org/project/Shapely/) - popunjavanje i konstruisanje poligona za iscrtavanje


### Instalacija:

Program je kompatibilan za operativim sistemom Ubuntu bilo koje verzije
na kojoj mogu biti instalirane dole navedene biblioteke.
#### Ubuntu:
Instalirati python3:

`sudo apt-get install python3 python3-pip`

Biblioteka dionysus koristi C++ biblioteku boost. Instalirati boost pokretanjem:

`sudo apt-get install libboost-all-dev`

Zatim instalirati potrebne python pakete pokretanjem:

`pip3 install shapely PyQt5 matplotlib dionysus qdarkstyle`

### Pokretanje:

#### Ubuntu:
Kao python script:

`cd project/folder`

`python PHV.py`

Kao izvršivi fajl:

`cd project/folder/release`

`./PHVlin`

### Autori:
Kristina Popović (mi16058@alas.math.rs)

Marko Spasić (mi16165@alas.math.rs) 