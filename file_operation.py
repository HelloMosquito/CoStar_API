import json
import csv


def file_read(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return html


def save_json(json_file_path, json_file_name, content):
    with open(json_file_path + json_file_name + '.json', 'w') as fw:
        json.dump(content, fw)


def json_to_csv(json_file, csv_file_path, csv_file_name):
    with open(json_file, 'r') as fr:
        data = fr.read()

    json_data = json.loads(data)

    with open(csv_file_path + csv_file_name + '.csv', 'w', encoding='utf-8',
              newline="") as csvfw:
        fieldnames = json_data[0].keys()
        writer = csv.DictWriter(csvfw, fieldnames=fieldnames)
        writer.writeheader()
        for item in json_data:
            writer.writerow(item)
