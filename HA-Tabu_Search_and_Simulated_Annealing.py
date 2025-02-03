import os
import random
import copy


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



def tabu_pretrazivanje(podaci, broj_iteracija, tabu_velicina, putanja_do_izlazne_datoteke):
    # Parametri problema
    broj_dogadaja = podaci['num_events']
    broj_termina = 45  # 9 termina x 5 dana
    broj_ucionica = podaci['num_rooms']

    # Početno rješenje: dodjeljujemo nasumično termine i učionice
    trenutna_rjesenja = [
        (random.randint(0, broj_termina - 1), random.randint(0, broj_ucionica - 1))
        for _ in range(broj_dogadaja)
    ]

    # Spremanje početnog rješenja u datoteku
    with open(putanja_do_izlazne_datoteke, 'w') as f:
        for i, (termin, ucionica) in enumerate(trenutna_rjesenja):
            f.write(f"{termin} {ucionica}\n")

    # Najbolje rješenje
    najbolje_rjesenje = trenutna_rjesenja[:]
    najbolji_trosak = izracunaj_trosak(putanja_do_izlazne_datoteke, podaci)

    # Tabu lista
    tabu_lista = []

    for iteracija in range(broj_iteracija):
        # Generiranje susjedstva (manje opcija)
        susjedna_rjesenja = []
        
        # Nasumično odabiremo 20 događaja za premještanje
        nasumicni_dogadaji = random.sample(range(broj_dogadaja), 20)  # Odaberi 20 događaja

        for i in nasumicni_dogadaji:
            # Za svaki od odabranih događaja nasumično biramo novi termin i učionicu
            novi_termin = random.randint(0, broj_termina - 1)
            nova_ucionica = random.randint(0, broj_ucionica - 1)
            
            # Stvaramo novo rješenje s promijenjenim samo jednim događajem
            novo_rjesenje = trenutna_rjesenja[:]
            novo_rjesenje[i] = (novi_termin, nova_ucionica)
            
            # Provjeravamo da li ovo rješenje nije na tabu listi
            if novo_rjesenje not in tabu_lista:
                susjedna_rjesenja.append(novo_rjesenje)

        # Procjena susjednih rješenja
        najbolji_susjed = None
        najbolji_susjed_trosak = float('inf')

        for rjesenje in susjedna_rjesenja:
            trosak = izracunaj_trosak(putanja_do_izlazne_datoteke, podaci)
            if trosak < najbolji_susjed_trosak:
                najbolji_susjed = rjesenje
                najbolji_susjed_trosak = trosak

        # Ažuriranje trenutnog rješenja i tabu liste
        if najbolji_susjed is not None:
            trenutna_rjesenja = najbolji_susjed[:]
            tabu_lista.append(najbolji_susjed)
            if len(tabu_lista) > tabu_velicina:
                tabu_lista.pop(0)

        # Ažuriranje najboljeg rješenja
        if najbolji_susjed_trosak < najbolji_trosak:
            najbolje_rjesenje = najbolji_susjed[:]
            najbolji_trosak = najbolji_susjed_trosak

        # Spremanje trenutnog rješenja u datoteku nakon svake iteracije
        with open(putanja_do_izlazne_datoteke, 'w') as f:  # 'a' za dodavanje na kraj datoteke
            for i, (termin, ucionica) in enumerate(trenutna_rjesenja):
                f.write(f"{termin} {ucionica}\n")

        # Ispis statusa svakih 10 iteracija
        if iteracija % 10 == 0:
            print(f"Iteracija: {iteracija}, najbolji trošak: {najbolji_trosak}")

    # Upisivanje samo najboljeg rješenja u datoteku
    with open(putanja_do_izlazne_datoteke, 'w') as f:  # 'a' za dodavanje na kraj datoteke
        for i, (termin, ucionica) in enumerate(najbolje_rjesenje):
            f.write(f"{termin} {ucionica}\n")

    print(f"Najbolje rješenje zapisano u: {putanja_do_izlazne_datoteke}")
    return najbolje_rjesenje, najbolji_trosak


def izracunaj_trosak(putanja_do_izlazne_datoteke, podaci):
    trosak_tvrdih = udaljenost_do_dopustivosti(putanja_do_izlazne_datoteke, podaci)
    trosak_mekih = trosak_narusavanja_mekih_uvjeta(putanja_do_izlazne_datoteke, podaci)
    return trosak_tvrdih + trosak_mekih




###################################################### ZADATAK 2 ###############################################################

import math

def simulirano_kaljenje(podaci, broj_iteracija, pocetna_temperatura, faktor_hladjenja, putanja_do_izlazne_datoteke):
    # Parametri problema
    broj_dogadaja = podaci['num_events']
    broj_termina = 45  # 9 termina x 5 dana
    broj_ucionica = podaci['num_rooms']

    # Početno rješenje: nasumično dodijeljeni termini i učionice
    trenutna_rjesenja = [
        (random.randint(0, broj_termina - 1), random.randint(0, broj_ucionica - 1))
        for _ in range(broj_dogadaja)
    ]
    
    # Kreiraj početni valjani raspored
    with open(putanja_do_izlazne_datoteke, 'w') as f:
        for i, (termin, ucionica) in enumerate(trenutna_rjesenja):
            f.write(f"{termin} {ucionica}\n")
    
    #kreiraj_valjan_raspored(putanja_do_izlazne_datoteke, podaci)
    trenutni_trosak = izracunaj_trosak(putanja_do_izlazne_datoteke, podaci)

    # Postavljanje početne temperature
    temperatura = pocetna_temperatura

    # Najbolje rješenje
    najbolje_rjesenje = trenutna_rjesenja[:]
    najbolji_trosak = trenutni_trosak

    # Iteracije simuliranog kaljenja
    for iteracija in range(broj_iteracija):
        # Generiranje susjednog rješenja (mijenjanje nasumičnog događaja)
        i = random.randint(0, broj_dogadaja - 1)
        novi_termin = random.randint(0, broj_termina - 1)
        nova_ucionica = random.randint(0, broj_ucionica - 1)
        
        novo_rjesenje = trenutna_rjesenja[:]
        novo_rjesenje[i] = (novi_termin, nova_ucionica)

        # Spremanje novog rješenja u datoteku
        with open(putanja_do_izlazne_datoteke, 'w') as f:
            for j, (termin, ucionica) in enumerate(novo_rjesenje):
                f.write(f"{termin} {ucionica}\n")
        
        # Primjena valjanosti na novo rješenje
        #kreiraj_valjan_raspored(putanja_do_izlazne_datoteke, podaci)
        
        # Izračunavanje troška novog rješenja
        novi_trosak = izracunaj_trosak(putanja_do_izlazne_datoteke, podaci)
        
        # Ako je novo rješenje bolje ili je lošije s određenom vjerojatnošću
        if novi_trosak < trenutni_trosak or random.random() < math.exp((trenutni_trosak - novi_trosak) / temperatura):
            trenutna_rjesenja = novo_rjesenje
            trenutni_trosak = novi_trosak

            # Ažuriranje najboljeg rješenja
            if trenutni_trosak < najbolji_trosak:
                najbolje_rjesenje = trenutna_rjesenja[:]
                najbolji_trosak = trenutni_trosak

        # Smanjivanje temperature
        temperatura *= faktor_hladjenja

        # Ispis statusa svakih 10 iteracija
        if iteracija % 10 == 0:
            print(f"Iteracija: {iteracija}, najbolji trošak: {najbolji_trosak}, temperatura: {temperatura}")

    # Spremanje najboljeg rješenja
    with open(putanja_do_izlazne_datoteke, 'w') as f:
        for i, (termin, ucionica) in enumerate(najbolje_rjesenje):
            f.write(f"{termin} {ucionica}\n")

    print(f"Najbolje rješenje zapisano u: {putanja_do_izlazne_datoteke}")
    return najbolje_rjesenje, najbolji_trosak





################################################### PROVEDBA ####################################################################

# UPIŠITE VAŠU PUTANJU DO MAPE U KOJOJ SE NALAZE DATOTEKE DATASETS I VALIDATOR !
path = r"C:\Users\Administrator\Desktop\Pokušaj"

path_datasets = os.path.join(path, 'datasets')

#Stvaramo datoteke u koje spremamo rješenja algoritama
path_tabu1 = os.path.join(path, 'Tabu pretraživanje 1')
path_tabu2=os.path.join(path, 'Tabu pretraživanje 2')
path_tabu3=os.path.join(path, 'Tabu pretraživanje 3')
path_kaljenje1=os.path.join(path, 'Algoritam simuliranog kaljenja 1')
path_kaljenje2=os.path.join(path, 'Algoritam simuliranog kaljenja 2')
path_kaljenje3=os.path.join(path, 'Algoritam simuliranog kaljenja 3')

#U tekstualne datoteke spremamo informacije: naziv datoteke za koju smo napravili raspored, udaljenost do dopustivosti tog rasporeda, trošak narušavanja mekih uvjeta te sumu prethodna 2 izračuna
informacije_tabu1_putanja=os.path.join(path_tabu1, 'Informacije.txt')
informacije_tabu2_putanja=os.path.join(path_tabu2, 'Informacije.txt')
informacije_tabu3_putanja=os.path.join(path_tabu3, 'Informacije.txt')
informacije_kaljenje1_putanja=os.path.join(path_kaljenje1, 'Informacije.txt')
informacije_kaljenje2_putanja=os.path.join(path_kaljenje2, 'Informacije.txt')
informacije_kaljenje3_putanja=os.path.join(path_kaljenje3, 'Informacije.txt')

#Kreirajmo mapu Tabu pretraživanje 1 u koju ćemo spremati rasporede dobivene tabu pretraživanjem s parametrima br_iter=100 i tabu=50 za sve datasetove
if not os.path.exists(path_tabu1):
    os.makedirs(path_tabu1)
    
#Kreirajmo mapu Tabu pretraživanje 2 u koju ćemo spremati rasporede dobivene tabu pretraživanjem s parametrima br_iter=100 i tabu=10 za sve datasetove
if not os.path.exists(path_tabu2):
    os.makedirs(path_tabu2)
    
#Kreirajmo mapu Tabu pretraživanje 3 u koju ćemo spremati rasporede dobivene tabu pretraživanjem s parametrima br_iter=50 i tabu=100 za sve datasetove
if not os.path.exists(path_tabu3):
    os.makedirs(path_tabu3)
    
if not os.path.exists(path_kaljenje1):
    os.makedirs(path_kaljenje1)
    
if not os.path.exists(path_kaljenje2):
    os.makedirs(path_kaljenje2)

if not os.path.exists(path_kaljenje3):
    os.makedirs(path_kaljenje3)
    

    
with open(informacije_tabu1_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_tabu2_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")
            
with open(informacije_tabu3_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")
    
with open(informacije_kaljenje1_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_kaljenje2_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_kaljenje3_putanja, 'a') as file:
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

    # Sortiramo datoteke prema vremenu stvaranja (ctime)
    files.sort(key=lambda x: os.path.getctime(x))  # Možeš koristiti getmtime za modifikaciju

    # Ispisujemo datoteke u redoslijedu stvaranja
    for file_path in files:
            #Ispišimo naziv datoteke s kojom radimo:
            s=os.path.splitext(os.path.basename(file_path))[0]
            print(f"\n\n\n---------------{s}----------------\n")
            print("-----Tabu pretraživanje 1 (br_iteracija=100 , tabu=50):")
        
            sln_file_path1 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Tabu pretraživanje 1'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci1=read_tim_file(file_path)
            schedule_output1 = tabu_pretrazivanje(podaci1, 100, 50, sln_file_path1)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Tabu pretraživanje 1 (100 , 50):")
            raspored1 = ucitaj_raspored(sln_file_path1)
            is_valid1 = provjera_dopustivosti(raspored1, podaci1)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path1,podaci1)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Tabu pretraživanje 1,no s ekstenzijom .txt ,a ne .sln:
            output_file_path1 = sln_file_path1.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path1,output_file_path1)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u1=udaljenost_do_dopustivosti(sln_file_path1,podaci1)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t1=trosak_narusavanja_mekih_uvjeta(sln_file_path1,podaci1)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name1 = os.path.splitext(os.path.basename(sln_file_path1))[0]
            with open(informacije_tabu1_putanja, 'a') as file:
                        file.write(f"{file_name1}                {u1}                                {t1}                       {u1+t1}\n")
                        
            
            
            
            print("\n-----Tabu pretraživanje 2 (br_iteracija=100 , tabu=10):")
        
            sln_file_path2 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Tabu pretraživanje 2'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci2=read_tim_file(file_path)
            schedule_output2 = tabu_pretrazivanje(podaci2, 100, 10, sln_file_path2)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Tabu pretraživanje 1 (100 , 50):")
            raspored2 = ucitaj_raspored(sln_file_path2)
            is_valid2 = provjera_dopustivosti(raspored2, podaci2)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path2,podaci2)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Tabu pretraživanje 2, no s ekstenzijom .txt ,a ne .sln:
            output_file_path2 = sln_file_path2.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path2,output_file_path2)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u2=udaljenost_do_dopustivosti(sln_file_path2,podaci2)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t2=trosak_narusavanja_mekih_uvjeta(sln_file_path2,podaci2)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name2 = os.path.splitext(os.path.basename(sln_file_path2))[0]
            with open(informacije_tabu2_putanja, 'a') as file:
                        file.write(f"{file_name2}                {u2}                                {t2}                       {u2+t2}\n")
                        
            
            
            
            print("\n-----Tabu pretraživanje 3 (br_iteracija=50 , tabu=100):")
        
            sln_file_path3 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Tabu pretraživanje 3'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci3=read_tim_file(file_path)
            schedule_output3 = tabu_pretrazivanje(podaci3, 50, 100, sln_file_path3)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Tabu pretraživanje 1 (100 , 50):")
            raspored3 = ucitaj_raspored(sln_file_path3)
            is_valid3 = provjera_dopustivosti(raspored3, podaci3)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path3,podaci3)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Tabu pretraživanje 3, no s ekstenzijom .txt ,a ne .sln:
            output_file_path3 = sln_file_path3.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path3,output_file_path3)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u3=udaljenost_do_dopustivosti(sln_file_path3,podaci3)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t3=trosak_narusavanja_mekih_uvjeta(sln_file_path3,podaci3)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name3 = os.path.splitext(os.path.basename(sln_file_path3))[0]
            with open(informacije_tabu3_putanja, 'a') as file:
                        file.write(f"{file_name3}                {u3}                                {t3}                       {u3+t3}\n")
             
                        
             
                
             
            

            print("\n-----Simulirano kaljenje 1 (br_iteracija=100, pocetna_temp=100):")
        
            sln_file_path4 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Algoritam simuliranog kaljenja 1'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci4=read_tim_file(file_path)
            schedule_output4 = simulirano_kaljenje(podaci4, 100, 100, 0.95, sln_file_path4)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Simuliranog kaljenja 1 (100, 100):")
            raspored4 = ucitaj_raspored(sln_file_path4)
            is_valid4= provjera_dopustivosti(raspored4, podaci4)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path4,podaci4)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Tabu pretraživanje 3, no s ekstenzijom .txt ,a ne .sln:
            output_file_path4 = sln_file_path4.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path4,output_file_path4)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u4=udaljenost_do_dopustivosti(sln_file_path4,podaci4)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t4=trosak_narusavanja_mekih_uvjeta(sln_file_path4,podaci4)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name4 = os.path.splitext(os.path.basename(sln_file_path4))[0]
            with open(informacije_kaljenje1_putanja, 'a') as file:
                        file.write(f"{file_name4}                {u4}                                {t4}                       {u4+t4}\n")
                        
            
            print("\n-----Simulirano kaljenje 2 (br_iteracija=100, pocetna_temp=1000):")
        
            sln_file_path5 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Algoritam simuliranog kaljenja 2'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci5=read_tim_file(file_path)
            schedule_output5 = simulirano_kaljenje(podaci5, 100, 1000, 0.95, sln_file_path5)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Simuliranog kaljenja 2 (100, 1000):")
            raspored5 = ucitaj_raspored(sln_file_path5)
            is_valid5= provjera_dopustivosti(raspored5, podaci5)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path5,podaci5)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Tabu pretraživanje 3, no s ekstenzijom .txt ,a ne .sln:
            output_file_path5 = sln_file_path5.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path5,output_file_path5)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u5=udaljenost_do_dopustivosti(sln_file_path5,podaci5)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t5=trosak_narusavanja_mekih_uvjeta(sln_file_path5,podaci5)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name5 = os.path.splitext(os.path.basename(sln_file_path5))[0]
            with open(informacije_kaljenje2_putanja, 'a') as file:
                        file.write(f"{file_name5}                {u5}                                {t5}                       {u5+t5}\n")
            
            print("\n-----Simulirano kaljenje 3 (br_iteracija=200, pocetna_temp=100):")
        
            sln_file_path6 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Algoritam simuliranog kaljenja 3'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci6=read_tim_file(file_path)
            schedule_output6 = simulirano_kaljenje(podaci6, 200, 100, 0.95, sln_file_path6)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću Simuliranog kaljenja 3 (200, 100):")
            raspored6 = ucitaj_raspored(sln_file_path6)
            is_valid6= provjera_dopustivosti(raspored6, podaci6)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path6,podaci6)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Tabu pretraživanje 3, no s ekstenzijom .txt ,a ne .sln:
            output_file_path6 = sln_file_path6.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path6,output_file_path6)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u6=udaljenost_do_dopustivosti(sln_file_path6,podaci6)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t6=trosak_narusavanja_mekih_uvjeta(sln_file_path6,podaci6)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name6 = os.path.splitext(os.path.basename(sln_file_path6))[0]
            with open(informacije_kaljenje3_putanja, 'a') as file:
                        file.write(f"{file_name6}                {u6}                                {t6}                       {u6+t6}\n")
                        
            
                        