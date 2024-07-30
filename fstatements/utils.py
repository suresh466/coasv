from coasc.models import Ac


def generate_trial_balance(start_date=None, end_date=None):
    accounts = Ac.get_flat_balances(None, start_date, end_date)

    total_net_debit = sum(ac["balance"]["net_debit"] for ac in accounts)
    total_net_credit = sum(ac["balance"]["net_credit"] for ac in accounts)

    return {
        "accounts": accounts,
        "total_net_debit": total_net_debit,
        "total_net_credit": total_net_credit,
    }


def generate_balance_sheet(start_date=None, end_date=None):
    asset_accounts = Ac.get_hierarchical_balances("AS", start_date, end_date)
    liability_accounts = Ac.get_hierarchical_balances("LI", start_date, end_date)

    total_assets = sum(ac["balance"]["net_balance"] for ac in asset_accounts)
    total_liabilities = sum(ac["balance"]["net_balance"] for ac in liability_accounts)

    # rearranging as = li + eq we get as - li = eq
    equity = total_assets - total_liabilities
    total_liabilities_and_equity = total_liabilities + equity

    return {
        "asset_accounts": asset_accounts,
        "liability_accounts": liability_accounts,
        "total_assets": total_assets,
        "equity": equity,
        "total_liabilities_and_equity": total_liabilities_and_equity,
    }


def generate_income_statement(start_date=None, end_date=None):
    income_accounts = Ac.get_hierarchical_balances("IN", start_date, end_date)
    expense_accounts = Ac.get_hierarchical_balances("EX", start_date, end_date)

    total_income = sum(ac["balance"]["net_balance"] for ac in income_accounts)
    total_expenses = sum(ac["balance"]["net_balance"] for ac in expense_accounts)
    net_income = total_income - total_expenses

    return {
        "income_accounts": income_accounts,
        "expense_accounts": expense_accounts,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": net_income,
    }
