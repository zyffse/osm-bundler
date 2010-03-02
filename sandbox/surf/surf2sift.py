from math import pi
import gzip,os

# Read in list of images
f = open('list.txt','r')
images = f.readlines()
images[:] = [foo.strip('\n\r ') for foo in images]
f.close()

def SURF2SIFT(filename):
  # Read in the SURF file
  filename = filename[:-4]
  print 'Reading in SURF file %s.surf' % (filename)
  f = open(filename + '.surf','r')
  data = f.readlines()
  f.close()

  # Create the sift key file
  f = open(filename + '.key','w')
  n = int(data[0].strip())
  header = '%2d 128' % (n)
  f.write(header)

  # Convert data from SURF to SIFT
  # This removes the laplacian, converts the angle to radians
  # and normalises the descriptor to integers between 0 and 256
  print 'Converting data to SIFT format'
  for i in range(2,n):
    temp = data[i].split()
    foo = map(float,temp[:5])
    keypoint = '\n%5.3f %5.3f %5.1f %5.4f' % (foo[0],foo[1],foo[3],(float(foo[4])-190)*pi/180.0) 
    f.write(keypoint)
    desc = map(float,temp[5:])
    minimum, maximum = min(desc), max(desc)
    ran = 256.0 / (maximum - minimum)
    desc[:] = [int((x-minimum)*ran+0.5) for x in desc]
    i1 = 0
    for i2 in (20,40,60,80,100,120,128):
      f.write('\n ' + ' '.join(map(str,desc[i1:i2]))+' ')
      i1 = i2
  f.close()

  print 'Done, compressing to key file %s.key.gz\n' % (filename)
  f_in = open(filename+'.key', 'rb')
  f_out = gzip.open(filename+'.key.gz', 'wb')
  f_out.writelines(f_in)
  f_out.close()
  f_in.close()
  #os.remove(filename+'.key')

# Convert SURF files to SIFT keyfiles
for item in images:
  SURF2SIFT(item)
