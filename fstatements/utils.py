def calculate_trial_balance(acs):
    dr_acs = []
    cr_acs = []
    for ac in acs:
        if ac.cat in {"AS", "EX"}:
            dr_acs.append(ac)
        elif ac.cat in {"LI", "IN"}:
            cr_acs.append(ac)

    cr_acs_with_bal = [{"ac": ac, "bal": ac.bal()} for ac in cr_acs]
    dr_acs_with_bal = [{"ac": ac, "bal": ac.bal()} for ac in dr_acs]

    total_sum = {
        "cr_acs": sum(ac["bal"]["diff"] for ac in cr_acs_with_bal),
        "dr_acs": sum(ac["bal"]["diff"] for ac in dr_acs_with_bal),
    }

    return cr_acs_with_bal, dr_acs_with_bal, total_sum


def calculate_income_statement(in_ac, ex_ac):
    in_ac_with_bal = {
        "ac": in_ac,
        "bal": in_ac.bal(),
        "children": [{"ac": ca, "bal": ca.bal()} for ca in in_ac.ac_set.all()],
    }

    ex_ac_with_bal = {
        "ac": ex_ac,
        "bal": ex_ac.bal(),
        "children": [{"ac": ca, "bal": ca.bal()} for ca in ex_ac.ac_set.all()],
    }

    return ex_ac_with_bal, in_ac_with_bal


def calculate_balance_sheet(li_acs, as_acs):
    li_acs_with_bal = [
        {
            "ac": ac,
            "bal": ac.bal(),
            "children": [{"ac": ca, "bal": ca.bal()} for ca in ac.ac_set.all()],
        }
        for ac in li_acs
    ]

    as_acs_with_bal = [
        {
            "ac": ac,
            "bal": ac.bal(),
            "children": [{"ac": ca, "bal": ca.bal()} for ca in ac.ac_set.all()],
        }
        for ac in as_acs
    ]

    return as_acs_with_bal, li_acs_with_bal
