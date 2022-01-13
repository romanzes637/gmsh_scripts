import asyncio
import sys
import platform

# asyncio + subprocess https://docs.python.org/3.8/library/asyncio-subprocess.html#subprocesses


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def main(n_workers=2):
    await asyncio.gather(
        *(run(f'{sys.executable} test_optimize.py') for _ in range(n_workers)))


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main(n_workers=2))
