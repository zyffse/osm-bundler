import cv
from cv import CV_BGR2GRAY

# Read in images to process
f = open('list.txt','r')
images = f.readlines()
f.close()

def SURF(filename):
  # Load file and convert to gray scale
  img = cv.LoadImage(filename)
  object1 = cv.CreateImage([img.width,img.height], 8, 1)
  cv.CvtColor(img, object1, CV_BGR2GRAY)

  # Create storage and extract features
  storage= cv.CreateMemStorage(0)
  print 'Starting keypoint extraction for %s' % (filename)
  keypoints, descriptors = cv.ExtractSURF(object1, None, storage, [1,300,3,4])

  # Create SURF file
  print 'Keypoint extraction complete, printing to file %s' % (filename[:-4]+'.surf')
  f = open(filename[:-4]+'.surf','w')
  header = '%2d\n' % (len(keypoints))
  f.write(header)
  f.write('# Columns: X - Y - Laplacian - Scale - Rotation - 128-dimension descriptor')

  # Write features to file
  for i in range(len(keypoints)):
    string = '\n%5.3f %5.3f %1d %3.1f %5.4f ' % (keypoints[i][0][0],keypoints[i][0][1],keypoints[i][1],keypoints[i][2],keypoints[i][3])
    string += " ".join(str(n) for n in descriptors[i][0:128])
    f.write(string)
  f.close()

for image in images:
  SURF(image.strip('\n'))
