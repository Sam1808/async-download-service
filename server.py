import aiofiles
import asyncio
import pathlib
import logging
from aiohttp import web


async def archivate(request):
    folder = request.match_info.get('archive_hash')
    files_dir = pathlib.Path(__file__).parent.joinpath("test_photos").joinpath(folder).absolute()
    exceptions = '.' or '..' or None
    if not files_dir.is_dir() or folder == exceptions:
        raise web.HTTPNotFound(
            text=f"Error 404. Cannot create archive from '{folder}'.  Maybe folder does not exist or has been deleted."
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
            await response.write(await process.stdout.read(102400))
            await asyncio.sleep(1)

    except (asyncio.CancelledError, ConnectionResetError, KeyboardInterrupt, SystemExit):
        logging.debug('Download was interrupted')
        await process.communicate()
        if process.returncode is None or process.returncode:
            try:
                process.kill()
            except ProcessLookupError:
                logging.debug(f'Cannot find process {process.pid}. Maybe it has been deleted.')
        logging.debug(f'Process {process.pid} has been deleted.')
        raise

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
