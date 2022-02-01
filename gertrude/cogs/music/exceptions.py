
class MusicException(Exception):
  def __init__(self, message):
    super().__init__(message)
    self._message = message

  @property
  def message(self):
    return self._message


class NotConnectedException(MusicException):
  def __init__(self, message):
      super().__init__(message)