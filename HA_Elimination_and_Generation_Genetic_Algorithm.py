import os
import random


"""""""""Kreiramo metodu koja prima putanju do .tim datoteke te vraća rječnik  """""""""""""""""""""
def read_tim_file(file_path):
    data = {}
    with open(file_path, 'r', errors='replace') as file:
        # iz prvog reda iščitamo broj predavanja, učionica, svojstava, studenata
        metadata = list(map(int, file.readline().strip().split()))
        num_events, num_rooms, num_features, num_students = metadata   
        
        
        data['num_events'] = num_events
        data['num_rooms'] = num_rooms
        data['num_features'] = num_features
        data['num_students'] = num_students

        # iščitavamo kapacitet učionica
        data['room_capacities'] = [int(file.readline().strip()) for _ in range(num_rooms)]   
        

        # za svakog studenta i svako predavanje iščitavamo sluša li taj student to predavanje
        data['student_event'] = []
        for _ in range(num_students*num_events):
            enrolled_students = map(int, file.readline().strip().split())
            data['student_event'].extend(enrolled_students)

        # za svaku učionicu i svako svojstvo iščitavami ima li ta učionica to svojstvo
        data['room_feature'] = []
        for _ in range(num_rooms*num_features):
            features = map(int, file.readline().strip().split())
            data['room_feature'].extend(features) 

        # za svako predavanje i svako svojstvo iščitavamo zahtjeva li to predavanje to svojstvo
        data['event_feature'] = []
        for _ in range(num_features*num_events):
            requirements = map(int, file.readline().strip().split())
            data['event_feature'].extend(requirements)
            
        # za svako predavanje i svaki termin iščitavamo može li se to predavanje održati u tom terminu
        data['event_timeslot'] =[]
        for _ in range(45*num_events):
            timeslots = map(int, file.readline().strip().split())
            data['event_timeslot'].extend(timeslots)

        #za svaka 2 predavanja provjeravamo u kakvom su odnosu(tj. treba li se neko predavanje održati prije/poslje tog drugog)
        data['event_event'] = []
        while True:
            line = file.readline().strip()
            if not line:  # Provjerava kraj datoteke ili blok s podacima
                break
            ordering = map(int, line.split())
            data['event_event'].extend(ordering)
        

    return data  #metoda vraća riječnik




"""""""""""""""""Metoda koja provjerava je li raspored dopustiv"""""""""""""""

def provjera_dopustivosti(raspored, podaci):
    dopustivo = True
    ############ Provjera ima li neki student preklapanje predavanja:
        
    # Kreiramo rječnik u kojem su ključevi termini, a vrijednosti svi predmeti koji se održavaju u tim terminima.
    predavanje_vrijeme = {}
    for i in range(len(raspored)):
        if raspored[i][0] not in predavanje_vrijeme:
            predavanje_vrijeme[raspored[i][0]] = []
        predavanje_vrijeme[raspored[i][0]].append(i)
    
    # Sada za svaka dva predavanja u istom intervalu potrebno provjeriti postoje li studenti koji slušaju oba:
    for vrijeme, predavanja in predavanje_vrijeme.items():
        for a in range(len(predavanja) - 1):
            for b in range(a + 1, len(predavanja)):
                for student in range(podaci['num_students']):
                    predavanje_a = predavanja[a]
                    predavanje_b = predavanja[b]
                    if (podaci['student_event'][student * podaci['num_events'] + predavanje_a] == 1 and 
                        podaci['student_event'][student * podaci['num_events'] + predavanje_b] == 1):
                        #print(f'Student {student+1} ima preklapanje između predavanja {predavanje_a+1} i {predavanje_b+1}.')
                        dopustivo=False

    ############# Provjera je li učionica dovoljno velika:
    for i in range(len(raspored)):
        kapacitet_ucionice = podaci['room_capacities'][raspored[i][1]]
        br_ucenika_na_predavanju = 0
        for k in range(podaci['num_students']):
            br_ucenika_na_predavanju += podaci['student_event'][k * podaci['num_events'] + i]
        if br_ucenika_na_predavanju > kapacitet_ucionice:
            #print(f'Na predavanju {i+1} je više učenika nego što je mjesta u učionici {raspored[i][1]+1}')
            dopustivo= False

    ############# Provjera jesu li 2 predavanja u istom intervalu raspoređena u istoj učionici:
    for vrijeme, predavanja in predavanje_vrijeme.items():
        for a in range(len(predavanja) - 1):
            for b in range(a + 1, len(predavanja)):
                if raspored[predavanja[a]][1] == raspored[predavanja[b]][1] and raspored[predavanja[a]][1]!=-1:
                    #print(f'Predavanja {predavanja[a]+1} i {predavanja[b]+1} održavaju se u istoj učionici {raspored[predavanja[a]][1]+1} u istom terminu {vrijeme+1}')
                    dopustivo= False

    ########### Provjera jesu li sva predavanja raspoređena u unaprijed predviđene intervale za njih:
    for i in range(len(raspored)):
        interval = raspored[i][0]
        if interval != -1 and podaci['event_timeslot'][i * 45 + interval] == 0:
            #print(f'Predavanje {i+1} nije raspoređeno u jedan od predviđenih intervala.')
            dopustivo= False

    ########### Provjeriti jesu li određena predavanja iza nekog drugog, kako je zahtjevano:
    for indeks, vrijednost in enumerate(podaci['event_event']):
        redak = indeks // podaci['num_events']
        stupac = indeks % podaci['num_events']
        
        if vrijednost == 1:
            if raspored[redak][0] >= raspored[stupac][0]:
                #print(f'Predavanje {redak+1} treba biti prije predavanja {stupac+1}!')
                dopustivo= False
    

    ########### Provjera 6: Sva predavanja su raspoređena (nijedan događaj nema (-1, -1))
    for i, (timeslot, room) in enumerate(raspored):
        if timeslot == -1 or room == -1:
            #print(f'Predavanje {i+1} nije raspoređeno.')
            dopustivo = False

    # Ispisujemo je li raspored dopustiv
    if dopustivo:
        print("Raspored je dopustiv!")
    else:
        print("Raspored nije dopustiv.")

    return dopustivo  # Vraća True ako je dopustiv, False ako nije



def ucitaj_raspored(file_path):
    raspored = []
    with open(file_path, 'r') as file:
        for line in file:
            timeslot, room = map(int, line.strip().split())
            raspored.append((timeslot, room))
    return raspored



"""""""""""""""""""Kreirajmo valjan raspored:"""""""""""""""""""""""""

def kreiraj_valjan_raspored(sln_file_path, podaci):
    raspored = ucitaj_raspored(sln_file_path)
    ############ Provjera ima li neki student preklapanje predavanja:
    predavanje_vrijeme = {}
    for i in range(len(raspored)):
        if raspored[i][0] not in predavanje_vrijeme:
            predavanje_vrijeme[raspored[i][0]] = []
        predavanje_vrijeme[raspored[i][0]].append(i)

    for vrijeme, predavanja in predavanje_vrijeme.items():
        for a in range(len(predavanja) - 1):
            for b in range(a + 1, len(predavanja)):
                for student in range(podaci['num_students']):
                    predavanje_a = predavanja[a]
                    predavanje_b = predavanja[b]
                    if (podaci['student_event'][student * podaci['num_events'] + predavanje_a] == 1 and 
                        podaci['student_event'][student * podaci['num_events'] + predavanje_b] == 1):
                        #print(f'Student {student+1} ima preklapanje između predavanja {predavanje_a+1} i {predavanje_b+1}!')
                        raspored[predavanje_a] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo
                        raspored[predavanje_b] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo
                       

    ############# Provjera je li učionica dovoljno velika:
    for i in range(len(raspored)):
        if raspored[i][1] == -1:
            continue  # Ako je već dodijeljeno -1, -1, preskoči

        kapacitet_ucionice = podaci['room_capacities'][raspored[i][1]]
        br_ucenika_na_predavanju = 0
        for k in range(podaci['num_students']):
            br_ucenika_na_predavanju += podaci['student_event'][k * podaci['num_events'] + i]
        
        if br_ucenika_na_predavanju > kapacitet_ucionice:
            #print(f'Na predavanju {i+1} je više učenika nego što je mjesta u učionici {raspored[i][1]+1}')
            raspored[i] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo
            

    ############# Provjera jesu li 2 predavanja u istom intervalu raspoređena u istoj učionici:
    for vrijeme, predavanja in predavanje_vrijeme.items():
        for a in range(len(predavanja) - 1):
            for b in range(a + 1, len(predavanja)):
                if raspored[predavanja[a]][1] == raspored[predavanja[b]][1] and raspored[predavanja[a]][1] != -1:
                    #print(f'Predavanja {predavanja[a]+1} i {predavanja[b]+1} održavaju se u istoj učionici {raspored[predavanja[a]][1]+1} u istom terminu {vrijeme+1}')
                    raspored[predavanja[a]] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo
                    raspored[predavanja[b]] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo
                    

    ########### Provjera jesu li sva predavanja raspoređena u unaprijed predviđene intervale za njih:
    for i in range(len(raspored)):
        interval = raspored[i][0]
        if interval != -1 and podaci['event_timeslot'][i * 45 + interval] == 0:
            #print(f'Predavanje {i+1} nije raspoređeno u jedan od predviđenih intervala.')
            raspored[i] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo
            

    ########### Provjeriti jesu li određena predavanja iza nekog drugog, kako je zahtjevano:
    for indeks, vrijednost in enumerate(podaci['event_event']):
        redak = indeks // podaci['num_events']
        stupac = indeks % podaci['num_events']
        
        if vrijednost == 1:
            if raspored[redak][0] >= raspored[stupac][0]:
                #print(f'Predavanje {redak+1} treba biti prije predavanja {stupac+1}!')
                raspored[redak] = (-1, -1)  # Dodijeli -1, -1 predavanju koje nije dopustivo


    ############ Zapisivanje izmijenjenog rasporeda u datoteku:
    with open(sln_file_path, 'w') as file:
        for predavanje in raspored:
            file.write(f"{predavanje[0]} {predavanje[1]}\n")  # Zapisuje svaki red s timeslotom i učionicom

    #print("Izmijenjeni (valjani) raspored je zapisan u datoteku.")
    
    


"""""""""Evaluacija dobivenog rješenja"""""""""""

def generiraj_raspored_ucionica(sln_file_path, output_file_path):
    # Inicijaliziraj rječnik za pohranu rasporeda po učionicama
    raspored_po_ucionicama = {}

    # Čitanje rasporeda iz datoteke i punjenje strukture podataka
    with open(sln_file_path, 'r') as file:
        for i, line in enumerate(file):
            termin, ucionica = map(int, line.split())
            
            # Dodavanje učionice u rječnik ako ne postoji
            if ucionica not in raspored_po_ucionicama:
                raspored_po_ucionicama[ucionica] = []

            # Dodavanje parova (termin, događaj) za učionicu
            raspored_po_ucionicama[ucionica].append((termin, i + 1))

    # Generiranje izlazne datoteke s prikazom rasporeda po učionicama
    with open(output_file_path, 'w') as output_file:
        for ucionica, dogadjaji in raspored_po_ucionicama.items():
            if ucionica != -1:
                # Zaglavlje za svaku učionicu
                output_file.write(f'Učionica {ucionica}\n')
                output_file.write("      PON    UTO    SRI    ČET    PET\n")

                # Kreiranje matrice za prikaz rasporeda
                matrica = [["  -  "] * 5 for _ in range(9)]  # 9 termina x 5 dana

                # Popunjavanje matrice prema terminima događaja
                for termin, dogadjaj in dogadjaji:
                    dan = termin % 5  # Računanje dana (pon=0, uto=1, ..., pet=4)
                    termin_broj = termin // 5  # Računanje indeksa termina (0-8)
                    matrica[termin_broj][dan] = f"{dogadjaj:5}"  # Upis broja događaja s poravnanjem

                # Pisanje matrice u datoteku
                for i, red in enumerate(matrica):
                    output_file.write(f"{i:<2}   " + "  ".join(f"{celija:>5}" for celija in red) + "\n")
                output_file.write("\n")

    print(f'Izlazni raspored zapisan u {output_file_path}')



def udaljenost_do_dopustivosti(sln_file_path, podaci):
    brojac = 0  # Brojač studenata na predavanjima koja nisu dopustiva

    # Učitaj raspored iz datoteke
    with open(sln_file_path, 'r') as file:
        for i, line in enumerate(file):
            termin, ucionica = map(int, line.split())

            # Provjera je li predavanju pridruženo (-1, -1)
            if termin == -1 and ucionica == -1:
                # Broji broj studenata koji pohađaju ovo predavanje
                broj_studenata_na_predavanju = sum(
                    podaci['student_event'][student * podaci['num_events'] + i]
                    for student in range(podaci['num_students'])
                )
                # Dodaj broj studenata s ovog predavanja u brojač
                brojac += broj_studenata_na_predavanju

    return brojac



def trosak_narusavanja_mekih_uvjeta(putanja_do_rasporeda, podaci):
    trosak_jedno_predavanje = 0
    trosak_uzastopna_predavanja = 0
    trosak_zadnji_interval = 0

    num_students = podaci['num_students']
    num_events = podaci['num_events']

    # Inicijalizacija rasporeda
    raspored = []

    # Učitavanje rasporeda iz datoteke
    with open(putanja_do_rasporeda, 'r') as file:
        for line in file:
            termin, _ = map(int, line.split())  # Razdvajanje termina i učionice
            raspored.append(termin)

    # Iteracija kroz studente
    for student in range(num_students):
        predavanja_po_danu = [[] for _ in range(5)]  # Predavanja po danima (PON, UTO, SRI, ČET, PET)

        # Popunjavamo predavanja po danu za svakog studenta
        for event in range(num_events):
            termin = raspored[event]  # Preuzimamo termin za događaj
            if podaci['student_event'][student * num_events + event] == 1 and termin != -1:  # Provjera da li student ima predavanje
                dan = termin % 5  # Računanje dana (0 = pon, 1 = uto, ..., 4 = pet)
                termin_broj = termin // 5  # Računanje indeksa termina (0-8)
                predavanja_po_danu[dan].append(termin_broj)  # Dodavanje predavanja za odgovarajući dan

        # Izračun troškova po danu
        for predavanja_u_danu in predavanja_po_danu:
            predavanja_u_danu.sort()  # Sortiraj predavanja po terminima

            # Provjera troška za jedno predavanje u danu
            if len(predavanja_u_danu) == 1:
                trosak_jedno_predavanje += 1  # Jedno predavanje u danu povećava trošak

            # Provjera troška za uzastopna predavanja unutar istog dana
            # Provjera troška za uzastopna predavanja unutar istog dana
            uzastopna = 0
            for i in range(1, len(predavanja_u_danu)):
                if predavanja_u_danu[i] == predavanja_u_danu[i - 1] + 1:
                    uzastopna += 1
                else:
                    if uzastopna >= 2:
                        trosak_uzastopna_predavanja += uzastopna -2# Smanjeni trošak za 2 umjesto 1
                    uzastopna = 0
            if uzastopna >= 2:
                trosak_uzastopna_predavanja += uzastopna -2 # Smanjeni trošak za 2 umjesto 1


            # Provjera troška za zadnji interval u danu (termin 8)
            if predavanja_u_danu and predavanja_u_danu[-1] == 8:
                trosak_zadnji_interval += 1  # Ako je zadnje predavanje u terminu 8, povećaj trošak

    # Suma svih troškova mekih uvjeta
    trosak_mekih_uvjeta = trosak_jedno_predavanje + trosak_uzastopna_predavanja + trosak_zadnji_interval

    return trosak_mekih_uvjeta



#################################################### ZADATAK 1 ########################################################################3


def izracunaj_trosak(putanja_do_izlazne_datoteke, podaci):
    trosak_tvrdih = udaljenost_do_dopustivosti(putanja_do_izlazne_datoteke, podaci)
    trosak_mekih = trosak_narusavanja_mekih_uvjeta(putanja_do_izlazne_datoteke, podaci)
    return trosak_tvrdih + trosak_mekih


def generiraj_kromosom(broj_dogadaja, broj_termina, broj_ucionica):
    return [(random.randint(0, broj_termina - 1), random.randint(0, broj_ucionica - 1)) for _ in range(broj_dogadaja)]

def izracunaj_prilagodbu(kromosom, podaci, putanja_do_izlazne_datoteke):
    with open(putanja_do_izlazne_datoteke, 'w') as f:
        for termin, ucionica in kromosom:
            f.write(f"{termin} {ucionica}\n")

    # Izračunaj trošak iz osnovnog rješenja
    trosak = izracunaj_trosak(putanja_do_izlazne_datoteke, podaci)

    # Dodaj udaljenost do dopuštenosti kao penalizaciju
    penalizacija = udaljenost_do_dopustivosti(putanja_do_izlazne_datoteke, podaci)
    
    # Prilagodba je kombinacija osnovnog troška i penalizacije
    prilagodba = trosak + penalizacija
    return prilagodba

def mutacija(kromosom, broj_dogadaja, broj_termina, broj_ucionica):
    novi_kromosom = kromosom[:]
    indeks = random.randint(0, broj_dogadaja - 1)
    novi_kromosom[indeks] = (random.randint(0, broj_termina - 1), random.randint(0, broj_ucionica - 1))
    return novi_kromosom

def krizanje(roditelj1, roditelj2, broj_dogadaja):
    tocka = random.randint(1, broj_dogadaja - 1)
    dijete = roditelj1[:tocka] + roditelj2[tocka:]
    return dijete



def eliminacijski_ga(podaci, broj_iteracija, velicina_populacije, stopa_mutacije, putanja_do_izlazne_datoteke):
    broj_dogadaja = podaci['num_events']
    broj_termina = 45  # 9 termina x 5 dana
    broj_ucionica = podaci['num_rooms']

    populacija = [generiraj_kromosom(broj_dogadaja, broj_termina, broj_ucionica) for _ in range(velicina_populacije)]
    prilagodbe = [izracunaj_prilagodbu(kromosom, podaci, putanja_do_izlazne_datoteke) for kromosom in populacija]

    for iteracija in range(broj_iteracija):
        kandidat1, kandidat2 = random.sample(range(velicina_populacije), 2)
        roditelj1 = populacija[kandidat1 if prilagodbe[kandidat1] < prilagodbe[kandidat2] else kandidat2]

        kandidat3, kandidat4 = random.sample(range(velicina_populacije), 2)
        roditelj2 = populacija[kandidat3 if prilagodbe[kandidat3] < prilagodbe[kandidat4] else kandidat4]

        dijete = krizanje(roditelj1, roditelj2, broj_dogadaja)
        if random.random() < stopa_mutacije:
            dijete = mutacija(dijete, broj_dogadaja, broj_termina, broj_ucionica)

        prilagodba_dijete = izracunaj_prilagodbu(dijete, podaci, putanja_do_izlazne_datoteke)

        najgori_indeks = prilagodbe.index(max(prilagodbe))
        populacija[najgori_indeks] = dijete
        prilagodbe[najgori_indeks] = prilagodba_dijete

        if iteracija % 10 == 0:
            print(f"Iteracija: {iteracija}, najbolji trošak: {min(prilagodbe)}")

    najbolji_indeks = prilagodbe.index(min(prilagodbe))
    najbolji_kromosom = populacija[najbolji_indeks]

    with open(putanja_do_izlazne_datoteke, 'w') as f:
        for termin, ucionica in najbolji_kromosom:
            f.write(f"{termin} {ucionica}\n")

    print(f"Najbolje rješenje zapisano u: {putanja_do_izlazne_datoteke}")
    return najbolji_kromosom, min(prilagodbe)



def generacijski_ga(podaci, broj_iteracija, velicina_populacije, stopa_mutacije, putanja_do_izlazne_datoteke):
    broj_dogadaja = podaci['num_events']
    broj_termina = 45  # 9 termina x 5 dana
    broj_ucionica = podaci['num_rooms']

    populacija = [generiraj_kromosom(broj_dogadaja, broj_termina, broj_ucionica) for _ in range(velicina_populacije)]
    prilagodbe = [izracunaj_prilagodbu(kromosom, podaci, putanja_do_izlazne_datoteke) for kromosom in populacija]

    for iteracija in range(broj_iteracija):
        nova_generacija = []

        while len(nova_generacija) < velicina_populacije:
            roditelj1, roditelj2 = random.choices(populacija, weights=[1/f for f in prilagodbe], k=2)
            dijete = krizanje(roditelj1, roditelj2, broj_dogadaja)
            if random.random() < stopa_mutacije:
                dijete = mutacija(dijete, broj_dogadaja, broj_termina, broj_ucionica)
            nova_generacija.append(dijete)

        populacija = nova_generacija
        prilagodbe = [izracunaj_prilagodbu(kromosom, podaci, putanja_do_izlazne_datoteke) for kromosom in populacija]

        if iteracija % 10 == 0:
            print(f"Iteracija: {iteracija}, najbolji trošak: {min(prilagodbe)}")

    najbolji_indeks = prilagodbe.index(min(prilagodbe))
    najbolji_kromosom = populacija[najbolji_indeks]

    with open(putanja_do_izlazne_datoteke, 'w') as f:
        for termin, ucionica in najbolji_kromosom:
            f.write(f"{termin} {ucionica}\n")

    print(f"Najbolje rješenje zapisano u: {putanja_do_izlazne_datoteke}")
    return najbolji_kromosom, min(prilagodbe)



################################################### PROVEDBA ####################################################################

# UPIŠITE VAŠU PUTANJU DO MAPE U KOJOJ SE NALAZE DATOTEKE DATASETS I VALIDATOR !
path = r"C:\Users\Administrator\Desktop\Moj pokusaj"

path_datasets = os.path.join(path, 'datasets')

#Stvaramo datoteke u koje spremamo rješenja algoritama
path_eg1 = os.path.join(path, 'Eliminacijski genetički algoritam 1')
path_eg2=os.path.join(path, 'Eliminacijski genetički algoritam 2')
path_eg3=os.path.join(path, 'Eliminacijski genetički algoritam 3')
path_gg1=os.path.join(path, 'Generacijski genetički algoritam 1')
path_gg2=os.path.join(path, 'Generacijski genetički algoritam 2')
path_gg3=os.path.join(path, 'Generacijski genetički algoritam 3')


#U tekstualne datoteke spremamo informacije: naziv datoteke za koju smo napravili raspored, udaljenost do dopustivosti tog rasporeda, trošak narušavanja mekih uvjeta te sumu prethodna 2 izračuna
informacije_eg1_putanja=os.path.join(path_eg1, 'Informacije.txt')
informacije_eg2_putanja=os.path.join(path_eg2, 'Informacije.txt')
informacije_eg3_putanja=os.path.join(path_eg3, 'Informacije.txt')
informacije_gg1_putanja=os.path.join(path_gg1, 'Informacije.txt')
informacije_gg2_putanja=os.path.join(path_gg2, 'Informacije.txt')
informacije_gg3_putanja=os.path.join(path_gg3, 'Informacije.txt')


#Kreiranje mapa
if not os.path.exists(path_eg1):
    os.makedirs(path_eg1)
    
if not os.path.exists(path_eg2):
    os.makedirs(path_eg2)
    
if not os.path.exists(path_eg3):
    os.makedirs(path_eg3)
    
if not os.path.exists(path_gg1):
    os.makedirs(path_gg1)

if not os.path.exists(path_gg2):
    os.makedirs(path_gg2)

if not os.path.exists(path_gg3):
    os.makedirs(path_gg3)
    


    
with open(informacije_eg1_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_eg2_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")
            
with open(informacije_eg3_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_gg1_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_gg2_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_gg3_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")




# Provjeriti da putanja postoji
if os.path.exists(path_datasets):
    # Prolazimo kroz sve datoteke i podmape u zadanoj mapi
    files = []

    # Prikupljamo sve datoteke u listu
    for root, dirs, files_in_dir in os.walk(path_datasets):
        for file in files_in_dir:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):  # Provjeravamo da je datoteka
                files.append(file_path)

    # Sortiramo datoteke:
    files.sort(key=lambda x: os.path.getctime(x))

    # Ispisujemo datoteke u redoslijedu stvaranja
    for file_path in files:
            #Ispišimo naziv datoteke s kojom radimo:
            s=os.path.splitext(os.path.basename(file_path))[0]
            
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Eliminacijski genetički algoritam 1:")
        
            sln_file_path1 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Eliminacijski genetički algoritam 1'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci1=read_tim_file(file_path)
            schedule_output1 = generacijski_ga(podaci1, 100, 50, 0.1, sln_file_path1)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Eliminacijskog genetičkog algoritma 1:")
            raspored1 = ucitaj_raspored(sln_file_path1)
            is_valid1 = provjera_dopustivosti(raspored1, podaci1)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path1,podaci1)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku
            output_file_path1 = sln_file_path1.replace('.sln', '.txt')
            
            generiraj_raspored_ucionica(sln_file_path1,output_file_path1)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u1=udaljenost_do_dopustivosti(sln_file_path1,podaci1)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t1=trosak_narusavanja_mekih_uvjeta(sln_file_path1,podaci1)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name1 = os.path.splitext(os.path.basename(sln_file_path1))[0]
            with open(informacije_eg1_putanja, 'a') as file:
                        file.write(f"{file_name1}                {u1}                                {t1}                       {u1+t1}\n")
                        
            
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Eliminacijski genetički algoritam 2:")
        
            sln_file_path2 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Eliminacijski genetički algoritam 2'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci2=read_tim_file(file_path)
            schedule_output2 = eliminacijski_ga(podaci2, 100, 100, 0.5, sln_file_path2)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Eliminacijskog genetičkog algoritma 2:")
            raspored2 = ucitaj_raspored(sln_file_path2)
            is_valid2 = provjera_dopustivosti(raspored2, podaci2)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path1,podaci2)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku
            output_file_path2 = sln_file_path2.replace('.sln', '.txt')
            
            generiraj_raspored_ucionica(sln_file_path2,output_file_path2)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u2=udaljenost_do_dopustivosti(sln_file_path2,podaci2)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t2=trosak_narusavanja_mekih_uvjeta(sln_file_path2,podaci2)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name2 = os.path.splitext(os.path.basename(sln_file_path2))[0]
            with open(informacije_eg2_putanja, 'a') as file:
                        file.write(f"{file_name2}                {u2}                                {t2}                       {u2+t2}\n")
                        
                        
            
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Eliminacijski genetički algoritam 3:")
        
            sln_file_path3 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Eliminacijski genetički algoritam 3'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci3=read_tim_file(file_path)
            schedule_output3 = eliminacijski_ga(podaci3, 100, 50, 0.05, sln_file_path3)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Eliminacijskog genetičkog algoritma 3:")
            raspored3 = ucitaj_raspored(sln_file_path3)
            is_valid3 = provjera_dopustivosti(raspored3, podaci3)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path3,podaci3)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku
            output_file_path3 = sln_file_path3.replace('.sln', '.txt')
            
            generiraj_raspored_ucionica(sln_file_path3,output_file_path3)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u3=udaljenost_do_dopustivosti(sln_file_path3,podaci3)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t3=trosak_narusavanja_mekih_uvjeta(sln_file_path3,podaci3)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name3 = os.path.splitext(os.path.basename(sln_file_path3))[0]
            with open(informacije_eg3_putanja, 'a') as file:
                        file.write(f"{file_name3}                {u3}                                {t3}                       {u3+t3}\n")
            
            
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Generacijski genetički algoritam 1:")
        
            sln_file_path4 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Generacijski genetički algoritam 1'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci4=read_tim_file(file_path)
            schedule_output4 = generacijski_ga(podaci4, 100, 50, 0.1, sln_file_path4)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Generacijskog genetičkog algoritma 1:")
            raspored4 = ucitaj_raspored(sln_file_path4)
            is_valid4 = provjera_dopustivosti(raspored4, podaci4)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path4,podaci4)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku
            output_file_path4 = sln_file_path4.replace('.sln', '.txt')
            
            generiraj_raspored_ucionica(sln_file_path4,output_file_path4)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u4=udaljenost_do_dopustivosti(sln_file_path4,podaci4)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t4=trosak_narusavanja_mekih_uvjeta(sln_file_path4,podaci4)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name4 = os.path.splitext(os.path.basename(sln_file_path4))[0]
            with open(informacije_gg1_putanja, 'a') as file:
                        file.write(f"{file_name4}                {u4}                                {t4}                       {u4+t4}\n")
            
            
            
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Generacijski genetički algoritam 2:")
        
            sln_file_path5 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Generacijski genetički algoritam 2'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci5=read_tim_file(file_path)
            schedule_output5 = generacijski_ga(podaci5, 100, 100, 0.5, sln_file_path5)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Generacijskog genetičkog algoritma 2:")
            raspored5 = ucitaj_raspored(sln_file_path5)
            is_valid5 = provjera_dopustivosti(raspored5, podaci5)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path5,podaci5)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku
            output_file_path5 = sln_file_path5.replace('.sln', '.txt')
            
            generiraj_raspored_ucionica(sln_file_path5,output_file_path5)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u5=udaljenost_do_dopustivosti(sln_file_path5,podaci5)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t5=trosak_narusavanja_mekih_uvjeta(sln_file_path5,podaci5)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name5 = os.path.splitext(os.path.basename(sln_file_path5))[0]
            with open(informacije_gg2_putanja, 'a') as file:
                        file.write(f"{file_name5}                {u5}                                {t5}                       {u5+t5}\n")
            
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Generacijski genetički algoritam 3:")
        
            sln_file_path6 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Generacijski genetički algoritam 3'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci6=read_tim_file(file_path)
            schedule_output6 = generacijski_ga(podaci6, 100, 50, 0.05, sln_file_path6)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Generacijskog genetičkog algoritma 3:")
            raspored6 = ucitaj_raspored(sln_file_path6)
            is_valid6 = provjera_dopustivosti(raspored6, podaci6)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path6,podaci6)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku
            output_file_path6 = sln_file_path6.replace('.sln', '.txt')
            
            generiraj_raspored_ucionica(sln_file_path6,output_file_path6)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u6=udaljenost_do_dopustivosti(sln_file_path6,podaci6)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t6=trosak_narusavanja_mekih_uvjeta(sln_file_path6,podaci6)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name6 = os.path.splitext(os.path.basename(sln_file_path6))[0]
            with open(informacije_gg3_putanja, 'a') as file:
                        file.write(f"{file_name6}                {u6}                                {t6}                       {u6+t6}\n")
            
            
            
            
           

           
                                                            
