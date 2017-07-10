import matplotlib.pyplot as plt
import numpy as np
import sys
import pygeoj
from rtree import index
from shapely.geometry import box, Polygon,shape, Point
import shapely
from shapely.strtree import STRtree
from osgeo import ogr

try:
	Truth = pygeoj.load(sys.argv[1])
	Segments = pygeoj.load(sys.argv[2])
except:
	print "Enter geo jason files to load"
Geo_Truths = []
Geo_Segments = []
count = 0
for feature in Truth:
    Geo_Truths.append(shape(feature.geometry))# turn the geojason file into shapely polygon
    count +=1

print "Found: ",count," Features in ", sys.argv[1]
# do the same for the Segments
count = 0
for feature in Segments:
    Geo_Segments.append(shape(feature.geometry))
    count +=1
print "Found: ",count," Features in ", sys.argv[2]


s = STRtree(Geo_Truths) #use an stree to calculate the intersects
threshold = .45
average_IOU = 0 # keep track of the average IOUs
IOUs = []
indexes = []
FN = 0
for i in range(len(Geo_Segments)):
    results = s.query(Geo_Segments[i])
    if not results: # if the Segment dosen't match add it to false positive
        FN += 1 #didn't intersect any truths, false positive
    else:
        for polygon in results:
            index = Geo_Truths.index(polygon)
            IOUs.append(polygon.intersection(Geo_Segments[i]).area/polygon.union(Geo_Segments[i]).area)

thresholds = [.15,.25,.35,.45,.55,.65,.75,.85,.95]
recalls = []
precisions = []

for threshold in thresholds:
    TP = 0  # true positves
    FP = 0  # False Negatives
    for iou in IOUs:
        if iou > threshold:
            TP +=1
        else:
            FP +=1
    print "False Positives:",FP, "\nTrue Positives:",TP, "\nFalse Negatives:", FN
    print "At threshold: ", iou,"\n"
    recalls.append(TP/float(TP+FN))
    precisions.append(TP/float(TP+FP))

plt.plot(precisions,recalls)
plt.xlabel("Prescision")
plt.ylabel("Recall")
plt.title('ROC curves for .15:.1:.95 Increments of IOU Threshold ')
plt.grid(True)


plt.show()
