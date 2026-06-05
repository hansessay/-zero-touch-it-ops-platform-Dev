import os
import yaml


def load_access_profiles():
    env = os.getenv("APP_ENV", "dev")

    path = f"config/{env}/access_profiles.yaml"

    with open(path, "r") as f:
        return yaml.safe_load(f)