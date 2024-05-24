from coasc.models import Ac

main_accounts = {
    "Share pujji": 10,
    "Kosh": 20,
    "Nichhep/Deposit hissab": 30,
    "Rin liyeko hissab": 40,
    "Aanudan hissab(haal prayogma bhayeko)": 50,
    "Bhuktani dinuparne hissab": 60,
    "Aanya dayito hissab": 70,
    "Nagad hissab": 80,
    "Bank chalti hissab": 90,
    "Lagani hissab": 100,
    "Sadasya harulai diyeko rin": 110,
    "Paunu parne hissab": 120,
    "Furniture, sofa, sabari sadhan, ghar jaggajamin hissab": 130,
    "Aanya sampati saman hissab": 140,
    "Saman kharid tatha kharcha hissab": 150,
    "Saman bikri tatha aamdani khata": 160,
}

sub_accounts = {
    20: {
        "Jageda kosh": 20.1,
        "Aanya kosh": 20.2,
    },
    30: {
        "Chalti khata": 30.1,
        "Bachat khata": 30.2,
        "Dharauti khata": 30.3,
    },
    60: {
        "Udharo kharid ra bhuktani": 60.1,
        "Peski prapta ra phasacheut": 60.2,
        "Karmachari heet kosh": 60.3,
        "Saapati prapta ra phirta": 60.4,
        "Aanya rakam": 60.5,
    },
    70: {
        "Tirnuparne talab bhatta": 70.1,
        "Tirnuparne gharbhada": 70.2,
        "Tirnuparne byaaj": 70.3,
        "Tirnuparne lehka parichhad sulka": 70.4,
        "Tirnu parne aanya rakam": 70.5,
    },
    100: {
        "Dhitopatra kharid": 100.1,
        "Mudhati khata": 100.2,
        "Bachat khata": 100.3,
        "Share kharid hissab": 100.4,
    },
    120: {
        "Udharo bikri ra aasuli hisaab": 120.1,
        "Peski diyeko ra phhachryot hissab": 120.2,
        "Paunu parne byaaj hissab": 120.3,
        "Heetkosh jamma": 120.4,
        "Beruju shortage hissab": 120.5,
        "Dharauti hissab": 120.6,
        "Aanibarye bachat": 120.7,
        "Aanya rakam": 120.8,
    },
    130: {
        "Furniture hissab": 130.1,
        "Safe hissab": 130.2,
        "Sabari sadhan hissab": 130.3,
        "Ghar, jagga jamin hissab": 130.4,
    },
    150: {
        "Saman kharid": "150.1",
        "Dhuwani jyala kharcha": "150.2",
        "Talab tatha bhatta kharcha": "150.3",
        "Ghar godam bhada": "150.4",
        "Masalanda kharcha": "150.5",
        "Marmar kharcha": "150.6",
        "Chalu byaaj kharcha": "150.7",
        "Bibidh kharcha": "150.8",
        "Has kharcha": "150.9",
        "Indhan kharcha": "150.10",
        "Baithak bhatta kharcha": "150.11",
        "Harjana kharcha": "150.12",
        "Byaparik chutt diyeko": "150.13",
    },
    160: {
        "Saaman bikri": 160.1,
        "Rinbata byaj prapta": 160.2,
        "Lagani bata byaaj prapta": 160.3,
        "Bibidh aamdani": 160.4,
        "Byaparik chutt prapta": 160.5,
        "Prasasanik aanudaan prapta": 160.6,
    },
}

"""
personal_ac = {
        'Suresh Thagunna': ['Badaipur', 110.001],
        'Deepak Thagunna': ['Badaipur', 110.002],
        'Niraj Pal': ['Pipraya', 110.003],
        'Krish Pal': ['Pipraya', 110.004],
        'Ram Singh': ['Odali', 110.005],
        'Shyam Pokhrel': ['Kathmandu', 110.006],
        }
"""

for name, code in main_accounts.items():
    main_ac = Ac(name=name, code=code, t_ac="I")
    if code <= 70:
        main_ac.cat = "LI"
    if code > 70 and code <= 140:
        main_ac.cat = "AS"
    if code > 140 and code <= 150:
        main_ac.cat = "EX"
    if code > 150 and code <= 160:
        main_ac.cat = "IN"
    main_ac.save()

    for main_code, sub_ac in sub_accounts.items():
        if main_code != main_ac.code:
            continue
        for name, code in sub_ac.items():
            Ac.objects.get_or_create(name=name, code=str(code), p_ac=main_ac)
