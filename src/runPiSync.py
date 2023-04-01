from piSync import piSync

try:
  mySync = piSync()
  mySync.doSync()
except:
  exit()