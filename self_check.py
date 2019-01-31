#!/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

'''МИСМП (Ecobot) — Модуль самодиагностики'''

def load_scheme(filename='./objects.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_state(element=''):
    # return element.get_state() — TODO: add actual call when elements are ready
    return random.randint(45, 50)  # FOR TESTING ONLY TODO REMOVE THIS

def check(scheme: dict):
    check_result = {}
    for key in scheme.keys():
        current_state = get_state(key)
        print(current_state)
        if scheme[key]['min'] <= current_state <= scheme[key]['max']:
            check_result[key] = True
        else:
            check_result[key] = False
    return check_result

if __name__ == "__main__":
    scheme = load_scheme()
    print(check(scheme))

