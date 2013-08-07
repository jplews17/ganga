from File import File
from File import ShareDir
from FileBuffer import FileBuffer

from IOutputFile import IOutputFile
from SandboxFile import SandboxFile
from MassStorageFile import MassStorageFile
from LCGSEFile import LCGSEFile

from Ganga.Utility.logging import getLogger
logger = getLogger()

# Make ancient systems without simplejson ignore GoogleFile
try:
    from GoogleFile import GoogleFile
except ImportError, e:
    if e.args[0].endswith('django.utils'):
        logger.warning('Lacking simplejson on system makes it impossible to use GoogleFile. Should only happen on some Python 2.4 systems')
    else:
        raise

from Ganga.GPIDev.Base.Filters import allComponentFilters
from Ganga.Utility.Config import getConfig, ConfigError


import fnmatch 

outputfilesConfig = {}

keys = getConfig('Output').options.keys()
keys.remove('PostProcessLocationsFileName')
keys.remove('ForbidLegacyInput')                     
keys.remove('ForbidLegacyOutput')                     
keys.remove('AutoRemoveFilesWithJob')
keys.remove('AutoRemoveFileTypes')

for key in keys:
    try:
        outputFilePatterns = []

        for configEntry in getConfig('Output')[key]['fileExtensions']:
            outputFilePatterns.append(configEntry)
                
        outputfilesConfig[key] = outputFilePatterns

    except ConfigError:
        pass    

def findOutputFileTypeByFileName(filename):      

    matchKeys = []

    for key in outputfilesConfig.keys():
        for filePattern in outputfilesConfig[key]:
            if fnmatch.fnmatch(filename, filePattern):
                matchKeys.append(key)

    if len(matchKeys) == 1:     
        return matchKeys[-1]
    elif len(matchKeys) > 1:
        logger.warning("file name pattern %s matched %s, assigning to %s" % (filename, str(matchKeys), matchKeys[-1]))
        return matchKeys[-1]
    else:
        return None     

def string_file_shortcut(v,item):
    if type(v) is type(''):
        # use proxy class to enable all user conversions on the value itself
        # but return the implementation object (not proxy)
        key = findOutputFileTypeByFileName(v)
        if key is not None:
            if key == 'MassStorageFile':
                from MassStorageFile import MassStorageFile
                return MassStorageFile._proxyClass(v)._impl         
            elif key == 'LCGSEFile':
                from LCGSEFile import LCGSEFile
                return LCGSEFile._proxyClass(v)._impl                                
            elif key == 'DiracFile':
                try:
                    from GangaDirac.Lib.Files.DiracFile import DiracFile
                    return  DiracFile._proxyClass(v)._impl                                
                except:
                    pass

        return SandboxFile._proxyClass(v)._impl

    return None 
        
allComponentFilters['outputfiles'] = string_file_shortcut