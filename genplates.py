#!/usr/bin/python
# Copyright 2017 8c30ff1057d69a6a6f6dc2212d8ec25196c542acb8620eb4148318a4b10dd131
#
# License AGPLv3

import sys
from jinja2 import Environment, FileSystemLoader

def python_version_check():
    v = sys.version_info

    if v.major < 3:
        print("This program requires python 3")
        sys.exit(1)

def build_lists():
    env = Environment(
        loader=FileSystemLoader('.')
    )

    template = env.get_template('easylist.j2')

    f = open("easylist.txt", "w")
    f.write(template.render())
    f.close()

    template = env.get_template('easyprivacy.j2')

    f = open("easyprivacy.txt", "w")
    f.write(template.render())
    f.close()

    template = env.get_template('fanboy-annoyance.j2')

    f = open("fanboy-annoyance.txt", "w")
    f.write(template.render())
    f.close()

    template = env.get_template('fanboy-social.j2')

    f = open("fanboy-social.txt", "w")
    f.write(template.render())
    f.close()


def main():
    python_version_check()
    build_lists()

if __name__ == '__main__':
    main()
