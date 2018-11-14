S['timer'] = 0

def timeSinus():
  import math

  S['timer'] += G['dt']
  result = math.sin(S['timer'])
  return result

call = timeSinus
