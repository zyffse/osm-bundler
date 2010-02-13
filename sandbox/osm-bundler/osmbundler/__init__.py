import sys, os
import PIL

# TODO: replace this later with dynamical load
from matching.bundler import BundlerMatching
from matching.manual import ManualMatching

# TODO: replace this later with dynamical load
from features.siftlowe import LoweSift
from features.siftvlfeat import VlfeatSift


class OsmBundler():
    # it might be need to convert results of feature extraction
    bundlerVersion = "NoahSnavely-0.3"

    # path to bin directory of the bundler distribution
    binDir = ""

    # path to bundler executable
    bundler = "bundler"

    workDir = ""
    
    featureExtractor = None
    
    matchingEngine = None

    def __init__(self):
        dirname = os.path.dirname(sys.argv[0])
        self.binDir = os.path.join(dirname, "bin")
        self.bundler = getExecPath(self.binDir, self.bundler)
        
        # parse command line arguments

        # create a temporary directory for the project with unique name, set self.workDir
        
        # initialize feature extractor based on command line arguments
        
        # initialize mathing engine based on command line arguments
        

    def preparePhotos(self):
        # open each photo, resize, convert to pgm, copy it to self.workDir and calculate focal distance
        # conversion to pgm is performed by PIL library
        # EXIF reading is performed by PIL library
        pass
        
    def extractFeatures(self):
        # let self.featureExtractor do its job
        # in the case of manual matching do nothing
        pass
    
    def matchFeatures(self):
        # let self.matchingEngine do its job
        # self.matchingEngine for the manual matching is supposed to create all files which Bundler needs
        pass
    
    def doBundleAdjustment(self):
        # just run Bundler here
        pass


# service function: get path of an executable (.exe suffix is added if we are on Windows)
def getExecPath(dir, fileName):
    if sys.platform == "win32": fileName = "%s.exe" % fileName
    return os.path.join(dir, fileName)