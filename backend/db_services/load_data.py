import csv


def load_data_to_db(path=None, model=None):
    if path is None or model is None:
        return

    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row)
            _, created = model.objects.get_or_create(**row)
