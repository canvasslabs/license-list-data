import os
import json
import argparse
import sys


JSON_PATH = 'json'
JSON_CUSTOM_PATH = 'custom/'
JSON_LICENSE_PATH = 'details/'
JSON_EXCEPTION_PATH = 'exceptions/'
JSON_ADAPTION_PATH = 'adaptions/'
JSON_LICENSE_FIELDS = ['name', 'licenseText', 'standardLicenseHeader',
          'standardLicenseTemplate', 'standardLicenseHeaderTemplate', 'seeAlso']
JSON_EXCEPTION_FIELDS = ['name', 'licenseExceptionText', 'licenseExceptionTemplate', 'seeAlso']


def init_custom(shortname, is_exception):
    fpath = os.path.join(JSON_PATH, JSON_CUSTOM_PATH, shortname)
    os.makedirs(fpath, exist_ok=True)
    json_fields = JSON_EXCEPTION_FIELDS if is_exception == 'exc' else JSON_LICENSE_FIELDS
    for field in json_fields:
        _init_file(os.path.join(fpath, field))


def _init_file(path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('')


def add_custom(shortname):
    custom_path = os.path.join(JSON_PATH, JSON_CUSTOM_PATH)
    if shortname is None:
        shortname_list = os.listdir(custom_path)
        shortname_list = [shortname for shortname in shortname_list if not shortname.endswith('.json')]
    else:
        shortname_list = [shortname]
    for shortname in shortname_list:
        dic = {}
        fpath = os.path.join(custom_path, shortname)
        for field in JSON_LICENSE_FIELDS:
            with open(os.path.join(fpath, field), 'r') as f:
                if field == 'seeAlso':
                    field_text = f.read().splitlines()
                else:
                    field_text = f.read()

            dic[field] = field_text
            for field, text in dic.items():
                if type(text) is str:
                    dic[field] = text.strip()
        if 'licenseText' in dic:
            dic['licenseId'] = shortname
        else:
            dic['licenseExceptionId'] = shortname

        _update_references(dic)
        license_path = os.path.join(JSON_PATH, JSON_CUSTOM_PATH, shortname + '.json')
        dic_text = json.dumps(dic, indent=2)
        with open(license_path, 'w') as f:
            f.write(dic_text)


def _update_references(fields):
    fpath = os.path.join(JSON_PATH, 'custom.json')
    with open(fpath, 'r') as f:
        all_dic = json.load(f)
    licenses = {lic['name']: lic for lic in all_dic['licenses']}
    new_dic = {}
    new_dic['reference'] = fields['seeAlso'][0:1]
    new_dic['name'] = fields['name']
    new_dic['licenseId'] = fields['licenseId']
    new_dic['seeAlso'] = fields['seeAlso'][1:]
    licenses[fields['name']] = new_dic
    all_dic['licenses'] = list(licenses.values())
    all_dic_text = json.dumps(all_dic, indent=2)
    with open(fpath, 'w') as f:
        f.write(all_dic_text)


def init_adaption(shortname, fields):
    fpath = os.path.join(JSON_PATH, JSON_ADAPTION_PATH, shortname)
    fields = dict(fields)
    is_exception = True if fields['is_exception'] == 'exc' else False
    json_fields = JSON_EXCEPTION_FIELDS if is_exception else JSON_LICENSE_FIELDS
    os.makedirs(fpath, exist_ok=True)
    # force to init files
    if is_exception:
        fields['licenseExceptionTemplate'] = True
    else:
        fields['standardLicenseTemplate'] = True
    is_empty = True
    for field, has_field in fields.items():
        if field in json_fields and has_field:
            _init_file(os.path.join(fpath, field))
            is_empty = False
    if is_empty:
        try:
            os.rmdir(fpath)
        except:
            pass
        print('Please specify field names for initialization.')


def add_adaption(shortname, note):
    fields = os.listdir(os.path.join(JSON_PATH, JSON_ADAPTION_PATH, shortname))
    is_exception = True if 'licenseExceptionTemplate' in fields else False
    json_fields = JSON_EXCEPTION_FIELDS if is_exception else JSON_LICENSE_FIELDS
    json_license_path = JSON_EXCEPTION_PATH if is_exception else JSON_LICENSE_PATH
    fpath = os.path.join(JSON_PATH, json_license_path, shortname + '.json')
    with open(fpath, 'r') as f:
        dic = json.load(f)

    fpath = os.path.join(JSON_PATH, JSON_ADAPTION_PATH, shortname)
    for field in json_fields:
        field_path = os.path.join(fpath, field)
        if not os.path.exists(field_path):
            continue
        with open(field_path, 'r') as f:
            if field == 'seeAlso':
                field_text = f.read().splitlines()
            else:
                field_text = f.read()

        dic[field] = field_text
        for field, text in dic.items():
            if type(text) is str:
                dic[field] = text.strip()

    _update_adaption(shortname, note)

    license_path = os.path.join(JSON_PATH, JSON_ADAPTION_PATH, shortname + '.json')
    dic_text = json.dumps(dic, indent=2)
    with open(license_path, 'w') as f:
        f.write(dic_text)


def _update_adaption(shortname, note):
    fpath = os.path.join(JSON_PATH, 'adaptions.json')
    with open(fpath, 'r') as f:
        all_dic = json.load(f)
    adaptions = {lic['licenseId']: lic for lic in all_dic['adaptions']}
    if shortname in adaptions:
        dic = adaptions[shortname]
        dic['notes'].append(note)
    else:
        adaptions[shortname] = {'licenseId': shortname, 'notes': [note]}

    all_dic['adaptions'] = list(adaptions.values())
    all_dic_text = json.dumps(all_dic, indent=2)
    with open(fpath, 'w') as f:
        f.write(all_dic_text)

def _parse_args(args):
    parser = argparse.ArgumentParser(
        description="update license files and templates"
    )
    # parser.add_argument(
    #     "mode", help="update mode (\"init_custom\", \"add_custom\", \"init_adaption\", \"add_adaption\")",
    #     choices=["init_custom", "add_custom", "init_adaption", "add_adaption"])

    parser.add_argument(
        "-s", "--shortname", help="short name of the license that needs to be updated",
        )
    subparsers = parser.add_subparsers(dest='mode', help='sub-command help', required=True)

    parser_init_custom = subparsers.add_parser('init_custom', help='init custom license')
    subparsers_init_custom = parser_init_custom.add_subparsers(dest='is_exception', help='sub-command help', required=True)
    parser_init_custom_e = subparsers_init_custom.add_parser('exc', help='init custom for exception')
    parser_init_custom_l = subparsers_init_custom.add_parser('lic', help='init custom for license')

    parser_add_custom = subparsers.add_parser('add_custom', help='add custom license')

    parser_init_adaption = subparsers.add_parser('init_adaption', help='init field adaption')
    subparsers_adaption = parser_init_adaption.add_subparsers(dest='is_exception', help='sub-command help', required=True)
    parser_init_adaption_e = subparsers_adaption.add_parser('exc', help='init field adaption for exception')
    # parser_init_adaption.add_argument(
    #     "-E", "--is-exception", help="is exception", action='store_true'
    #     )
    parser_init_adaption_e.add_argument(
        "-E", "--licenseExceptionText", help="licenseText", action='store_true'
        )
    parser_init_adaption_e.add_argument(
        "-T", "--licenseExceptionTemplate", help="standardLicenseTemplate", action='store_true'
        )
    parser_init_adaption_e.add_argument(
        "-S", "--seeAlso", help="seeAlso", action='store_true'
        )

    parser_init_adaption_l = subparsers_adaption.add_parser('lic', help='init field adaption for license')
    parser_init_adaption_l.add_argument(
        "-L", "--licenseText", help="licenseText", action='store_true'
        )
    parser_init_adaption_l.add_argument(
        "-T", "--standardLicenseTemplate", help="standardLicenseTemplate", action='store_true'
        )
    parser_init_adaption_l.add_argument(
        "-H", "--standardLicenseHeader", help="standardLicenseHeader", action='store_true'
        )
    parser_init_adaption_l.add_argument(
        "-N", "--standardLicenseHeaderTemplate", help="standardLicenseHeaderTemplate", action='store_true'
        )
    parser_init_adaption_l.add_argument(
        "-S", "--seeAlso", help="seeAlso", action='store_true'
        )

    parser_add_adaption = subparsers.add_parser('add_adaption', help='add field adaption')
    parser_add_adaption.add_argument(
        "note", help="note"
        )

    # parser_init_adaption = subparsers.add_parser('add_all', help='add all changes of customs and adaptions')
    return parser.parse_args(args)

def main():
    args = _parse_args(sys.argv[1:])
    if args.mode == "init_custom":
        init_custom(args.shortname, args.is_exception)
    elif args.mode == "add_custom":
        add_custom(args.shortname)
    elif args.mode == "init_adaption":
        init_adaption(args.shortname, args._get_kwargs())
    elif args.mode == "add_adaption":
        add_adaption(args.shortname, args.note)

if __name__ == '__main__':
    main()
