import logging
import osmbundler

logging.basicConfig(level=logging.INFO)

# command line arguments:
#  - a file with a list of images or a directory with images 
#  - which feature extraction method to use
#  - how features are matched: manually or with KeyMatchFull

# initialize OsmBundler manager class
manager = osmbundler.OsmBundler()

manager.preparePhotos()

manager.extractFeatures()

manager.matchFeatures()

manager.doBundleAdjustment()

