"""Lossless typed DAG encoding shared by the one v4 numerical ROOT writer."""

import math


def encode(value):
    return str(value).encode('utf-8').hex() or '-'


def decode(value):
    return bytes.fromhex(value).decode('utf-8') if value != '-' else ''


def nodes(value, stream):
    intern = {}

    def visit(item):
        if item is None:
            kind, text, children, keys = 'N', '', (), ()
        elif type(item) is bool:
            kind, text, children, keys = 'B', str(int(item)), (), ()
        elif type(item) is int:
            kind, text, children, keys = 'I', str(item), (), ()
        elif type(item) is float:
            if not math.isfinite(item):
                raise ValueError('nonfinite archive scalar')
            kind, text, children, keys = 'F', item.hex(), (), ()
        elif type(item) is str:
            kind, text, children, keys = 'S', item, (), ()
        elif type(item) is list:
            kind, text, children, keys = 'A', '', tuple(visit(x) for x in item), ()
        elif type(item) is dict:
            keys = tuple(sorted(item))
            kind, text, children = 'O', '', tuple(visit(item[key]) for key in keys)
        else:
            raise ValueError('unsupported archive value')
        key = (kind, text, children, keys)
        if key in intern:
            return intern[key]
        identity = len(intern)
        intern[key] = identity
        stream.write('\t'.join(['N', str(identity), kind, encode(text),
            ','.join(map(str, children)) or '-',
            ','.join(map(encode, keys)) or '-']) + '\n')
        return identity

    return visit(value)
