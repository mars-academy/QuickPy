import asyncio
import logging

import os
import pathlib
import sys
import signal
import argparse
import funcy
import aiofiles
import clint
import progress
from quick_download import quick_download

DISPLAY_PROGRESS: bool = True
DISPLAY_STARTUP: bool = True
import pyximport

pyximport.install(pyimport=True, language_level=3)

import file_size


async def display_startup():
    print("---------------------------------------------------------------------")
    print("|                                                                   |")
    print("|                        Welcome to QuickPy!                        |")
    print("|                 QuickPy is a Download Accelerator                 |")
    print("|                                                                   |")
    print("|                                                                   |")
    print("|          Github: https://github.com/mars-academy/QuickPy          |")
    print("|                                                                   |")
    print("---------------------------------------------------------------------")


async def parse_args():
    parser = argparse.ArgumentParser(description='Accelerated File Download.')
    parser.add_argument('Command',
                        metavar='command',
                        type=str,
                        help='Command')

    parser.add_argument('Link',
                        metavar='link',
                        type=str,
                        help='the link to your desired file.')
    parser.add_argument('Connections',
                        metavar='connections',
                        type=int,
                        default=32,
                        required=False,
                        help='maximum number of connections.')
    parser.add_argument('Skip_TLS',
                        metavar='skip-tls',
                        type=bool,
                        default=False,
                        required=False,
                        help='skip verify certificate for https')
    parser.add_argument('Output',
                        metavar='output',
                        type=str,
                        required=True,
                        help='output address')

    args = parser.parse_args()
    return args


async def main(**kwargs):
    if DISPLAY_STARTUP:
        await display_startup()
    if kwargs is None:
        args = await parse_args()
        kwargs = {
            "command": args.command,
            "link": args.link,
            "connections": args.connections,
            "skip_tls": args.skip_tls,
            "output": args.output
        }
    else:
        if "connections" not in kwargs.keys():
            kwargs["connections"] = 32
        if "skip_tls" not in kwargs.keys():
            kwargs["skip_tls"] = False
    if kwargs["command"] == 'tasks':
        # TODO: Tasks
        pass
    elif kwargs["command"] == 'resume':
        # TODO: Resume
        pass
    elif kwargs["command"] == 'download':
        content: bytes = await quick_download(kwargs["link"], kwargs["connections"], kwargs["skip_tls"])
        print(f"content_length: {len(content)}")
        content_length_in_unit, unit = file_size.get_largest_unit(len(content))
        print(f"content_length: {content_length_in_unit}")
        # TODO: Write content to output file at args.output
        async with aiofiles.open(kwargs["output"], "wb") as file:
            with progress.Bar("Writing downloaded files to output.", unit=unit,
                              expected_size=content_length_in_unit) as bar:
                for chunk in funcy.chunks(1024**file_size.SizeUnit.__get_unit__(unit), content):
                    await file.write(chunk)
                    bar.show(bar.last_progress + 1)


def start(**kwargs):
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    try:
        loop.run_until_complete(main(**kwargs))
    finally:
        loop.close()
        logging.info("Successfully shutdown the Mayhem service.")


if __name__ == '__main__':
    start(command="download", link="a", output="b.rar")
