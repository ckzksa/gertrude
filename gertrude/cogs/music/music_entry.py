import random
import logging

log = logging.getLogger(__name__)

class MusicEntry():
  def __init__(self, author, data=None) -> None:
    self.id = random.randint(100000, 999999)
    self.author = author
    self.data = data

  def __repr__(self) -> str:
    return f'{self.id} - {self.title} resqueted by {self.author}'

  @property
  def url(self):
    return self.data['url']

  @property
  def title(self):
    return self.data['title']

  @property
  def duration(self):
    if not 'duration' in self.data:
      return None
    return self.data['duration']

  @property
  def webpage_url(self):
    return self.data['webpage_url']

  @property
  def uploader(self):
    return self.data['uploader']

  @property
  def thumbnails_url(self):
    return self.data['thumbnails'][0]['url']

  