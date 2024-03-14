import os
from configparser import ConfigParser

ROOT_DIR = os.path.dirname(__file__)
PATH_TO_JSON_EMPLOYERS_ID = os.path.join(ROOT_DIR, "data/employers_id.json")


def config_database(filename="/home/sosdanil/PycharmProjects/database_coursework_5/database.ini", section="postgresql"):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db_params = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_params[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db_params
