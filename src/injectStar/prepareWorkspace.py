import argparse
import injectStar.utils.config_actions as config_actions


def main(args):
    config_actions.make_config_multi('./')
    config_actions.make_config('./')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Use prepareWorkspace.py to create '
        '(or reinitialise) config files.'
        )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
