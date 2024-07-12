#!/usr/bin/env python3
from pprint import pprint

import fire

from client import ApiClient

api_test = ApiClient("test")


def p():
    pprint(api_test.participate())


def r():
    pprint(api_test.rounds())


def u():
    pprint(api_test.units())


def w():
    pprint(api_test.world())


if __name__ == "__main__":
    fire.Fire()
