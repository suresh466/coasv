from coasc.models import Ac


def generate_trial_balance(start_date=None, end_date=None):
    accounts = Ac.get_flat_balances()

    total_net_debit = sum(ac["balance"]["net_debit"] for ac in accounts)
    total_net_credit = sum(ac["balance"]["net_credit"] for ac in accounts)

    return {
        "accounts": accounts,
        "total_net_debit": total_net_debit,
        "total_net_credit": total_net_credit,
    }


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
