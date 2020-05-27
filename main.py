import asyncio
import logging

import os
import pathlib
import sys
import signal

import argparse

from quick_download import quick_download

DISPLAY_PROGRESS: bool = True
DISPLAY_STARTUP: bool = True


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


async def main(args=None):
    if DISPLAY_STARTUP:
        await display_startup()
    if args is None:
        args = await parse_args()
    if args.command == 'tasks':
        # TODO: Tasks
        pass
    elif args.command == 'resume':
        # TODO: Resume
        pass
    elif args.command == 'download':
        content = await quick_download(args.link, args.connections, args.skip_tls)
        # TODO: Write content to output file at args.output
        print(content)
        pass


def start():
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda sig: asyncio.create_task(shutdown(sig, loop)))
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
        logging.info("Successfully shutdown the Mayhem service.")


async def shutdown(sig: signal.Signals, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logging.info(f"Received exit signal {sig.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks)
    logging.info(f"Flushing metrics")
    loop.stop()


if __name__ == '__main__':
    start()
