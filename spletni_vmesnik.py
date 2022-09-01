from bottle import *
from model import *

UPORABNISKOIMENSKI_PISKOT = "halidbeslic"
SIFRIRNI_KLJUC = "Še vedno smo v aprilu."

def current_user():
    uname = request.get_cookie(
        UPORABNISKOIMENSKI_PISKOT, secret=SIFRIRNI_KLJUC)
    if uname:
        return Uporabnik.nalozi_uporabnika(uname)
    else:
        return None


@get('/')
def osnovna_stran():
    return template('osnovna_stran.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse())


@get('/statistika/')
def statistika():
    return template('statistika.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse())


@post("/registracija/")
def registracija_post():
    uporabnisko_ime = request.forms.getunicode("uname")
    geslo = request.forms.getunicode("pass")
    geslo_kopija = request.forms.getunicode("pass_conf")

    if len(uporabnisko_ime) == 0:
        return template("registracija.html", error='manjka_ime')

    if len(geslo) == 0 or len(geslo_kopija) == 0:
        return template("registracija.html", error='manjka_geslo')

    if geslo != geslo_kopija:
        return template("registracija.html", error='neenako_geslo')

    if len(geslo) < 8:
        return template("registracija.html", error='slabo_geslo')

    try:
        Uporabnik.registracija(uporabnisko_ime, geslo)
        response.set_cookie(
            UPORABNISKOIMENSKI_PISKOT, uporabnisko_ime, path="/", secret=SIFRIRNI_KLJUC
        )
        redirect("/")
    except ValueError:
        print("napaka")
        return template("registracija.html", error='zaseden')


@get('/registracija/')
def registracija_get():
    return template('registracija.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse())


@post("/prijava/")
def prijava_post():
    uporabnisko_ime = request.forms.getunicode("uname")
    geslo = request.forms.getunicode("pass")

    if len(uporabnisko_ime) == 0:
        return template("prijava.html", error='manjka_ime')

    if len(geslo) == 0:
        return template("prijava.html", error='manjka_geslo')

    try:
        Uporabnik.prijava(uporabnisko_ime, geslo)
        response.set_cookie(
            UPORABNISKOIMENSKI_PISKOT, uporabnisko_ime, path="/", secret=SIFRIRNI_KLJUC
        )
        redirect("/")
    except ValueError:
        return template("prijava.html", error='napacni_podatki')


@get('/prijava/')
def prijava_get():
    return template('prijava.html', evrovizije=Evrovizija.poisci_vse())


@get('/odjava/')
def odjava():
    response.delete_cookie(UPORABNISKOIMENSKI_PISKOT, path="/")
    redirect("/")


@get('/glasovanje/<ime>/')
def glasovanje_get(ime):
    uporabnik = current_user()
    print(ime)
    if uporabnik == None:
        abort(403, "Hopla, za to stran pa nimate dostopa.")
    try:
        return template('glasovanje.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse(), trenutna_evrovizija=Evrovizija.odpri_po_sifri(ime))
    except ValueError:
        abort(404, "Napacen URL")


@post('/glasovanje/<ime>/')
def glasovanje_post(ime):
    uporabnik = current_user()
    evrovizija = Evrovizija.odpri_po_sifri(ime)
    drzava = request.forms.get('ime_drzave')
    tocke = request.forms.get(f"tocke_{drzava}")
    print(f"tocke_{drzava}")
    print(tocke)
    if uporabnik == None:
        abort(403, "Hopla, za to stran pa nimate dostopa.")
    try:
        uporabnik.dodaj_oceno(evrovizija.ime, drzava, tocke)
        return template('glasovanje.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse(), trenutna_evrovizija=Evrovizija.odpri_po_sifri(ime))
    except ValueError:
        abort(404, "Napacen URL")


@get('/glasovanje/<ime>/prijava_ziranta')
def glasovanje_get_prijava1(ime):
    uporabnik = current_user()
    trenutna_evrovizija = Evrovizija.odpri_po_sifri(ime)
    if uporabnik == None:
        abort(403, "Hopla, za to stran pa nimate dostopa.")
    uporabnik.dodaj_dostop(trenutna_evrovizija.ime, 1)
    redirect(f'/glasovanje/{trenutna_evrovizija.hash}/')


@get('/glasovanje/<ime>/prijava_publike')
def glasovanje_get_prijava2(ime):
    uporabnik = current_user()
    trenutna_evrovizija = Evrovizija.odpri_po_sifri(ime)
    if uporabnik == None:
        abort(403, "Hopla, za to stran pa nimate dostopa.")
    uporabnik.dodaj_dostop(trenutna_evrovizija.ime, 2)
    redirect(f'/glasovanje/{trenutna_evrovizija.hash}/')


@get('/administracija/')
def admin_get():
    uporabnik = current_user()
    if uporabnik == None or uporabnik.ime != 'admin':
        abort(403, "Hopla, za to stran pa nimate dostopa.")
    return template('admin.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse())


@post('/administracija/')
def admin_post():
    uporabnik = current_user()
    if uporabnik == None or uporabnik.ime != 'admin':
        abort(403, "Hopla, za to stran pa nimate dostopa.")
    if 'ime_evrovizije' in request.forms:
        novo_ime = request.forms.get('ime_evrovizije')
        for e in Evrovizija.poisci_vse():
            if e.ime == novo_ime:
                return template('admin.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse(), error='evrovizija')
        evrovizija = Evrovizija(novo_ime, [])
        evrovizija.shrani()
        return template('admin.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse(), success='evrovizija')

    elif 'pesem' in request.forms:
        print("nova pesem")
        ime_evrovizije = request.forms.get("evrovizija")
        drzava = request.forms.get("drzava")
        izvajalec = request.forms.get("izvajalec")
        pesem = request.forms.get("pesem")
        evrovizija = Evrovizija.odpri_po_imenu(ime_evrovizije)
        for d in evrovizija.drzave:
            if d.ime == drzava:
                return template('admin.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse(), error='drzava')
        evrovizija.dodaj_drzavo(Drzava(drzava, izvajalec, pesem))
        evrovizija.shrani()
        return template('admin.html', uporabnik=current_user(), evrovizije=Evrovizija.poisci_vse(), success='drzava')


@route('/static/<filename:path>', name='static')
def serve_static(filename):
    return static_file(filename, root='static')


run(debug=True, reloader=True)
