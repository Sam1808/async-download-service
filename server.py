import aiofiles
import argparse
import asyncio
import logging
import pathlib

from aiohttp import web
from environs import Env
from functools import partial


async def archivate(request, photo_dir: str, delay: int,  file_fragment: int):

    folder = request.match_info['archive_hash']
    files_dir = pathlib.Path(__file__).parent.joinpath(photo_dir).joinpath(folder).absolute()
    exceptions = ['.', '..', None]
    if not files_dir.is_dir() or folder in exceptions:
        raise web.HTTPNotFound(
            text=f"""
            Error 404. Cannot create archive from '{folder}' in '{photo_dir}' folder.
            Maybe this folder does not exist or has been deleted."""
        )

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = f"attachment;  filename = {folder}.zip"
    await response.prepare(request)

    zip_command = ('zip', '-r', '-', '.')
    process = await asyncio.create_subprocess_exec(
        *zip_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=files_dir
    )

    try:
        while not process.stdout.at_eof():
            logging.debug('Sending archive chunk ...')
            await response.write(await process.stdout.read(file_fragment))
            await asyncio.sleep(delay)

    except (asyncio.CancelledError, ConnectionResetError, KeyboardInterrupt, SystemExit):
        logging.debug('Download was interrupted')
        await process.communicate()
        logging.debug(f'Process {process.pid} has been deleted.')
        raise

    finally:
        if process.returncode is None or process.returncode:
            try:
                process.kill()
            except ProcessLookupError:
                logging.debug(f'Cannot find process {process.pid}. Maybe it has been deleted.')

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser(description='Start server with parameters.')
    parser.add_argument('--debug', action='store_true', help='Logging level (default DEBUG)')
    parser.add_argument('--delay', type=int, help='Download delay (sec)')
    parser.add_argument('--photo_dir', type=str, help='Photo folder name')
    parser.add_argument('--fragment', type=int, help='File fragment (Kbytes)')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=env.log_level('LOG_LEVEL'))

    photo_dir = args.photo_dir or env('PHOTO_DIR')
    delay = args.delay or env.int('DELAY')
    file_fragment = args.fragment or env.int('KBYTES')
    file_fragment *= 1024

    partial_archiving = partial(archivate, photo_dir=photo_dir, delay=delay, file_fragment=file_fragment)

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', partial_archiving),
    ])
    web.run_app(app)
