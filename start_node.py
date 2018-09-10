import os
import sys
import json
import yaml
import argparse
from munch import DefaultMunch

from spletnya.spletnya_node import SpletnyaNode
from spletnya.exceptions import Misconfiguration

import logging
logger = logging.getLogger(__name__)

def run(cfg):
    engine = SpletnyaNode(cfg)
    engine.run()

def get_config():
    parser = argparse.ArgumentParser(description='Trading Engine named Strela')
    parser.add_argument('-config', help='a path to configuration file')

    args = parser.parse_args()
    filename = args.config

    if os.path.exists(filename):
        with open(filename, 'r') as ymlfile:
            try:
                cfg_dict = yaml.load(ymlfile)
            except yaml.YAMLError:
                raise Misconfiguration("Unable to attach a config")
            return DefaultMunch.fromDict(cfg_dict, None)
    else:
        raise Misconfiguration("Unable to find config {}".format(filename))

def start_node():
    try:
        cfg = get_config()
    except Misconfiguration as err:
        print("Program will be stopped. Reason: {}".format(err))
        exit(0)

    logger_level = {
        "DEBUG":   logging.DEBUG,
        "INFO" :   logging.INFO,
        "WARNING": logging.WARNING,
        "WARNING": logging.ERROR
    }

    if cfg.logger is None:
        print("Program will be stopped. Reason: Config does not contain a logger info")
        exit(1)
    if cfg.logger.path is None or cfg.logger.level is None:
        print("Program will be stopped. Reason: Config does not contain a logger path or level")
        exit(1)


    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=cfg.logger.path, level=logger_level[cfg.logger.level])

    logger = logging.getLogger(__name__)
    logger.info("Spletny poshli!")
    logger.info("Configurations: {}".format(json.dumps(cfg)))
    run(cfg)

if __name__ == "__main__":
    print('Spletnya started')
    sys.stdout.flush()
    start_node()

