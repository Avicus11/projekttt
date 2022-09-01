from multiprocessing.sharedctypes import Value
import os
import json
from hasher import *
from pkg_resources import IMetadataProvider

#sledeč seznam dobim iz printer.py:
zastavice = ['albanija.png', 'armenija.png', 'avstralija.png', 'avstrija.png', 'azerbaijan.png', 'b.jpg', 'belgija.png', 
'belorusija.png', 'bolgarija.png', 'bosnainhercegovina.png', 'ceskarepublika.png', 'crnagora.png', 'danska.png', 
'estonija.png', 'finska.png', 'francija.png', 'grcija.png', 'hrvaska.png', 'irska.png', 
'islandija.png', 'izrael.png', 'italija.png', 'jugoslavija.png', 'latvija.png', 'litva.png', 'luksemburg.png', 
'madzarska.png', 'malta.png', 'moldavija.png', 'monako.png', 'nemcija.png', 'nizozemska.png', 'norveska.png', 
'poljska.png', 'portugalska.png', 'romunija.png', 'rusija.webp', 'sanmarino.png', 'severnamakedonija.png', 'slovaska.png', 
'slovenija.png', 'spanija.png', 'ciper.png', 'gruzija.png',
'srbija.png', 'svedska.png', 'svica.png', 'turcija.png', 'ukrajina.png', 'velikabritanija.png']

class Drzava:
    def __init__(self, ime, izvajalec, pesem):
        self.ime = ime
        self.izvajalec = izvajalec
        self.pesem = pesem
        self.tocke_zirantov = 0
        self.tocke_publike = 0
        self.tocke = 0
        self.indeks = 0 if ''.join(self.ime.lower().split()) + '.png' not in zastavice else 1
        self.zastava = ''.join(self.ime.lower().split()) + '.png' if self.indeks == 1 else "b.jpg"


    def prestej_tocke(self, ime_evrovizije: str):
        uporabniki = Uporabnik.najdi_vse_uporabnike()
        for user in uporabniki:
            for dost in filter(lambda x: x.ime == ime_evrovizije, user.dostop):
                print(dost)
                for ocena in filter(lambda x: x.drzava == self.ime and x.evrovizija == ime_evrovizije, user.ocene):
                    print(ocena.ocena)
                    if dost.status == 1:
                        self.tocke_zirantov += int(ocena.ocena)
                    elif dost.status == 2:
                        self.tocke_publike += int(ocena.ocena)
                    self.tocke += int(ocena.ocena)

    def pretvori_v_dict(self):
        dic = {}
        print(type(dic))
        dic["ime"] = self.ime
        dic["izvajalec"] = self.izvajalec
        dic["pesem"] = self.pesem
        return dic

    def pretvori_iz_dict(dict):
        return Drzava(
            ime=dict["ime"],
            izvajalec=dict["izvajalec"],
            pesem=dict["pesem"]
        )


class Dostop():
    def __init__(self, ime, status):
        self.ime = ime
        self.status = status

    def __str__(self):
        return f"{self.ime} {self.status}"

    def pretvori_v_dict(self):
        d = {}
        d["ime"] = self.ime
        d["status"] = self.status
        return d

    def pretvori_iz_dict(d):
        return Dostop(d["ime"], d["status"])


class Ocena():
    def __init__(self, evrovizija: str, drzava: str, ocena: int):
        self.evrovizija = evrovizija
        self.drzava = drzava
        self.ocena = ocena

    def pretvori_v_dict(self):
        d = {}
        d["evrovizija"] = self.evrovizija
        d["drzava"] = self.drzava
        d["ocena"] = self.ocena
        return d

    def pretvori_iz_dict(d):
        return Ocena(d["evrovizija"], d["drzava"], d["ocena"])


class Uporabnik():

    def __init__(self, ime, geslo, dostop, ocene):
        self.ime = ime
        self.geslo = geslo
        self.dostop = dostop
        self.ocene = ocene

    def prijava(uname, geslo):
        filepath = f"uporabniki/{uname}.json"
        if(not(os.path.exists(filepath))):
            raise ValueError
        with open(filepath, "r") as f:
            dict = json.load(f)
        f.close()
        print(dict["pass"])
        print(zakodiraj(geslo))
        print(geslo)
        if dict["pass"] == zakodiraj(geslo):
            return True
        else:
            raise ValueError

    def pretvori_v_dict(self) -> dict:
        d = {}
        d["user"] = self.ime
        d["pass"] = self.geslo
        d["access"] = []
        d["scores"] = []
        for dos in self.dostop:
            d["access"].append(dos.pretvori_v_dict())

        for oc in self.ocene:
            d["scores"].append(oc.pretvori_v_dict())

        return d

    def pretvori_iz_dict(d):
        return Uporabnik(
            d["user"],
            d["pass"],
            list(map(Dostop.pretvori_iz_dict, d["access"])),
            list(map(Ocena.pretvori_iz_dict, d["scores"])),
        )

    def registracija(uname, password):
        filepath = f"uporabniki/{uname}.json"
        if(os.path.exists(filepath)):
            raise ValueError
        with open(filepath, "w") as f:
            nov_uporabnik = Uporabnik(uname, zakodiraj(password), [], [])
            json.dump(nov_uporabnik.pretvori_v_dict(), f)
        f.close()

    def shrani(self):
        filepath = f"uporabniki/{self.ime}.json"
        print(self.dostop)
        with open(filepath, "w") as f:
            json.dump(self.pretvori_v_dict(), f)
        f.close()

    def nalozi_uporabnika_iz_path(filepath):
        if(not(os.path.exists(filepath))):
            raise ValueError
        with open(filepath, "r") as f:
            dict = json.load(f)
        f.close()
        return Uporabnik.pretvori_iz_dict(dict)

    def nalozi_uporabnika(uname):
        filepath = f"uporabniki/{uname}.json"
        return Uporabnik.nalozi_uporabnika_iz_path(filepath)

    def preveri_dostop(self, ime_evrovizije: str):
        for i in self.dostop:
            if i.ime == ime_evrovizije:
                return i.status
        return 0

    def dodaj_dostop(self, ime_evrovizije: str, status):
        self.dostop.append(Dostop(ime_evrovizije, status))
        print(self.dostop[0])
        self.shrani()

    def obstaja_ocena(self, evrovizija, drzava):
        for o in self.ocene:
            if o.drzava == drzava and o.evrovizija == evrovizija:
                return o.ocena
        return -1

    def dodaj_oceno(self, evrovizija: str, drzava: str, ocena: int):
        # Poglej ali ocena ze obstaja
        for o in self.ocene:
            if o.drzava == drzava and o.evrovizija == evrovizija:
                o.ocena = ocena
                self.shrani()
                return

        self.ocene.append(Ocena(evrovizija, drzava, ocena))
        self.shrani()

    def najdi_vse_uporabnike():
        L = []
        for file in os.listdir("uporabniki/"):
            f = os.path.join("uporabniki/", file)
            L.append(Uporabnik.nalozi_uporabnika_iz_path(f))
        return L


class Evrovizija:
    def __init__(self, ime, drzave):
        self.ime = ime
        self.drzave = drzave
        self.drzave.sort(key=lambda x: x.ime, reverse=False)

        self.drzave_po_tockah = drzave[:]
        for d in self.drzave_po_tockah:
            d.prestej_tocke(self.ime)
        self.drzave_po_tockah.sort(key=lambda x: x.tocke, reverse=True)

        self.hash = zakodiraj(ime)

    def dodaj_drzavo(self, drzava):
        self.drzave.append(drzava)

    def dodaj_ziranta(self, zirant):
        sez = []
        for drzava, tocke in zirant.tocke.items():
            sez.append([drzava.ime, tocke])
        self.ziranti.append([zirant.ime, sez, zirant])

    def dodaj_public_voterji(self, public_voter):
        sez = []
        for drzava, tocke in public_voter.tocke.items():
            sez.append([drzava.ime, tocke])
        self.public_voterji.append([public_voter.ime, sez, public_voter])

    def posodobi_mesta(self):
        sez = []
        for element in self.drzave:
            sez.append((- element[0], element[1]))
        sez.sort()
        # zdaj mamo [(-180, Švedska), (-170, Velika_Britanija), (-100, Španija)]
        self.drzave = []
        for j in range(len(sez)):
            self.drzave.append([-sez[j][0], sez[j][1], j + 1])

    def pretvori_v_dict(self):
        dict = {}
        dict["ime"] = self.ime
        dict["drzave"] = []
        for drzava in self.drzave:
            print(type(drzava))
            dict["drzave"].append(drzava.pretvori_v_dict())
        return dict

    def pretvori_iz_dict(dict):
        return Evrovizija(dict["ime"], list(map(Drzava.pretvori_iz_dict, dict["drzave"])))

    def shrani(self):
        filepath = f"evrovizije/{self.hash}.json"
        zaznamek = self.pretvori_v_dict()
        with open(filepath, "w") as f:
            json.dump(zaznamek, f)
        f.close()

    def odpri(filepath):
        with open(filepath, "r") as f:
            return Evrovizija.pretvori_iz_dict(json.load(f))

    def odpri_po_imenu(ime):
        return Evrovizija.odpri_po_sifri(zakodiraj(ime))

    def odpri_po_sifri(sifra):
        filepath = f"evrovizije/{sifra}.json"
        print(filepath)
        if not(os.path.exists(filepath)):
            raise ValueError
        return Evrovizija.odpri(filepath)

    def poisci_vse():
        L = []
        for file in os.listdir("evrovizije/"):
            f = os.path.join("evrovizije/", file)
            L.append(Evrovizija.odpri(f))

        # posortiraj
        L.sort(key=lambda x: x.ime, reverse=False)
        return L

    def oceni_vse_drzave():
        pass
