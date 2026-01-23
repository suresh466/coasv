from django.db import transaction as db_transaction
from decimal import Decimal as Dec
from coasc.models import Ac, Transaction, Split
from datetime import timedelta
from django.utils import timezone


def generate_specific_dates(base_date):
    # Last week: Transactions 1-5
    # Last month: Transactions 1-7
    # Last quarter: Transactions 1-9
    # Last half-year: Transactions 1-12
    # Last year: All transactions

    dates = []

    # 1: Today
    dates.append((base_date, "Today"))

    # 2: One day back
    dates.append((base_date - timedelta(days=1), "1 day ago"))

    # 3: Two days back
    dates.append((base_date - timedelta(days=2), "2 days ago"))

    # 4: Mid-week (assuming 3 days back)
    dates.append((base_date - timedelta(days=3), "Mid-week (3 days ago)"))

    # 5: A week ago
    dates.append((base_date - timedelta(weeks=1), "1 week ago"))

    # 6: 15 days ago
    dates.append((base_date - timedelta(days=15), "15 days ago"))

    # 7: A month ago
    dates.append((base_date - timedelta(days=30), "1 month ago"))

    # 8: Two months ago
    dates.append((base_date - timedelta(days=60), "2 months ago"))

    # 9: 3 months ago
    dates.append((base_date - timedelta(days=90), "3 months ago"))

    # 10: 4 months ago
    dates.append((base_date - timedelta(days=120), "4 months ago"))

    # 11: 5 months ago
    dates.append((base_date - timedelta(days=150), "5 months ago"))

    # 12: 6 months ago
    dates.append((base_date - timedelta(days=180), "6 months ago"))

    # 13: 7 months ago
    dates.append((base_date - timedelta(days=210), "7 months ago"))

    # 14: 8 months ago
    dates.append((base_date - timedelta(days=240), "8 months ago"))

    # 15: 9 months ago
    dates.append((base_date - timedelta(days=270), "9 months ago"))

    # 16: 10 months ago
    dates.append((base_date - timedelta(days=300), "10 months ago"))

    # 17: 11 months ago
    dates.append((base_date - timedelta(days=330), "11 months ago"))

    # 18: 11 months and 15 days ago
    dates.append((base_date - timedelta(days=345), "11 months and 15 days ago"))

    # 19: One week less than a year ago
    dates.append((base_date - timedelta(days=358), "1 week less than a year ago"))

    # 20: A year ago
    dates.append((base_date - timedelta(days=365), "1 year ago"))

    return dates


def create_tx(desc, date):
    return Transaction.objects.create(desc=desc, tx_date=date)


def get_ac(code):
    return Ac.objects.get(code=str(code))


def generate_split(ac, t_sp, am, tx):
    Split.objects.create(ac=ac, t_sp=t_sp, am=Dec(am), tx=tx)


txs_data = [
    {
        "sharebikri tatha prabesh shulkabapat nagad prapta": [
            (80, "dr", 15500),
            (10, "cr", 15000),
            (160.4, "cr", 500),
        ]
    },
    {
        "nepal bank limited ma bachat khata kholi nagad jamma": [
            (100.3, "dr", 12000),
            (80, "cr", 12000),
        ]
    },
    {
        "byabasthak rammadi ghimirelai cq.01 bata saman kharid peski": [
            (120.2, "dr", 7000),
            (100.3, "cr", 7000),
        ]
    },
    {
        "jilla sahaakri sangh ko share ra bikash rinpatra nagadbata kharid": [
            (100.2, "dr", 500),
            (100.4, "dr", 1000),
            (80, "cr", 1500),
        ]
    },
    {
        "sangalna phatwari bamojim prabandha" + " raammadi ghimireko peski perchyaut": [
            (80, "dr", 500),
            (140, "dr", 3000),
            (150.1, "dr", 2500),
            (150.2, "dr", 100),
            (150.3, "dr", 1000),
            (120.2, "cr", 7000),
            (160.5, "cr", 100),
        ]
    },
    {
        "sadasyaharu bata bachat swarupnichhep prapta": [
            (80, "dr", 2500),
            (30.2, "cr", 2500),
        ]
    },
    {
        "nagad tatha udharo rammaan shresthalai saaman bikri": [
            (80, "dr", 1500),
            (120.1, "dr", 1200),
            (160.1, "cr", 2700),
        ]
    },
    {
        "nagadbata bibhinnam sirsakma kharcha": [
            (140, "dr", 1500),
            (150.5, "dr", 1000),
            (150.8, "dr", 100),
            (150.11, "dr", 400),
            (80, "cr", 3000),
        ]
    },
    {
        "suryanagar gaun bikash samitibata anudanjagga prapta": [
            (130.4, "dr", 25000),
            (20.1, "cr", 25000),
        ]
    },
    {
        "sadasyaharubata bachat swarup nichhep prapta": [
            (80, "dr", 2000),
            (30.2, "cr", 2000),
        ]
    },
    {
        "sadasya himal sapkota ra samjhana shrestha lai nagad rin bitaran": [
            (110, "dr", 3500),
            (80, "cr", 3500),
        ]
    },
    {
        "nepal bank limitedbata prapta bechbikhan rin bachat khatama jamma": [
            (100.3, "dr", 20000),
            (40, "cr", 20000),
        ]
    },
    {
        "furniture tatha safe kharidbapat milan furniture"
        + " udhyoglai cq.03 bata bhuktani ra dhuwani kharcha": [
            (130.1, "dr", 4300),
            (130.2, "dr", 2200),
            (80, "cr", 500),
            (100.3, "cr", 6000),
        ]
    },
    {
        "share bikri bapat nagad prebesh ra shulka prapta": [
            (80, "dr", 2750),
            (10, "cr", 2500),
            (160.4, "cr", 250),
        ]
    },
    {
        "krishi samagri sansthanbata udharo tatha cq.03"
        + " bata saman kharid ra nagaddhuwani kharcha": [
            (150.1, "dr", 5500),
            (150.2, "dr", 500),
            (60.1, "cr", 2000),
            (80, "cr", 500),
            (100.3, "cr", 3000),
            (160.5, "cr", 500),
        ]
    },
    {
        "dealer ramman shrestha bata udharo bikriko" + " rakam bachat khatabata jamm": [
            (100.3, "dr", 1200),
            (120.1, "cr", 1200),
        ]
    },
    {
        "sadasyaharu lai share rakam ra bachat rakam nagad firta diyeko": [
            (10, "dr", 1000),
            (30.2, "dr", 500),
            (80, "cr", 1500),
        ]
    },
    {
        "sadasya kalimohan lai rinma, sadasya bekhalallai"
        + " rinma udharoma ra nagad saman bikri": [
            (80, "dr", 2000),
            (110, "dr", 2000),
            (120.1, "dr", 1800),
            (160.1, "cr", 5800),
        ]
    },
    {
        "sadasya himlalbata rinko saba byaaj asuli ra krishi samagri"
        + " sansthan lai udharo kharidko rakam cq.04 bata bhuktani": [
            (80, "dr", 2130),
            (60.1, "dr", 2000),
            (100.3, "cr", 2000),
            (110, "cr", 2000),
            (160.2, "cr", 130),
        ]
    },
    {
        "karmachariko asar mahinako talab bhatta " + " nagadbata bhuktani ra hitkosh jamma": [
            (150.3, "dr", 6000),
            (60.3, "cr", 1000),
            (80, "cr", 5000),
        ]
    },
]

# Generate specific dates
base_date = timezone.now().date()
transaction_dates = generate_specific_dates(base_date)

# Main loop
for tx_data, (tx_date, date_description) in zip(txs_data, transaction_dates):
    for tx_desc, splits in tx_data.items():
        with db_transaction.atomic():
            tx = create_tx(tx_desc, tx_date)
            for code, t_sp, am in splits:
                generate_split(get_ac(code), t_sp, am, tx)
            Ac.validate_accounting_equation()
        print(f"Created transaction for {date_description}: {tx_date}")
