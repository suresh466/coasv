def generate_rows(splits):
    if not splits:
        return []

    rows = []
    difference = 0
    for split in splits:
        if split.type_split == 'dr':
            difference += split.amount
            row = {
                    'debit': split.amount, 'credit': 0,
                    'difference': difference,
                    'description': split.transaction.description}
        else:
            difference -= split.amount
            row = {'debit': 0, 'credit': split.amount,
                   'difference': difference,
                   'description': split.transaction.description}
        rows.append(row)
    return rows


def generate_table(account):
    table = {
            'name': account.name, 'code': account.code,
            'rows': generate_rows(account.split_set.all()),
            'balances': account.current_balance(),
    }
    return table
