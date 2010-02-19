import logging
import sys, os, getopt, tempfile

from PIL import Image
from PIL.ExifTags import TAGS

import defaults

# TODO: replace this later with dynamical load
from matching.bundler import BundlerMatching
from matching.manual import ManualMatching

# TODO: replace this later with dynamical load
from features.siftlowe import LoweSift
from features.siftvlfeat import VlfeatSift

commandLineLongFlags = ["photos=", "maxPhotoSize="]
exifAttrs = dict(Model=True,Make=True,ExifImageWidth=True,ExifImageHeight=True,FocalLength=True)


class OsmBundler():
    # it might be need to convert results of feature extraction
    bundlerVersion = "NoahSnavely-0.3"

    # path to bin directory of the bundler distribution
    binDir = ""

    # path to bundler executable
    bundler = "bundler"

    workDir = ""
    
    # value of command line argument --photos=<..>
    photosArg = ""
    
    featureExtractor = None
    
    matchingEngine = None

    def __init__(self):
        # mixin defaults
        for attr in dir(defaults):
            if attr[0]!='_':
                setattr(self, attr, getattr(defaults, attr))
        
        self.parseCommandLineFlags()
        
        dirname = os.path.dirname(sys.argv[0])
        self.binDir = os.path.join(dirname, "bin")
        self.bundler = getExecPath(self.binDir, self.bundler)
        
        # create a working directory
        self.workDir = tempfile.mkdtemp()
        logging.info("Working directory created: "+self.workDir)
        
        if not (os.path.isdir(self.photosArg) or os.path.isfile(self.photosArg)):
            raise Exception, "'%s' is neither directory nor a file name" % self.photosArg
        # initialize feature extractor based on command line arguments
        
        # initialize mathing engine based on command line arguments

    def parseCommandLineFlags(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "", commandLineLongFlags)
        except getopt.GetoptError:
            self.printHelpExit()

        for opt,val in opts:
            if opt=="--photos":
                self.photosArg=val
            elif opt=="--maxPhotoSize":
                if val.isdigit() and int(val)>0: self.maxPhotoSize = int(val)
            elif opt=="--help":
                self.printHelpExit()
        
        if self.photosArg=="": self.printHelpExit()

    def preparePhotos(self):
        # open each photo, resize, convert to pgm, copy it to self.workDir and calculate focal distance
        # conversion to pgm is performed by PIL library
        # EXIF reading is performed by PIL library
        
        if os.path.isdir(self.photosArg):
            # directory with images
            photos=[f for f in os.listdir(self.photosArg) if os.path.isfile(os.path.join(self.photosArg, f)) and os.path.splitext(f)[1].lower()==".jpg"]
            if len(photos)<3: raise Exception, "The directory with images should contain at least 3 .jpg photos"
            for photo in photos:
                self._preparePhoto(self.photosArg, photo)
        elif os.path.isfile(self.photosArg):
            # a file with a list of images
            photosFile = open(self.photosArg)
            for photo in photosFile:
                photo = photo.rstrip()
                if os.path.isfile(photo):
                    dirname,basename = os.path.split(photo)
                    self._preparePhoto(dirname,basename)
            photosFile.close()

    def _preparePhoto(self, photoDir, photo):
        inputFileName = os.path.join(photoDir, photo)
        outputFileName = os.path.join(self.workDir, photo) +  ".pgm"
        # open photo
        photoHandle = Image.open(inputFileName)
        # get EXIF information as dictionary
        exif = self._getExif(photoHandle)
        print exif
        photoHandle.convert("L").save(outputFileName)
        
    def _getExif(self, photoHandle):
        exif = {}
        info = photoHandle._getexif()
        if info:
            for attr, value in info.items():
                decodedAttr = TAGS.get(attr, attr)
                if decodedAttr in exifAttrs: exif[decodedAttr] = value
        if 'FocalLength' in exif: exif['FocalLength'] = float(exif['FocalLength'][0])/float(exif['FocalLength'][1])
        return exif

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
    
    def printHelpExit(self):
        self.printHelp()
        sys.exit(2)
    
    def printHelp(self):
        print "--photos=<text file with a list of photos or a directory with photos>"
        print "\tThe only obligatory tag"
        print "--help"
        print "\tPrint help and exit"


# service function: get path of an executable (.exe suffix is added if we are on Windows)
def getExecPath(dir, fileName):
    if sys.platform == "win32": fileName = "%s.exe" % fileName
    return os.path.join(dir, fileName)