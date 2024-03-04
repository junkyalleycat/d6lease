#!/usr/bin/env python3

from pathlib import Path
from textx import metamodel_from_file
from ipaddress import *
import datetime
from collections import namedtuple

default_leases_path = Path('/var/db/dhcpd6/dhcpd6.leases')
model_path = Path(__file__).parent.joinpath('d6leases.tx')

class DATE(namedtuple('DATE', ['date', 'weekday'])):

    @staticmethod
    def from_parsed(parsed):
        yr, mo, dy = map(int, parsed.date.split('/'))
        hr, mi, se = map(int, parsed.time.split(':'))
        return DATE(datetime.datetime(yr, mo, dy, hr, mi, se), parsed.weekday)

def put_(m, key, value):
    if key in m: raise Exception(key)
    m[key] = value

class IA_NA(namedtuple('IA_NA', ['iaid_duid', 'cltt', 'iaaddr'])):

    @staticmethod
    def from_parsed(parsed):
        kwargs = {}
        kwargs['iaid_duid'] = parsed.iaid_duid.value
        for statement in parsed.block.statements:
            if statement.name == 'cltt':
                put_(kwargs, 'cltt', DATE.from_parsed(statement.value))
            else:
                raise Exception(statement.name)
        if len(parsed.block.iaaddrs) == 0:
            iaaddr = None
        elif len(parsed.block.iaaddrs) == 1:
            iaaddr = IAADDR.from_parsed(parsed.block.iaaddrs[0])
        else:
            raise Exception()
        kwargs['iaaddr'] = iaaddr
        return IA_NA(**kwargs)

class IAADDR(namedtuple('IAADDR', ['addr', 'binding_state', 'preferred_life', 'max_life', 'ends', 'variables'])):

    @staticmethod
    def from_parsed(parsed):
        kwargs = {}
        kwargs['addr'] = ip_address(parsed.addr)
        variables = {}
        for statement in parsed.block.statements:
            key = statement.name
            if key == 'binding state':
                put_(kwargs, 'binding_state', statement.value)
            elif key == 'preferred-life':
                put_(kwargs, 'preferred_life', int(statement.value))
            elif key == 'max-life':
                put_(kwargs, 'max_life', int(statement.value))
            elif key == 'ends':
                put_(kwargs, 'ends', DATE.from_parsed(statement.value))
            elif key == 'set':
                put_(variables, statement.variable, statement.value)
            else:
                raise Exception(statement.name)
        kwargs['variables'] = variables
        return IAADDR(**kwargs)

class GLOBAL(namedtuple('GLOBAL', ['authoring_byte_order', 'server_duid', 'ia_nas'])):

    @staticmethod
    def from_parsed(parsed):
        kwargs = {}
        for statement in parsed.statements:
            key = statement.name
            if key == 'authoring-byte-order':
                put_(kwargs, 'authoring_byte_order', statement.value)
            elif key == 'server-duid':
                put_(kwargs, 'server_duid', statement.value)
            else:
                raise Exception(key)
        kwargs['ia_nas'] = [IA_NA.from_parsed(x) for x in parsed.ia_nas]
        return GLOBAL(**kwargs)

def load_leases(leases_path=default_leases_path):
    d6leases_meta = metamodel_from_file(model_path)
    d6leases = d6leases_meta.model_from_str(leases_path.read_text())
    return GLOBAL.from_parsed(d6leases)

