import logging

from random import shuffle

log = logging.getLogger(__name__)

class Playlist():
  def __init__(self, guild_id) -> None:
    self.guild_id = guild_id
    self.entries = []
    self.index = 0
    self.next_track = 0
    self.is_loop = False

  def __iter__(self):
    return iter(self.entries)

  def __getitem__(self, item):
    return self.entries[item]

  def __len__(self):
    return len(self.entries)

  @property
  def selected(self):
    if self.index is None or self.is_empty():
      return None
    return self.entries[self.index]

  @property
  def before(self):
    if self.index == 0:
      return []
    return iter(self.entries[self.index-1:])

  @property
  def after(self):
    return iter(self.entries[:self.index])

  @property
  def to_be_played(self):
    if self.is_loop:
      return iter([self.selected] + [*self.after] + [*self.before])
    else:
      return iter([self.selected] + [*self.after])

  def is_empty(self):
    return False if self.entries else True

  def add(self, entry, index=None):
    if index:
      self.entries.insert(index, entry)
    else:
      self.entries.append(entry)

  def shuffle(self):
    entry = self.entries.pop(self.index)
    shuffle(self.entries)
    self.entries = [entry] + self.entries

  def loop(self, value=None):
    if value == None:
      self.is_loop = not self.is_loop
    else:
      self.is_loop = value

  def clear(self):
    self.entries = []

  def select(self, index):
    try:
      entry = self.entries[index]
      self.index = index
      self.next_track = self.index
      return entry
    except:
      return None

  def next(self):
    if self.next_track >= len(self.entries):
      if self.is_loop:
        self.next_track = 0
      else:
        return None

    self.index = self.next_track
    self.next_track += 1

    return self.entries[self.index]

  def remove_by_index(self, index):
    return self.entries.pop(index)

  def remove_by_id(self, id):
    for i, e in enumerate(self.entries):
      if e.id == id:
        return self.entries.pop(i)
    return None

  def move(self, origin, destination):
    _entry = self.entries[origin]
    self.pop(origin)
    self.entries.insert(destination, _entry)

  @property
  def size(self):
    return len(self.entries)

  @property
  def duration(self):
    _total_duration = 0
    for entry in self:
      if entry.duration:
        _total_duration += entry.duration
