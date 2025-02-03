import os
import random
import copy

################################################## ZADATAK 1 ###########################################################################

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

    print("Izmijenjeni (valjani) raspored je zapisan u datoteku.")
    
    


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


#################################################### ZADATAK 2 ########################################################################3

"""""""""""""""""""Greedy algoritam"""""""""""""""

#prvo rasporedimo one događaje koje sluša najveći broj studenata
def prioritize_events(data):
    # Prioritize events by number of students enrolled (more students = higher priority)
    num_students_per_event = [sum(data['student_event'][i::data['num_events']]) for i in range(data['num_events'])]
    # Sort events by the number of students, in descending order
    prioritized_events = sorted(range(data['num_events']), key=lambda e: num_students_per_event[e], reverse=True)
    return prioritized_events

#svakom događaju pridružimo najmanju učionicu koja zadovoljava zahtjevani kapacitet
def select_optimal_room(event, data):
    # Select the smallest room that meets the capacity and feature requirements
    required_capacity = sum([data['student_event'][event + i * data['num_events']] for i in range(data['num_students'])])

    for room in range(data['num_rooms']):
        # Check if the room has enough capacity
        if data['room_capacities'][room] < required_capacity:
            continue

        # Check if the room meets feature requirements
        has_all_features = True
        for feature in range(data['num_features']):
            event_needs_feature = data['event_feature'][event * data['num_features'] + feature]
            room_has_feature = data['room_feature'][room * data['num_features'] + feature]
            if event_needs_feature and not room_has_feature:
                has_all_features = False
                break

        if has_all_features:
            return room  # Return the first room that meets all criteria

    return None  # No suitable room found

#Pronalazimo najraniji termin u koji taj događaj smije biti smješten, a da je termin dostupan
def find_earliest_timeslot(event, room, schedule, data):
    # Find the earliest timeslot for the event that is available in the room and does not violate constraints
    for timeslot in range(45):
        is_available = True

        # Check if the event can be held at this timeslot
        if data['event_timeslot'][event * 45 + timeslot] == 0:
            continue  # Timeslot is not available for this event

        # Check for conflicts with other scheduled events in the same room
        for other_event, (other_timeslot, other_room) in enumerate(schedule):
            if other_room == room and other_timeslot == timeslot:
                is_available = False
                break

        if is_available:
            return timeslot  # Return the first suitable timeslot

    return None  # No suitable timeslot found

#Pomoću greedy algoritma stvaramo raspored koji zadovoljava prethodna 3 uvjeta, dakle rezultat greedy algoritma neće biti valjan raspored (to ćemo osigurati drugom metodom)
def greedy_schedule(data, output_file):
    schedule_output = [(-1, -1) for _ in range(data['num_events'])]

    # Prioritize events by the chosen criteria
    events = prioritize_events(data)

    for event in events:
        # Select the optimal room for the event
        room = select_optimal_room(event, data)
        if room is None:
            # print(f"Nema odgovarajuće prostorije za događaj {event}.")
            continue

        # Find the earliest available timeslot for the event
        timeslot = find_earliest_timeslot(event, room, schedule_output, data)
        if timeslot is None:
            # print(f"Nema odgovarajućeg termina za događaj {event}.")
            continue

        # Assign the room and timeslot to the event
        schedule_output[event] = (timeslot, room)
        # print(f"Događaj {event} je raspoređen u prostoriju {room} u vremenskom intervalu {timeslot}.")
    
    # Write the schedule to an output file in the required format
    with open(output_file, "w") as file:
        for timeslot, room in schedule_output:
            file.write(f"{timeslot} {room}\n")

    print(f"Rješenje je zapisano u {output_file}")
    return schedule_output



###################################################### ZADATAK 3 ###############################################################

def generiraj_pocetni_random_raspored(podaci):
    num_events = podaci['num_events']
    num_rooms = podaci['num_rooms']
    num_terms = 5 * 9  # 5 dana, 9 termina po danu
    raspored = {}
    for event in range(num_events):
        random_termin = random.randint(0, num_terms - 1)  # Random termin
        random_ucionica = random.randint(0, num_rooms - 1)  # Random učionica
        raspored[event] = (random_termin, random_ucionica)
    return raspored

def spremi_raspored(raspored, file_path):
    with open(file_path, 'w') as file:
        for event, (termin, ucionica) in raspored.items():
            file.write(f"{termin} {ucionica}\n")


"""""""""""""""""""""""""""""""""Lokalno pretraživanje koje koristi random zamjenu učionice i termina od 2 događaja"""""""""""""""""""""""""""""""""""""""""""""""


####Algoritam ponavljamo sve dok ne pronađemo najboljeg poboljšavajućeg susjeda (ograničili smo se na 100 iteracija)

def kreiraj_susjeda1(raspored, podaci):
    susjed_raspored = copy.deepcopy(raspored)
    num_events = podaci['num_events']
    random_event = random.randint(0, num_events - 1)
    novi_termin = random.randint(0, 44)  # 5 dana * 9 termina po danu
    novi_ucionica = random.randint(0, podaci['num_rooms'] - 1)
    susjed_raspored[random_event] = (novi_termin, novi_ucionica)
    return susjed_raspored

def lokalno_pretrazivanje_1_1(podaci, sln_file_path):
    # Generiraj početni random raspored i pohrani ga
    pocetni_raspored = generiraj_pocetni_random_raspored(podaci)
    spremi_raspored(pocetni_raspored, sln_file_path)
    
    # Izračunaj trošak početnog rasporeda
    najbolji_trosak = trosak_narusavanja_mekih_uvjeta(sln_file_path, podaci)
    najbolji_raspored = copy.deepcopy(pocetni_raspored)
    
    # Postavljamo maksimalan broj iteracija
    max_iteracija = 100
    iteracija = 0

    while iteracija < max_iteracija:
        iteracija += 1
        # Kreiramo susjeda i pohranjujemo ga u privremenu .sln datoteku
        susjed_raspored = kreiraj_susjeda1(najbolji_raspored, podaci)
        privremeni_file_path = sln_file_path.replace('.sln', '_temp.sln')
        spremi_raspored(susjed_raspored, privremeni_file_path)

        # Izračunaj trošak susjednog rasporeda
        susjed_trosak = trosak_narusavanja_mekih_uvjeta(privremeni_file_path, podaci)
        
        # Ispis troška trenutnog i susjednog rasporeda
        trenutni_trosak = najbolji_trosak
        #print(f"Iteracija {iteracija}: Trenutni trošak = {trenutni_trosak}, Susjedni trošak = {susjed_trosak}")
        
        # Ako susjed ima manji trošak, zamjenjujemo trenutni najbolji raspored
        if susjed_trosak < najbolji_trosak:
            najbolji_raspored = susjed_raspored
            najbolji_trosak = susjed_trosak
            spremi_raspored(najbolji_raspored, sln_file_path)  # Spremi novi najbolji raspored
    if os.path.exists(privremeni_file_path):
        os.remove(privremeni_file_path)
        
    return najbolji_raspored, najbolji_trosak

##Algoritam ponavljamo sve dok ne pronađemo prvog poboljšavajućeg susjeda

def lokalno_pretrazivanje_1_2(podaci, sln_file_path):
    # Generiraj početni random raspored i pohrani ga
    pocetni_raspored = generiraj_pocetni_random_raspored(podaci)
    spremi_raspored(pocetni_raspored, sln_file_path)
    
    # Izračunaj trošak početnog rasporeda
    najbolji_trosak = trosak_narusavanja_mekih_uvjeta(sln_file_path, podaci)
    najbolji_raspored = copy.deepcopy(pocetni_raspored)
    
    while True:
        # Kreiramo susjeda i pohranjujemo ga u privremenu .sln datoteku
        susjed_raspored = kreiraj_susjeda1(najbolji_raspored, podaci)
        privremeni_file_path = sln_file_path.replace('.sln', '_temp.sln')
        spremi_raspored(susjed_raspored, privremeni_file_path)

        # Izračunaj trošak susjednog rasporeda
        susjed_trosak = trosak_narusavanja_mekih_uvjeta(privremeni_file_path, podaci)
        
        # Ako susjed ima manji trošak, zamjenjujemo trenutni najbolji raspored i završavamo pretragu
        if susjed_trosak < najbolji_trosak:
            najbolji_raspored = susjed_raspored
            najbolji_trosak = susjed_trosak
            spremi_raspored(najbolji_raspored, sln_file_path)  # Spremi novi najbolji raspored
            break

    # Brisanje privremene datoteke ako postoji
    if os.path.exists(privremeni_file_path):
        os.remove(privremeni_file_path)
        
    return najbolji_raspored, najbolji_trosak


"""""""""""""""""""""""""""""""""Lokalno pretraživanje koje koristi random zamjenu učionice i termina od 2 događaja"""""""""""""""""""""""""""""""""""""""""""""""


#Algoritam ponavljamo sve dok ne pronađemo najboljeg poboljšavajućeg susjeda (ograničili smo se na 100 iteracija)

def kreiraj_susjeda2(raspored, podaci):
    # Kreira susjeda mijenjanjem termina i učionice nasumičnom događaju
    susjed_raspored = copy.deepcopy(raspored)
    num_events = podaci['num_events']
    
    random_event = random.randint(0, num_events - 1)
    trenutni_termin, trenutna_ucionica = raspored[random_event]
    
    # Generiramo novi termin i učionicu s provjerom da bar jedno od njih bude različito
    novi_termin, novi_ucionica = trenutni_termin, trenutna_ucionica
    while novi_termin == trenutni_termin and novi_ucionica == trenutna_ucionica:
        novi_termin = random.randint(0, 44)  # 5 dana * 9 termina po danu
        novi_ucionica = random.randint(0, podaci['num_rooms'] - 1)
    
    susjed_raspored[random_event] = (novi_termin, novi_ucionica)
    return susjed_raspored


def lokalno_pretrazivanje_2_1(podaci, sln_file_path):
    # Generiraj početni random raspored i pohrani ga
    pocetni_raspored = generiraj_pocetni_random_raspored(podaci)
    spremi_raspored(pocetni_raspored, sln_file_path)
    
    # Izračunaj trošak početnog rasporeda
    najbolji_trosak = trosak_narusavanja_mekih_uvjeta(sln_file_path, podaci)
    najbolji_raspored = copy.deepcopy(pocetni_raspored)
    
    # Postavljamo maksimalan broj iteracija
    max_iteracija = 100
    iteracija = 0

    while iteracija < max_iteracija:
        iteracija += 1
        
        # Kreiramo susjeda i pohranjujemo ga u privremenu .sln datoteku
        susjed_raspored = kreiraj_susjeda2(najbolji_raspored, podaci)
        privremeni_file_path = sln_file_path.replace('.sln', '_temp.sln')
        spremi_raspored(susjed_raspored, privremeni_file_path)

        # Izračunaj trošak susjednog rasporeda
        susjed_trosak = trosak_narusavanja_mekih_uvjeta(privremeni_file_path, podaci)
        
        # Ispis troška trenutnog i susjednog rasporeda
        trenutni_trosak = najbolji_trosak
        #print(f"Iteracija {iteracija}: Trenutni trošak = {trenutni_trosak}, Susjedni trošak = {susjed_trosak}")
        
        # Ako susjed ima manji trošak, zamjenjujemo trenutni najbolji raspored
        if susjed_trosak < najbolji_trosak:
            najbolji_raspored = susjed_raspored
            najbolji_trosak = susjed_trosak
            spremi_raspored(najbolji_raspored, sln_file_path)  # Spremi novi najbolji raspored
    
    # Brisanje privremene datoteke ako postoji
    if os.path.exists(privremeni_file_path):
        os.remove(privremeni_file_path)
        
        
    return najbolji_raspored, najbolji_trosak


##Algoritam ponavljamo sve dok ne pronađemo prvog poboljšavajućeg susjeda 

def lokalno_pretrazivanje_2_2(podaci, sln_file_path):
    # Generiraj početni random raspored i pohrani ga
    pocetni_raspored = generiraj_pocetni_random_raspored(podaci)
    spremi_raspored(pocetni_raspored, sln_file_path)
    
    # Izračunaj trošak početnog rasporeda
    najbolji_trosak = trosak_narusavanja_mekih_uvjeta(sln_file_path, podaci)
    najbolji_raspored = copy.deepcopy(pocetni_raspored)
    
    # Iteracija za pronalazak prvog poboljšavajućeg susjeda
    while True:
        # Kreiramo susjeda i pohranjujemo ga u privremenu .sln datoteku
        susjed_raspored = kreiraj_susjeda2(najbolji_raspored, podaci)
        privremeni_file_path = sln_file_path.replace('.sln', '_temp.sln')
        spremi_raspored(susjed_raspored, privremeni_file_path)

        # Izračunaj trošak susjednog rasporeda
        susjed_trosak = trosak_narusavanja_mekih_uvjeta(privremeni_file_path, podaci)
        
        # Ispis troška trenutnog i susjednog rasporeda
        trenutni_trosak = najbolji_trosak
        #print(f"Trenutni trošak = {trenutni_trosak}, Susjedni trošak = {susjed_trosak}")
        
        # Ako susjed ima manji trošak, zamjenjujemo trenutni najbolji raspored i završavamo pretragu
        if susjed_trosak < najbolji_trosak:
            najbolji_raspored = susjed_raspored
            najbolji_trosak = susjed_trosak
            spremi_raspored(najbolji_raspored, sln_file_path)  # Spremi novi najbolji raspored
            break

    # Brisanje privremene datoteke ako postoji
    if os.path.exists(privremeni_file_path):
        os.remove(privremeni_file_path)
        
    return najbolji_raspored, najbolji_trosak



################################################### PROVEDBA ####################################################################

# UPIŠITE VAŠU PUTANJU DO MAPE U KOJOJ SE NALAZE DATOTEKE DATASETS I VALIDATOR !
path = r'C:\Users\Administrator\Desktop\Heuristički algoritmi'

path_datasets = os.path.join(path, 'datasets')

#Stvaramo datoteke u koje spremamo rješenja algoritama
path_greedy = os.path.join(path, 'Greedy algoritam')
path_local1=os.path.join(path, 'Lokalno pretraživanje 1 (najbolji poboljšavajući susjed)')
path_local2=os.path.join(path, 'Lokalno pretraživanje 2 (najbolji poboljšavajući susjed)')
path_local1_=os.path.join(path, 'Lokalno pretraživanje 1 (prvi poboljšavajući susjed)')
path_local2_=os.path.join(path, 'Lokalno pretraživanje 2 (prvi poboljšavajući susjed)')

#U tekstualne datoteke spremamo informacije: naziv datoteke za koju smo napravili raspored, udaljenost do dopustivosti tog rasporeda, trošak narušavanja mekih uvjeta te sumu prethodna 2 izračuna
informacije_greedy_putanja=os.path.join(path_greedy, 'Informacije.txt')
informacije_local1_putanja=os.path.join(path_local1, 'Informacije.txt')
informacije_local2_putanja=os.path.join(path_local2, 'Informacije.txt')
informacije_local1_putanja_=os.path.join(path_local1_, 'Informacije.txt')
informacije_local2_putanja_=os.path.join(path_local2_, 'Informacije.txt')

#Kreirajmo mapu Greedy algoritam u koju ćemo spremati rasporede dobivene greedy algoritmom za sve datasetove
if not os.path.exists(path_greedy):
    os.makedirs(path_greedy)
    
#Kreirajmo mapu Lokalno pretraživanje 1 (1 - susjeda kreiramo tako da iz rasporeda dvama nasumičnim događajima zamjenimo termin i učionicu) u koju ćemo spremati rasporede dobivene local1 algoritmom za sve datasetove, koristimo najboljeg poboljšavajućeg susjeda)
if not os.path.exists(path_local1):
    os.makedirs(path_local1)
    
#Kreirajmo mapu Lokalno pretraživanje 2 (2 - susjeda kreiramo tako da iz rasporeda nasumičnom događaju pridjelimo novi termin i učionicu) u koju ćemo spremati rasporede dobivene local2 algoritmom za sve datasetove, koristimo najboljeg poboljšavajućeg susjeda)
if not os.path.exists(path_local2):
    os.makedirs(path_local2)
    
#Kreirajmo mapu Lokalno pretraživanje 1 (1 - susjeda kreiramo tako da iz rasporeda dvama nasumičnim događajima zamjenimo termin i učionicu) u koju ćemo spremati rasporede dobivene local1 algoritmom za sve datasetove, koristimo prvog poboljšavajućeg susjeda)
if not os.path.exists(path_local1_):
    os.makedirs(path_local1_)
    
#Kreirajmo mapu Lokalno pretraživanje 2 (2 - susjeda kreiramo tako da iz rasporeda nasumičnom događaju pridjelimo novi termin i učionicu) u koju ćemo spremati rasporede dobivene local2 algoritmom za sve datasetove, koristimo prvog poboljšavajućeg susjeda)
if not os.path.exists(path_local2_):
    os.makedirs(path_local2_)
    
    
with open(informacije_greedy_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_local1_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")
            
with open(informacije_local2_putanja, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")
    
with open(informacije_local1_putanja_, 'a') as file:
            file.write("Naziv datoteke    Udaljenost do dopustivosti(u)    Trošak narušavanja mekih uvjeta(t)       u + t \n")

with open(informacije_local2_putanja_, 'a') as file:
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
            print("-----Greedy algoritam:")
        
            sln_file_path = os.path.join(os.path.dirname(file_path).replace('datasets', 'Greedy algoritam'), os.path.basename(file_path).replace('.tim', '.sln'))
            podaci=read_tim_file(file_path)
            schedule_output = greedy_schedule(podaci, sln_file_path)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću greedy algoritma:")
            raspored = ucitaj_raspored(sln_file_path)
            is_valid = provjera_dopustivosti(raspored, podaci)

            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path,podaci)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Greedy algoritam,no s ekstenzijom .txt ,a ne .sln:
            output_file_path = sln_file_path.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path,output_file_path)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u=udaljenost_do_dopustivosti(sln_file_path,podaci)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t=trosak_narusavanja_mekih_uvjeta(sln_file_path,podaci)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name = os.path.splitext(os.path.basename(sln_file_path))[0]
            with open(informacije_greedy_putanja, 'a') as file:
                        file.write(f"{file_name}                {u}                                {t}                       {u+t}\n")
                        
            
            
            
            
            print("\n-----Lokalno pretraživanje 1 (najbolji poboljšavajući susjed):")
            sln_file_path1 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Lokalno pretraživanje 1 (najbolji poboljšavajući susjed)'), os.path.basename(file_path).replace('.tim', '.sln'))
            najbolji_raspored1, loc1 = lokalno_pretrazivanje_1_1(podaci, sln_file_path1)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću prvog lokalnog pretraživanja:")
            raspored1 = ucitaj_raspored(sln_file_path1)
            is_valid1 = provjera_dopustivosti(raspored1, podaci)
            
            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path1,podaci)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Lokalno pretraživanje 1,no s ekstenzijom .txt ,a ne .sln:
            output_file_path1 = sln_file_path1.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path1,output_file_path1)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u1=udaljenost_do_dopustivosti(sln_file_path1,podaci)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t1=trosak_narusavanja_mekih_uvjeta(sln_file_path1,podaci)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name1 = os.path.splitext(os.path.basename(sln_file_path1))[0]
            with open(informacije_local1_putanja, 'a') as file:
                        file.write(f"{file_name}                {u1}                                {t1}                       {u1+t1}\n")
                        
            
            
            
            print("\n-----Lokalno pretraživanje 2 (najbolji poboljšavajući susjed):")
            sln_file_path2 = os.path.join(os.path.dirname(file_path).replace('datasets', 'Lokalno pretraživanje 2 (najbolji poboljšavajući susjed)'), os.path.basename(file_path).replace('.tim', '.sln'))
            najbolji_raspored2, loc2 = lokalno_pretrazivanje_2_1(podaci, sln_file_path2)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću drugog lokalnog pretraživanja:")
            raspored2 = ucitaj_raspored(sln_file_path2)
            is_valid2 = provjera_dopustivosti(raspored2, podaci)
            
            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path2,podaci)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Lokalno pretraživanje 1,no s ekstenzijom .txt ,a ne .sln:
            output_file_path2 = sln_file_path2.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path2,output_file_path2)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u2=udaljenost_do_dopustivosti(sln_file_path2,podaci)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t2=trosak_narusavanja_mekih_uvjeta(sln_file_path2,podaci)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name2 = os.path.splitext(os.path.basename(sln_file_path2))[0]
            with open(informacije_local2_putanja, 'a') as file:
                        file.write(f"{file_name}                {u2}                                {t2}                       {u2+t2}\n")
                          
            
            if loc2<loc1:
                print("Bolji rezultat dalo je lokalno pretraživanje koje koristi random zamjenu 2 susjeda.")
            if loc1<loc2:
                print("Bolji rezultat dalo je lokalno pretraživanje koje koristi random zamjenu termina i učionice jednog događaja.")
            if loc2==loc1:
                print("Oba načina lokalnog pretraživanja dala su isti rezultat.")
            
            
            
            
            
            print("\n-----Lokalno pretraživanje 1 (prvi poboljšavajući susjed):")
            sln_file_path1_ = os.path.join(os.path.dirname(file_path).replace('datasets', 'Lokalno pretraživanje 1 (prvi poboljšavajući susjed)'), os.path.basename(file_path).replace('.tim', '.sln'))
            najbolji_raspored1_, loc1_ = lokalno_pretrazivanje_1_2(podaci, sln_file_path1_) 
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću prvog lokalnog pretraživanja:")
            raspored1_ = ucitaj_raspored(sln_file_path1_)
            is_valid1_ = provjera_dopustivosti(raspored1_, podaci)
            
            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path1_,podaci)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Lokalno pretraživanje 1,no s ekstenzijom .txt ,a ne .sln:
            output_file_path1_ = sln_file_path1_.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path1_,output_file_path1_)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u1_=udaljenost_do_dopustivosti(sln_file_path1_,podaci)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t1_=trosak_narusavanja_mekih_uvjeta(sln_file_path1_,podaci)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name1_ = os.path.splitext(os.path.basename(sln_file_path1_))[0]
            with open(informacije_local1_putanja_, 'a') as file:
                        file.write(f"{file_name}                {u1_}                                {t1_}                       {u1_+t1_}\n")
                        
            
            
            
            print("\n-----Lokalno pretraživanje 2 (prvi poboljšavajući susjed):")
            sln_file_path2_ = os.path.join(os.path.dirname(file_path).replace('datasets', 'Lokalno pretraživanje 2 (prvi poboljšavajući susjed)'), os.path.basename(file_path).replace('.tim', '.sln'))
            najbolji_raspored2_, loc2_ = lokalno_pretrazivanje_2_2(podaci, sln_file_path2_)
            
            #Provjerimo je li raspored dopustiv:
            print("Provjera dopustivosti rasporeda kreiranog pomoću drugog lokalnog pretraživanja:")
            raspored2_ = ucitaj_raspored(sln_file_path2_)
            is_valid2_ = provjera_dopustivosti(raspored2_, podaci)
            
            #Kreirajmo valjan raspored te ga spremimo "preko" rasporeda koji nije valjan za isti dataset:
            kreiraj_valjan_raspored(sln_file_path2_,podaci)

            #Za valjan raspored ispišimo ga u tekstualnu datoteku, također u mapu Lokalno pretraživanje 1,no s ekstenzijom .txt ,a ne .sln:
            output_file_path2_ = sln_file_path2_.replace('.sln', '.txt')
            generiraj_raspored_ucionica(sln_file_path2_,output_file_path2_)

            #Izračunajmo udaljenost do dopustivosti za kreirani valjani raspored:
            u2_=udaljenost_do_dopustivosti(sln_file_path2_,podaci)

            #Izračunajmo trošak narušavanja mekih uvjeta za kreirani valjani raspored:
            t2_=trosak_narusavanja_mekih_uvjeta(sln_file_path2_,podaci)

            #Spremimo te informacije u kreiranu tekstualnu datoteku Informacije.txt
            file_name2_ = os.path.splitext(os.path.basename(sln_file_path2_))[0]
            with open(informacije_local2_putanja_, 'a') as file:
                        file.write(f"{file_name}                {u2_}                                {t2_}                       {u2_+t2_}\n")
                          
            
            if loc2_<loc1_:
                print("\n --Bolji rezultat dalo je lokalno pretraživanje koje koristi random zamjenu 2 susjeda.--")
            if loc1_<loc2_:
                print("\n--Bolji rezultat dalo je lokalno pretraživanje koje koristi random zamjenu termina i učionice jednog događaja.--")
            if loc2_==loc1_:
                print("\n--Oba načina lokalnog pretraživanja dala su isti rezultat.--")
            
            


            
            