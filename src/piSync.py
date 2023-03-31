#!/usr/bin/env python
# encoding: utf-8

# piSync will syncronize files between two directries,
# 1) sourceDir to 2) backupDir specifed in a file config.txt.

# piSyncClass is the entry point

import os
import hashlib
import time
LOG = 'log.txt'
# function area
# -------------------------------------------------------------

# log function
def log(message):
    # write log
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG, 'a') as f:
        f.write('['+now+']'+message+'\n')

def fixBadChars(inStr):

    outStr = inStr
    if ' ' in outStr:
      outStr = outStr.replace(' ', '\ ')
    if '\'' in outStr:
      outStr = outStr.replace("'", "\\'")
    if '(' in outStr:
      outStr = outStr.replace("(", "\(")
      #print('piChk1: '+outStr)
    if ')' in outStr:
      outStr = outStr.replace(")", "\)")
      #print('piChk2: '+outStr)
    if '&' in outStr:
      outStr = outStr.replace("&", "\&")
      #print('piChk3: '+outStr)

    return outStr

def compare2file(file1, file2):
    # compare 2 files with hash
    # print('file1: '+file1)
    # print('file2: '+file2)
    if file1 == '.DS_Store': return True
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            f1Hash = hashlib.md5(f1.read()).hexdigest()
            f2Hash = hashlib.md5(f2.read()).hexdigest()
            if f1Hash == f2Hash:
                return True
            else:
                log(file1+': '+str(f1Hash))
                log(file2+': '+str(f2Hash))
                return False

def compareHashSourceDir(sourceDir, backupDir):
    # compare hash sourceDir
    # return True if all file is same
    # return False if any file is different
     # get all file in sourceDir
    files = os.listdir(sourceDir)
    # get all file in backupDir
    files_backupDir = os.listdir(backupDir)
    # compare 2 list
    if len(files) != len(files_backupDir):
        return False

    for file in files:
        if file in files_backupDir and not os.path.isdir(os.path.join(backupDir, file)):
            if not compare2file(os.path.join(sourceDir, file), os.path.join(backupDir, file)):
                return False
        else:
            return False
    return True

def chkSourceDir(sourceDir, backupDir):
    # check file hash in sourceDir and compare with backupDir
    countSync = 0
    updateFile = 0
    deleteFile = 0

  # check if sourceDir is same with backupDir
    if compareHashSourceDir(sourceDir, backupDir):
        now = time.strftime("%Y-%m-%d %H:%M:%S.%f", time.localtime())
        print(f'[{now}] source is up to date')
        log('backup is up to date')
        return countSync, updateFile, deleteFile
    else:
        sourceDirsOK = True
        # check sourceDir
        if os.path.isdir(sourceDir):
            print(f'sync source: {sourceDir}')
            log(f'sync source: {sourceDir}')
        else:
            print('source directory directory does not exist')
            log('source directory directory does not exist')
            print('please check your config file')
            sourceDirsOK = False

        # check backupDir
        if sourceDirsOK == True:
          if os.path.isdir(backupDir):
            print(f'sync backup: {backupDir}')
            log(f'sync backup: {backupDir}')
          else:
              print('backup directory does not exist')
              log('backup directory does not exist')
              print('please check your config file')
              sourceDirsOK = False

        if sourceDirsOK == True:
            # get all file in sourceDir
            files = os.listdir(sourceDir)
            # get all file in backupDir
            files_backupDir = os.listdir(backupDir)
            # compare 2 list
            for file in files_backupDir:
                if not file == '.DS_Store':
                    #print(os.path.join(backupDir, file)+' : '+str(os.path.isdir(os.path.join(backupDir, file))))
                    if file in files and not os.path.isdir(os.path.join(backupDir, file)):
                        if compare2file(sourceDir+'/'+file, backupDir+'/'+file):
                            log(f'{file} is up to date')
                            countSync += 1
                        else:
                            # copy file from sourceDir to backupDir
                            updateFile += 1
                            os.remove(os.path.join(backupDir, file))
                            theCommand = 'cp ' + fixBadChars(sourceDir)+'/'+fixBadChars(file)+' '+fixBadChars(backupDir)
                            rtnCode = os.system(theCommand)
                            #print(str(rtnCode)+'-1: '+theCommand)
                            if rtnCode == 0:
                                log(f'different - {file} is copied')
                                print(f'different - {file} is copied')
                            else:
                                log(f'*** error {rtnCode}: {file} not copied')
                                print(f'*** error {rtnCode}: {file} not copied')
                    if file not in files and not os.path.isdir(os.path.join(backupDir, file)):
                        # delete file in backupDir
                        log(f'{file} is deleted')
                        deleteFile += 1
                        os.remove(os.path.join(backupDir, file))

            for file in files:
                if not file == '.DS_Store':
                    if file not in files_backupDir and not os.path.isdir(os.path.join(backupDir, file)):
                        # copy file from sourceDir to backupDir
                        updateFile += 1
                        theCommand = 'cp ' + fixBadChars(sourceDir)+'/'+fixBadChars(file)+' '+fixBadChars(backupDir)
                        rtnCode = os.system(theCommand)
                        #print(str(rtnCode)+'-2: '+theCommand)
                        if rtnCode == 0:
                            log(f'missing - {file} is copied')
                            print(f'missing - {file} is copied')
                        else:
                            log(f'*** error {rtnCode}: {file} not copied')
                            log(f'CMD: {theCommand}')
                            print(f'*** error {rtnCode}: {file} not copied')

    return countSync, updateFile, deleteFile

def chkBackupSubDirs(backupDir, theDirs):
    for aDir in theDirs:
        chkBackup = os.path.join(backupDir, aDir)
        if not os.path.isdir(chkBackup):
            os.mkdir(chkBackup, 0o755)

def writeConfig(sourceDir,backupDir):

    sourceDir = os.path.abspath(sourceDir)
    backupDir = os.path.abspath(backupDir)

    with open('config.txt', 'w') as f:
        f.write('sourceDir:'+sourceDir)
        f.write('\n')
        f.write('backupDir:'+backupDir)

# ----- class

class piSync():
  def __init__(self, sourceDir='', backupDir=''):
    try:
        log('Start')
        self.sourceDir = sourceDir
        self.backupDir = backupDir
        self.checkConfigFile()
    except:
      raise(FileExistsError)

  def checkConfigFile(self):
    if os.path.isfile('config.txt'):
        # get variable from config
        with open('config.txt', 'r') as f:
            lines = f.readlines()
            sourceDir = lines[0].split(':')[1].strip()
            backupDir = lines[1].split(':')[1].strip()
        # check if sourceDir is exist
        if not os.path.isdir(sourceDir):
            log('source directory: NOT FOUND')
            print('source directory is not exist')
            raise(FileExistsError)
        else:
            sourceDir = os.path.abspath(sourceDir)
        # check if backupDir is exist
        if not os.path.isdir(backupDir):
            newbackupDirParent = os.path.dirname(backupDir)
            foundGoodBaseDir = False
            while foundGoodBaseDir:
                if not os.path.isdir(newbackupDirParent):
                    newbackupDirParent = os.path.dirname(newbackupDirParent)
                else:
                    foundGoodBaseDir = True
                if newbackupDirParent == '':
                    log('backup directory: NOT FOUND')
                    print('backup directory parent does not exist')
                    raise(FileExistsError)
                #print(newbackupDirParent)

            newbackupDir = os.path.join(newbackupDirParent, os.path.basename(backupDir))
            createbackupDir = input(f'Create: {newbackupDir}? (y/n): ')
            if createbackupDir in ['y', 'Y']:
                os.makedirs(newbackupDir, 0o755)
                # write config
                writeConfig(sourceDir,newbackupDir)
            else:
                raise(FileExistsError)
        else:
            backupDir = os.path.abspath(backupDir)
            writeConfig(sourceDir,backupDir)

        print("config file: OK")
        log ('config file: OK')

    else:
        log('config file: NOT FOUND')
        print("config file: NOT FOUND")
        # register sourceDir
        sourceDir = input('enter source directory path: ')
        # '/Volumes/piDrive/music/Music/The Beatles/Acoustic Submarine'
        print(sourceDir)
        backupDir = input('enter backup directory path: ')
        # '/Volumes/piSpace/Music/Media/Music/The Beatles/Acoustic Submarine'
        print(backupDir)
        # check if sourceDir is exist
        if not os.path.isdir(sourceDir):
            log('source directory: NOT FOUND')
            print('source directory does not exist')
            raise(FileExistsError)
        # check if backupDir is exist
        if not os.path.isdir(backupDir):
            log('backup directory: NOT FOUND')
            print('backup directory does not exist')
            raise(FileExistsError)
        # write config
        writeConfig(sourceDir,backupDir)

        print('config file: CREATED')
        log('config file: CREATED')

    self.sourceDir = sourceDir
    self.backupDir = backupDir

  def doSync(self):
    # run loop every 5 minutes
    countSyncTotal = 0
    updateFileTotal = 0
    deleteFileTotal = 0
    keepLooping = True
    print(self.sourceDir)
    while keepLooping:
        for subdir, dirs, files in os.walk(self.sourceDir):
            if subdir == self.sourceDir:
                countSync, updateFile, deleteFile = chkSourceDir(subdir, self.backupDir)
                chkBackupSubDirs(self.backupDir, dirs)
            else:
                chkBackup = subdir.replace(self.sourceDir,self.backupDir)
                countSync, updateFile, deleteFile = chkSourceDir(subdir, chkBackup)
                chkBackupSubDirs(chkBackup, dirs)

            now = time.strftime("%Y-%m-%d %H:%M:%S.%f", time.localtime())
            print(f'[{now}] sync: {countSync}; update: {updateFile}; delete: {deleteFile}')

            countSyncTotal += countSync
            updateFileTotal += updateFile
            deleteFileTotal += deleteFile

        now = time.strftime("%Y-%m-%d %H:%M:%S.%f", time.localtime())
        print(f'[{now}] totals - sync: {countSyncTotal}; update: {updateFileTotal}; delete: {deleteFileTotal}')

        keepLooping = False
        # sleep for 5 minutes
        #time.sleep(300)
