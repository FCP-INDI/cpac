#!/usr/bin/env python
r"""cpac_parse_resources.py.

When provided with a `callback.log` file, this utility can sort through
the memory `runtime` usage, `estimate`, and associated `efficiency`, to
identify the `n` tasks with the `highest` or `lowest` of each of these
categories.
`cpac_parse_resources` is intended to be run outside a C-PAC container.
"""
from argparse import ArgumentParser
import configparser
import json
import os
import uuid

import pandas as pd
from rich.console import Console
from rich.table import Table

runti = "runtime_memory_gb"
estim = "estimated_memory_gb"

field = {"runtime": runti, "estimate": estim, "efficiency": "efficiency"}


def display(df):
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Task ID", style="dim", width=40)
    table.add_column("Memory Used")
    table.add_column("Memory Estimated")
    table.add_column("Memory Efficiency")

    for _, d in df.iterrows():
        tmp = []
        tmp += [d["id"]]
        tmp += [d[runti]]
        tmp += [d[estim]]
        tmp += ["{0:.2f} %".format(100 * d[runti] * 1.0 / d[estim])]

        tmp = ["{0:.4f}".format(t) if isinstance(t, float) else str(t) for t in tmp]
        table.add_row(*tmp)
        del tmp

    console.print(table)


def get_or_create_config(udir):
    """Create a Google Analytics tracking config file.

    Sourced from https://github.com/FCP-INDI/C-PAC/blob/80424468c7f4e59c102f446b05d4154ec1cd4b2d/CPAC/utils/ga.py#L19-L30
    """  # pylint: disable=line-too-long
    tracking_path = os.path.join(udir, ".cpac")
    cparser = configparser.ConfigParser()
    if os.path.exists(tracking_path):
        cparser.read(tracking_path)
    if not cparser.has_section("user"):
        cparser.read_dict({"user": {"uid": uuid.uuid1().hex, "track": True}})
        with open(tracking_path, "w+") as fhandle:
            cparser.write(fhandle)
    return tracking_path


def load_runtime_stats(callback):
    with open(callback) as fhandle:
        logs = [json.loads(log) for log in fhandle.readlines()]

    pruned_logs = []
    for log in logs:
        if runti not in log.keys():
            continue

        tmp = {}
        for k in ["id", runti, estim]:
            tmp[k] = log[k]
        tmp["efficiency"] = tmp[runti] / tmp[estim] * 100

        pruned_logs += [tmp]
        del tmp

    return pd.DataFrame.from_dict(pruned_logs)


def main(args):
    """Parse and display resource usage.

    Parameters
    ----------
    args : argparse.Namespace

    Returns
    -------
    None
    """
    usage = load_runtime_stats(args.callback)
    filtered_usage = query(
        usage, args.filter_field, args.filter_group, args.filter_count
    )
    display(filtered_usage)


def query(usage, f, g, c):
    order = g == "lowest"
    usage.sort_values(by=field[f], ascending=order, inplace=True)
    usage.reset_index(inplace=True, drop=True)
    return usage[0:c]


def set_args(parser):
    """Set up the command line arguments for the script.

    Parameters
    ----------
    parser : argparse.ArgumentParser

    Returns
    -------
    parser : argparse.ArgumentParser
    """
    parser.add_argument(
        "callback",
        help="callback.log file found in the 'log' "
        "directory of the specified derivatives path",
    )
    parser.add_argument(
        "--filter_field",
        "-f",
        action="store",
        choices=["runtime", "estimate", "efficiency"],
        default="efficiency",
    )
    parser.add_argument(
        "--filter_group",
        "-g",
        action="store",
        choices=["lowest", "highest"],
        default="lowest",
    )
    parser.add_argument("--filter_count", "-n", action="store", type=int, default=10)
    return parser


if __name__ == "__main__":
    main(set_args(ArgumentParser(__file__, add_help=True)).parse_args())
