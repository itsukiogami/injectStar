import utils.config_actions as config_actions
import argparse

def main():
    config_actions.make_configMulti('./')
    config_actions.make_config('./')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Use prepareWorkspace.py to create (or reinitialise) config files.')
    args = parser.parse_args()
    main()