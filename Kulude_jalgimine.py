from Kulutused import Kulud # Võtan Kulutused failist Kulud klassi
import datetime # Impordin pythoni datetime ja kalendri. Vaja on kuupäevasid kasutada
import calendar
# Vaatleb kulutusi. Võrdleb toodete hindu ja ütleb, mitu % oleksid säästnud
# kui oleksid valinud davama toote. Kui kulutusi ei ole, siis ei öelda midagi
def kulude_vaatlemine(kulutused):
    if not kulutused:
        return {}

    kulud_liigiti = {}
    soovitused = {}

    for expense in kulutused:
        kulud_liigiti.setdefault(expense.liik, []).append(expense)

    for kategooria, kategooria_kulutused in kulud_liigiti.items():
        kategooria_kulutused.sort(key=lambda x: x.hind)
        if len(kategooria_kulutused) == 1:
            odavam_toode = kallim_toode = kategooria_kulutused[0]
        else:
            odavam_toode, kallim_toode = kategooria_kulutused[:2]

        if odavam_toode.hind > 0 and kallim_toode.hind > 0:
            hinna_erinevus_protsent = ((kallim_toode.hind - odavam_toode.hind) / odavam_toode.hind) * 100
            if hinna_erinevus_protsent > 0:
                soovitused[kategooria] = f"Vali odavam {odavam_toode.nimi}. Hinnaerinevus võrreldes kallimaga: {hinna_erinevus_protsent:.2f}%."

    return soovitused
# Siin antakse kategooria ning selle kohta käiv soovitus
def kohandatud_soovitused(soovitused):
    print("Kohandatud soovitused:")
    for kategooria, soovitus in soovitused.items():
        print(f" - {kategooria}: {soovitus}")
# Main loop, kestab seni, kuni kasutaja ei taha enam andmeid sisestada
def main():
    while True:
        tee_csv_failini = "Eelarve.csv"
        eelarve = 500

        expense = kasutaja_sisestab_kulu()
        kasutaja_salvesta_csv(expense, tee_csv_failini)

        kulutused1 = kasutaja_liida_kulu(tee_csv_failini, eelarve)

        soovitused = kulude_vaatlemine(kulutused1)
        kohandatud_soovitused(soovitused) if soovitused else print("Soovitusi ei leitud.")

        kas_kinni = input("Kas lisad veel andmeid? (jah/ei): ").lower()
        if kas_kinni != 'jah':
            break
# Kasutaja saab sisestada kulu, hinna ja koguse. Kuupäev pannakse automaatselt. Kulule pannakse 3
# komakohta, kuna kütuse hind on meil kolme koma kohaga
# Liigid e. kategooriad on ette antud, et saaks kuvada soovitusi
# Kui kulu liigi number on vale, palutakse number uuesti sisestada
def kasutaja_sisestab_kulu():
    kulu_nimi = input("Sisesta kulutuse nimi: ")
    kulu_hind = float(input("Sisesta hind: "))
    kulu_kogus = float(input("Sisesta kogus: "))
    now = datetime.datetime.now()
    kuupaev = now.strftime("%Y-%m-%d")
    print(f"Sisestasid {kulu_nimi}, {kulu_kogus}, {kulu_hind:.3f}€")
    
    kulude_liigid = ["Toit ja jook", "Üür", "Kütus", "Kommunaalid", "Muud kulud"]
    while True:
        print("Palun vali kulu liik: ")
        for i, kulu_liik in enumerate(kulude_liigid, start=1):
            print(f"   {i}. {kulu_liik}")
        
        valitud = int(input(f"Palun sisesta kulu liigi ees olev number (Sobiv piirkond [1 - {len(kulude_liigid)}]): ")) - 1
        if 0 <= valitud < len(kulude_liigid):
            valitud_kululiik = kulude_liigid[valitud]
            uus_kulu = Kulud(nimi=kulu_nimi, liik=valitud_kululiik, kogus=kulu_kogus, hind=kulu_hind, kuupaev=kuupaev)
            return uus_kulu
        else:
            print("Valitud kulu liiki ei leitud, palun proovi uuesti!")

# Salvestab .csv faili. Siin lisan ka kuupäeva muutuja, et saaksin kuupäeva faili salvestada
def kasutaja_salvesta_csv(expense, tee_csv_failini):
    now = datetime.datetime.now()
    kuupaev_str = now.strftime("%Y-%m-%d")
    print(
        f"Salvestan kulutuse: {expense} asukohta {tee_csv_failini}"
    )
    with open(
        tee_csv_failini, "a"
    ) as f:  # Kui faili pole, loo see, ära kirjuta üle ("a")
        f.write(
            f"{expense.nimi},{expense.liik},{expense.kogus},{expense.hind},{kuupaev_str}\n"
        )

# Vaadatakse mis on miinimum kütuse hind ning siis arvutatakse, kui palju oleks säästnud raha
# kui oleks ostnud kütust odava hinnaga
def kytusehinna_arvutus_kuupaevaga(kulud):
    kytusehinnad = [kyts for kyts in kulud if kyts.liik == "Kütus"]
    if not kytusehinnad:
        return None
    min_kyts_hind = min(
        kytusehinnad, key=lambda x: x.hind
    )
    print(f"Kõige odavam kütusehind oli: {min_kyts_hind.hind}€/L")
    return min_kyts_hind

# Siin liidetakse kulud kokku ja prinditakse ka soovitused, mida oleks kasutaja
# võinud teisiti teha. Kütuse kohta on eraldi soovitused. Kui eelarve läheb miinusesse
# teavitatakse sellest kasutajat ja soovitatakse vähem kulutada. Veel annab programm
# teada, kui palju võid iga päev raha kulutada võttes arvesse kui palju on raha alles ning
# kui mitu päeva on kuu lõpuni. Selleks importisin calender rakenduse.
# Kulud kuvatakse liigiti. Kui liigis ei olnud ühtegi kulu (0€), siis seda ei kuvata.
# Faili ega liiki ei kirjutata üle vaid sinna lisatakse juurde. Sellest ka +=. Kui liiki
# pole olemas, tehakse see (=)
def kasutaja_liida_kulu(tee_csv_failini, eelarve):
    kulutused1: list[Kulud] = []
    
    with open(tee_csv_failini, "r") as f:
        lines = f.readlines()
        for line in lines:
            vormindus = line.strip()
            kulu_nimi, kulu_liik, kulu_kogus, kulu_hind, kuupaev = vormindus.split(",")
            line_expense = Kulud(
                nimi=kulu_nimi, liik=kulu_liik, kogus=float(kulu_kogus), hind=float(kulu_hind), kuupaev=kuupaev
            )
            kulutused1.append(line_expense)
        
    oleks_pidanud_tankima = kytusehinna_arvutus_kuupaevaga(kulutused1)

    if oleks_pidanud_tankima:
        kytusehinnad = [kyts for kyts in kulutused1 if kyts.liik == "Kütus"]
        raha_alles = eelarve - sum([kul.kogus for kul in kulutused1])

        if kytusehinnad:
            min_kyts_hind = min([kul.hind for kul in kytusehinnad])
            säästetud_nuts = (
                raha_alles
                + (min_kyts_hind - oleks_pidanud_tankima.hind)
                * oleks_pidanud_tankima.kogus
            )
            if säästetud_nuts > 0:
                print(
                    f"Kui oleksid tankinud kõige odavama kütusehinna ajal, oleksid säästnud {säästetud_nuts:.2f}€."
                )
                print(
                    "Soovitan tankida kütust rohkem siis, kui hind on odav. Kui tundub, et hind on tavalisest odavam, varu kütust kanistritesse"
                )
            else:
                print(
                    "Säästu ei ole."
                )
        else:
            print("Kütusehinda ei leitud.")
    else:
        print("Kütusehinda ei leitud.")

    kulud_liigiti = {}
    for expense in kulutused1:
        key = expense.liik
        if key in kulud_liigiti:
            kulud_liigiti[key].append(expense)
        else:
            kulud_liigiti[key] = [expense]

    print("Kulud liigiti: ")
    for key, kogus in kulud_liigiti.items():
        kulud_kokku = sum([kul.kogu_maksumus for kul in kulutused1])
        print(f"  {key}: {kulud_kokku:.2f}€")

    kulude_summa = sum([kul.kogu_maksumus for kul in kulutused1])
    print(f"Oled sellel kuul kokku kulutanud {kulude_summa:.2f}€")

    raha_alles = eelarve - kulude_summa
    if raha_alles < 0:
        print(
            f"EELARVE ON MIINUSES!!! Sinu eelarve oli: {eelarve:.2f}€, kuid sa kulutasid {kulude_summa:.2f}€ rohkem!!!"
        )
        print(
            "1. Hoia suurte kulutuste pealt kokku. Kas kõik kulutused olid vajalikud?"
        )
        print(
            "2. Kas tarbisid teenuseid või tooteid, millele on odavamad alternatiivid?"
        )
    else:
        print(f"Sul on sel kuul veel {raha_alles:.2f}€ alles!")

        # Praegune aeg ja kuupäev
        now = datetime.datetime.now()
        # Mitu päeva on käesoleval kuul
        paevi_kuus = calendar.monthrange(now.year, now.month)[1]
        # Mitu päeva kuu lõpuni
        kuu_lopuni = paevi_kuus - now.day

        päeva_eelarve = raha_alles / kuu_lopuni
        print(f"Sinu päevane eelarve on {päeva_eelarve:.2f}€")
        print(f"Käesolev kuu kestab veel {kuu_lopuni} päeva.")

        soovitused = kulude_vaatlemine(kulutused1)
        kohandatud_soovitused(soovitused) if soovitused else print("Soovitusi ei leitud.") # Pole veel jõudnud soovitusi lisada, paar kohandatud soovitust siiski on


if __name__ == "__main__":  # Tõene ainult kui paneme selle faili käima
    main()
