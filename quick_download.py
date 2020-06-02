is_running = True


async def quick_download(link: str, conn: int = 32, skip_tls: bool = False) -> bytes:
    # TODO: Change it to something real
    return open("/home/aria/PycharmProjects/QuickPy/a.rar", "rb").read()


async def quick_download_range(link: str, start: int, finish: int) -> bytes:
    pass
