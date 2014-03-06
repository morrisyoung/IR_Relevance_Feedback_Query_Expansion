import os
import fnmatch
import stat


class Clear:

    def __init__(self):
        self.l_rv = ['*.pyc', '*.swp']  # add the deleting file type here
        self.l_f = []

    def gettarget(self, dir):
        for fileName in os.listdir(dir):
            for t in self.l_rv:
                if fnmatch.fnmatch(fileName, t):
                    new = dir+'/'+fileName
                    self.l_f.append(new)
        return

    def clear(self, dir):  # either get the remove list, or check whether there is a sub-folder existing.
        self.gettarget(dir)
        for fileName in os.listdir(dir):
            fileStats = os.stat(dir+'/'+fileName)
            fileMode = fileStats[stat.ST_MODE]
            if stat.S_ISDIR(fileMode):
                newdir = dir+'/'+fileName
                self.clear(newdir)
        return self.l_f