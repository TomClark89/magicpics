"""
Kmeans clustering algorithm for colour detection in images

Initialise a kmeans object and then use the run() method.
Several debugging methods are available which can help to
show you the results of the algorithm.
"""

from PIL import Image, ImageDraw
import random
import numpy
import colorsys
import os

class Cluster(object):

    def __init__(self):
        self.pixels = []
        self.centroid = None

    def addPoint(self, pixel):
        self.pixels.append(pixel)

    def setNewCentroid(self):

        R = [colour[0] for colour in self.pixels]
        G = [colour[1] for colour in self.pixels]
        B = [colour[2] for colour in self.pixels]

        R = int(sum(R) / len(R))
        G = int(sum(G) / len(G))
        B = int(sum(B) / len(B))

        self.centroid = (R, G, B)
        self.pixels = []

        return self.centroid


class Kmeans(object):

    def __init__(self, k=5, max_iterations=4, min_distance=5.0, size=100):
        self.k = k
        self.max_iterations = max_iterations
        self.min_distance = min_distance
        self.size = (size, size)

    def run(self, image):
        self.image = image
        self.image.thumbnail(self.size)
        self.pixels = numpy.array(list(image.getdata()), dtype=numpy.uint8)

        self.clusters = [None for i in range(self.k)]
        self.oldClusters = None

        while True:
            randomPixels = random.sample(list(self.pixels), self.k)
            centroid_list = []
            for idx in range(self.k):
                self.clusters[idx] = Cluster()
                self.clusters[idx].centroid = randomPixels[idx]
                centroid_list.append(randomPixels[idx])

            duplicates = False
            for centroid in centroid_list:
                count = 0
                for centroid2 in centroid_list:
                    if (centroid[0],centroid[1],centroid[2]) == (centroid2[0],centroid2[1],centroid2[2]):
                        count = count + 1
                if count > 1:
                    duplicates = True
                    break

            if not duplicates:
                break



        iterations = 0

        while self.shouldExit(iterations) is False:

            self.oldClusters = [cluster.centroid for cluster in self.clusters]

            #print ("Iterations: " + str(iterations))
            for pixel in self.pixels:
                self.assignClusters(pixel)
                # looks like it's messing up here - found it at last!
                # needs to assign at least one pixel to all

            count = 0
            for cluster in self.clusters:
                count = count + 1
                #print ("cluster " + str(count) + ": ",len(cluster.pixels),cluster.centroid)

            for cluster in self.clusters:
                cluster.setNewCentroid()

            iterations += 1

        return [cluster.centroid for cluster in self.clusters]

    def assignClusters(self, pixel):
        shortest = float('Inf')
        for cluster in self.clusters:
            distance = self.calcDistance(cluster.centroid, pixel)
            if distance < shortest:
                shortest = distance
                nearest = cluster


        nearest.addPoint(pixel)

    def calcDistance(self, a, b):

        result = numpy.sqrt(sum((a - b) ** 2))
        return result

    def shouldExit(self, iterations):

        if self.oldClusters is None:
            return False

        for idx in range(self.k):
            dist = self.calcDistance(
                numpy.array(self.clusters[idx].centroid),
                numpy.array(self.oldClusters[idx])
            )
            if dist < self.min_distance:
                return True

        if iterations <= self.max_iterations:
            return False

        return True

    # ############################################
    # The remaining methods are used for debugging
    def showImage(self):
        self.image.show()

    def showCentroidColours(self):

        for cluster in self.clusters:
            image = Image.new("RGB", (200, 200), cluster.centroid)
            image.show()

    def showClustering(self):

        localPixels = [None] * len(self.image.getdata())

        for idx, pixel in enumerate(self.pixels):
                shortest = float('Inf')
                for cluster in self.clusters:
                    distance = self.calcDistance(cluster.centroid, pixel)
                    if distance < shortest:
                        shortest = distance
                        nearest = cluster

                localPixels[idx] = nearest.centroid

        w, h = self.image.size
        localPixels = numpy.asarray(localPixels)\
            .astype('uint8')\
            .reshape((h, w, 3))

        colourMap = Image.fromarray(localPixels)
        colourMap.show()

    def showCombinedCentroidColours(self):
        image = Image.new("RGB",(200, 200*self.k),"white")
        i = 0
        for cluster in self.clusters:
            ImageDraw.Draw(image).polygon([(0,i * 200),(200,i * 200),(200,200 + i * 200),(0,200 + i * 200)], fill = cluster.centroid)
            i = i + 1
        image.show()


def testForColours(image_path):
    image_path = image_path
    try:
        image = Image.open(image_path)
    except PermissionError:
        return "Not found"
    k = Kmeans()
    try:
        result = k.run(image)
    except ZeroDivisionError:
        return "Not found"

    hsv_result = []
    for colour in result:
        hsv_colour = colorsys.rgb_to_hsv(colour[0]/255,colour[1]/255,colour[2]/255)
        hsv_colour = [int(hsv_colour[0]*360), int(hsv_colour[1]*100), int(hsv_colour[2]*100)]
        hsv_result.append(hsv_colour)

        #green is 81 to 140
        #purpley pink is 241 345
    pink_found = False
    green_found = False
    for hsv_colour in hsv_result:
        if 61 <= hsv_colour[0] <= 140:
            #print ("green", hsv_colour[0])
            pink_found = True
        elif 241 <= hsv_colour[0] <= 345:
            #print ("pink", hsv_colour[0])
            green_found = True

    #print(image_path,hsv_result)

    if pink_found and green_found:
        return "Found"
    else:
        return "Not found"


    #k.showImage()
    #k.showCentroidColours()
    #k.showCombinedCentroidColours()
    #k.showClustering()


if __name__ == "__main__":
    image_folder = "downloaded_images"
    max_filename = 0
    padding = 5
    for file in os.listdir(image_folder):
        if not os.path.isdir(os.path.join(image_folder,file)):
            if len(file) > max_filename:
                max_filename = len(file)
    i = 0
    for file in os.listdir(image_folder):
        if not os.path.isdir(os.path.join(image_folder,file)):
            i = i + 1
            test_results = testForColours(os.path.join(image_folder,file))
            print(str(i).rjust(3) + ": " + file.ljust(max_filename + padding) + test_results)
            if test_results == "Found":
                os.rename(os.path.join(image_folder,file),os.path.join(image_folder,"found",file))
