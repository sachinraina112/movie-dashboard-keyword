import os

import yaml

_fpath = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(_fpath) as fp:
    config = yaml.safe_load(fp)
    api_config = config['api_config']
