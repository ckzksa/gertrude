import asyncio
import logging
from functools import partial
import re
from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)
YDL_OPTIONS = {
  'format': 'bestaudio/best',
  'quiet': True,
  'postprocessors' : [{
      'key' : 'FFmpegExtractAudio',
      'preferredcodec' : 'mp3',
      'preferredquality' : '192',
  }],
  'noplaylist' : True,
  'logtostderr': False,
  'no_warnings': True,
  'nocheckcertificate': True,
  'ignoreerrors': False,
  'default_search': 'auto',
  'source_address': '0.0.0.0',
  'skip_download': True,
  # 'logger': log,
}

YDL_OPTIONS_PLAYLIST = dict(YDL_OPTIONS)
YDL_OPTIONS_PLAYLIST.update({
  'extract_flat': True,
})

YOUTUBE_URL_VALIDATOR =  re.compile(r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$', re.IGNORECASE)
URL_VALIDATOR = re.compile(
  r'^(?:http|ftp)s?://' # http:// or https://
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
  r'localhost|' #localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
  r'(?::\d+)?' # optional port
  r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class Downloader():
  def __init__(self) -> None:
    self.thread_pool = ThreadPoolExecutor(max_workers=3)
    self.loop = asyncio.get_event_loop()

  async def extract_info(self, url, download=False):
    if re.match(YOUTUBE_URL_VALIDATOR, url) and 'list=' in url:
      # playlist
      with YoutubeDL(YDL_OPTIONS_PLAYLIST) as ytdl:
        to_run = partial(ytdl.extract_info, url=url, download=download)
        data = await self.loop.run_in_executor(None, to_run)
        entries = []

        async def to_run(data, entries):
          while data:
            entry = await self.extract_info(data.pop(0)['url'], download=download)
            entries.append(entry)

        await asyncio.gather(*[to_run(data['entries'], entries) for _ in range(12)])
        return entries, data
    else:
      # search or video
      with YoutubeDL(YDL_OPTIONS) as ytdl:
        to_run = partial(ytdl.extract_info, url=url, download=download)
        data = await self.loop.run_in_executor(None, to_run)

        if 'entries' in data:
          data = data['entries'][0]

        return data
