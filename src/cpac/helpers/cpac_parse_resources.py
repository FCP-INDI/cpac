#!/usr/bin/env python
'''cpac_parse_resources.py

`cpac_parse resources` is intended to be run outside a C-PAC container
'''

from rich.console import Console
from rich.table import Table

from argparse import ArgumentParser
import pandas as pd
import numpy as np
import json


runti = 'runtime_memory_gb'
estim = 'estimated_memory_gb'

field = {'runtime': runti,
         'estimate': estim,
         'efficiency': 'efficiency'}


def display(df):
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Task ID", style="dim", width=40)
    table.add_column("Memory Used")
    table.add_column("Memory Estimated")
    table.add_column("Memory Efficiency")

    for _, d in df.iterrows():
        tmp = list()
        tmp += [d['id']]
        tmp += [d[runti]]
        tmp += [d[estim]]
        tmp += ["{0:.2f} %".format(100*d[runti] * 1.0 / d[estim])]

        tmp = ["{0:.4f}".format(t) if isinstance(t, float) else str(t)
               for t in tmp]
        table.add_row(*tmp)
        del tmp

    console.print(table)


def load_runtime_stats(callback):
    with open(callback) as fhandle:
        logs = [json.loads(log) for log in fhandle.readlines()]

    pruned_logs = []
    for log in logs:
        if runti not in log.keys():
            continue

        tmp = {}
        for k in ['id', runti, estim]:
            tmp[k] = log[k]
        tmp['efficiency'] = tmp[runti] / tmp[estim] * 100

        pruned_logs += [tmp]
        del tmp

    return pd.DataFrame.from_dict(pruned_logs)


def query(usage, f, g, c):
    order = True if g == 'lowest' else False
    usage.sort_values(by=field[f], ascending=order, inplace=True)
    usage.reset_index(inplace=True, drop=True)
    return usage[0:c]


if __name__ == '__main__':
    parser = ArgumentParser(__file__)
    parser.add_argument("callback",
                        help="callback.log file found in the 'log' "
                             "directory of the specified derivatives path")
    parser.add_argument("--filter_field", "-f", action="store",
                        choices=['runtime', 'estimate', 'efficiency'],
                        default='efficiency')
    parser.add_argument("--filter_group", "-g", action="store",
                        choices=['lowest', 'highest'], default='lowest')
    parser.add_argument("--filter_count", "-n", action="store", type=int,
                        default=10)

    res = parser.parse_args()
    usage = load_runtime_stats(res.callback)

    filtered_usage = query(usage, res.filter_field, res.filter_group,
                           res.filter_count)
    display(filtered_usage)
