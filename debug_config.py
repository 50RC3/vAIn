import configparser
import json
import yaml
import os

def load_ini_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def load_json_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def load_yaml_config(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    # Load configurations
    ini_config = load_ini_config('/c:/Users/Mr.V/Desktop/vAIn/configs/hive_mind_config.ini')
    json_config = load_json_config('/c:/Users/Mr.V/Desktop/vAIn/.vscode/settings.json')
    yaml_config = load_yaml_config('/C:/Users/Mr.V/Desktop/vAIn/configs/db_config.yaml')

    # Print configurations
    print("INI Configuration:")
    for section in ini_config.sections():
        print(f"[{section}]")
        for key, value in ini_config.items(section):
            print(f"{key} = {value}")
        print()

    print("JSON Configuration:")
    print(json.dumps(json_config, indent=4))
    print()

    print("YAML Configuration:")
    print(yaml.dump(yaml_config, indent=4))
