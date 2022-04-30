import json

def list_of_all_files(json_file_name):

    # list of all the files
    all_files = list()

    # load json file
    file = open("permissions.json")
    data = json.load(file)

    # get all names
    for i in data['name']:
        all_files.append(i)

    # return all the files
    return all_files
