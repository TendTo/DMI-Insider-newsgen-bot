"""Used to set secret variables, like the token, in the config/settings.yaml file"""
import sys
import getopt
import yaml

help_message = "settings.py -t <token>\n\n"\
            "-t --token <token>             set the token variable\n\n"\
            "-w --webhook [enable_webhook]  set the webhook:enabled variable (defaults to false)\n"\
            "-u --url [web_url]             set the webhook:url variable\n\n"\
            "-g --groups [web_url]          set the groups variable (dealauts to allow all)\n\n"\
            "--test-api_id                  set the test:api_id variable (needed for testing)\n"\
            "--test-api_hash                set the test:api_hash variable (needed for testing)\n"\
            "--test-session                 set the test:session variable (needed for testing)\n"\
            "--test-tag                     set the test:tag variable (needed for testing)\n"\
            "--test-token                   set the test:token variable (needed for testing)\n\n"\
            "-p --path [settings_path]      set the path of the setting file (defaults to config/settings.yaml)\n" \
            "-r --revert                    set token to \"\" and enable_webhook to false"

new_token = ""
webhook_enabled = False
web_url = ""
settings_path = "config/settings.yaml"
groups = []
test_api_id = ""
test_api_hash = ""
test_session = ""
test_tag = ""
test_token = ""

try:
    # get a list of argv with the related option flag
    opts, args = getopt.getopt(sys.argv[1:], "rht:p:w:u:g:", [
        "help",
        "revert",
        "token=",
        "path=",
        "webhook=",
        "url=",
        "groups=",
        "test-api_id=",
        "test-api_hash=",
        "test-session=",
        "test-tag=",
        "test-token=",
    ])
except getopt.GetoptError:
    print(help_message)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):  # show the help prompt
        print(help_message)
        sys.exit()
    elif opt in ("-p", "--path"):  # set the settings_path value (defaults to config/settings.yaml)
        settings_path = arg

try:
    with open(settings_path, "r") as yaml_file:
        config_map = yaml.load(yaml_file, Loader=yaml.SafeLoader)
except FileNotFoundError as e:
    print(["[error] settings: " + str(e)])

for opt, arg in opts:
    if opt in ("-t", "--token"):  # set the new_token value (defaults to "")
        new_token = arg if arg != "none" else ""
    elif opt in ("-u", "--url"):  # set the web_url value to false...
        web_url = arg if arg != "none" else ""
    elif opt in ("-w", "--webhook"):  # set the webhook_enabled value to false...
        if arg.lower() in ("false", "no", "disable", "falso", "f", "n", "0", "-1"):  # if the parameter is in this list
            webhook_enabled = False
        else:
            webhook_enabled = True
    elif opt in ("-g", "--groups"):
        groups = arg.split(" ") if arg != "none" else []
    elif opt == "--test-api_id":
        test_api_id = arg
    elif opt == "--test-api_hash":
        test_api_hash = arg
    elif opt == "--test-api_id":
        test_api_id = arg
    elif opt == "--test-session":
        test_session = arg
    elif opt == "--test-tag":
        test_tag = arg
    elif opt == "--test-token":
        test_token = arg
    elif opt in ("-r", "--revert"):  # reset all values to their default
        new_token = ""
        webhook_enabled = False
        web_url = ""
        groups = []
        test_api_id = ""
        test_api_hash = ""
        test_session = ""
        test_tag = ""
        test_token = ""
        break
else:
    if not new_token:
        print("A token must provided with -t token")
        sys.exit(2)
    if webhook_enabled and not web_url:
        print("If webhook is enabled, a web_url must be provided\nYou can disable it with -w false")
        sys.exit(2)
    try:
        groups = [int(group_id) for group_id in groups]
    except ValueError:
        print("[error] groups must be integers")
    try:
        test_api_id = int(test_api_id)
    except ValueError:
        print("[error] test_api_id must be integers")

with open(settings_path, 'w') as yaml_file:
    config_map['token'] = new_token
    config_map['webhook']['enabled'] = webhook_enabled
    config_map['webhook']['url'] = web_url
    config_map['groups'] = groups
    config_map['test']['api_id'] = test_api_id
    config_map['test']['api_hash'] = test_api_hash
    config_map['test']['session'] = test_session
    config_map['test']['tag'] = test_tag
    config_map['test']['token'] = test_token
    yaml.dump(config_map, yaml_file)
