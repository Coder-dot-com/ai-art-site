from PIL import Image
import glob, os, math
import colorsys
import blog.utils.blog_page.gradienttupleFunctions as tf
import random
from quiz_site.settings import BASE_DIR

def create_gradient():
    hue = (random.randint(0, 360))/360
    startColor = colorsys.hls_to_rgb(hue, 0.95, 0.8)
    startColor = tuple([int(255*x) for x in startColor])
    endColorX = colorsys.hls_to_rgb((random.randint(0, 360))/360, (random.randint(75, 90))/100, (random.randint(50, 90))/100)
    endColorY = colorsys.hls_to_rgb((random.randint(0, 360))/360, (random.randint(75, 90))/100, (random.randint(41, 70))/100)
    size = (800, 800)

    im = Image.new("RGB", size, 'black')
    pixels = im.load()

    deltaX = ((endColorX[0]-startColor[0]) / float(size[0]), (endColorX[1]-startColor[1]) / float(size[0]), (endColorX[2]-startColor[2]) / float(size[0]))
    deltaY = ((endColorY[0]-startColor[0]) / float(size[0]), (endColorY[1]-startColor[1]) / float(size[0]), (endColorY[2]-startColor[2]) / float(size[0]))


    thisPixelX = ()
    thisPixelY = ()

    for j in range(im.size[1]):    # for every pixel:
        if (j != 0):
            thisPixelY = tf.addTuples(thisPixelY, deltaY)
        else:
            thispixelY = startColor

        for i in range(im.size[0]):
            if (i == 0 and j == 0) :
                thisPixelX = startColor
                thisPixelY = startColor
                pixels[i,j] = startColor
                continue
            if (i != 0):
                thisPixelX = tf.addTuples(thisPixelX, deltaX)
            else:
                thisPixelX = startColor
            add = tf.divTuple(tf.addTuples(thisPixelY, thisPixelX), 2)
            pixels[i,j] = tf.roundTuple(add)

    im.save(f'{BASE_DIR}/blog/utils/blog_page/gradient.jpg')


