from functools import partial
from asyncio import get_running_loop

async def run_blocking(func, *args, **kwargs):
    loop = get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))
