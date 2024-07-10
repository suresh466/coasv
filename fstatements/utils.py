from coasc.models import Ac


def calculate_trial_balance(start_date=None, end_date=None):
    dr_acs = Ac.objects.filter(cat__in=["AS", "EX"])
    cr_acs = Ac.objects.filter(cat__in=["LI", "IN"])

    cr_acs_with_bal = [{"ac": ac, "bal": ac.bal(start_date, end_date)} for ac in cr_acs]
    dr_acs_with_bal = [{"ac": ac, "bal": ac.bal(start_date, end_date)} for ac in dr_acs]

    total_sum = {
        "cr_acs": sum(ac["bal"]["diff"] for ac in cr_acs_with_bal),
        "dr_acs": sum(ac["bal"]["diff"] for ac in dr_acs_with_bal),
    }

    return cr_acs_with_bal, dr_acs_with_bal, total_sum


def calculate_balance_sheet(start_date=None, end_date=None):
    as_acs = Ac.objects.filter(cat="AS")
    li_acs = Ac.objects.filter(cat="LI")

    li_acs_with_bal = [
        {
            "ac": ac,
            "bal": ac.bal(start_date, end_date),
            "children": [
                {"ac": ca, "bal": ca.bal(start_date, end_date)}
                for ca in ac.ac_set.all()
            ],
        }
        for ac in li_acs
    ]
    as_acs_with_bal = [
        {
            "ac": ac,
            "bal": ac.bal(start_date, end_date),
            "children": [
                {"ac": ca, "bal": ca.bal(start_date, end_date)}
                for ca in ac.ac_set.all()
            ],
        }
        for ac in as_acs
    ]

    as_total_bal = Ac.total_bal("AS", start_date, end_date)
    li_total_bal = Ac.total_bal("LI", start_date, end_date)

    return as_acs_with_bal, li_acs_with_bal, as_total_bal, li_total_bal


def calculate_income_statement(start_date=None, end_date=None):
    in_ac = Ac.objects.get(cat="IN")
    ex_ac = Ac.objects.get(cat="EX")

    in_ac_with_bal = {
        "ac": in_ac,
        "bal": in_ac.bal(start_date, end_date),
        "children": [
            {"ac": ca, "bal": ca.bal(start_date, end_date)} for ca in in_ac.ac_set.all()
        ],
    }

    ex_ac_with_bal = {
        "ac": ex_ac,
        "bal": ex_ac.bal(start_date, end_date),
        "children": [
            {"ac": ca, "bal": ca.bal(start_date, end_date)} for ca in ex_ac.ac_set.all()
        ],
    }

    return ex_ac_with_bal, in_ac_with_bal
