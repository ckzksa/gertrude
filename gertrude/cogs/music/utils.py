
class Singleton(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

def format_duration(duration):
  if not duration or duration <= 0:
    return 'LIVE'
    
  formated_duration = ''
  seconds = duration % 60
  minutes = duration // 60 % 60
  hours = duration // 60 // 60

  formated_duration = f'{str(minutes).rjust(2, "0")}:{str(seconds).rjust(2, "0")}'
  if hours > 0:
    return f'{str(hours).rjust(2, "0")}:' + formated_duration
  return formated_duration
