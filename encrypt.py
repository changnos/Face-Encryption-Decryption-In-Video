from PIL import Image
import face_recognition
import cv2
import os
from random import randint
import numpy
import sys
from Image_Cryptography_master.helper import *

# Open the input video file
input_movie = cv2.VideoCapture(sys.argv[1])
length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
w = round(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))
h = round(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = input_movie.get(cv2.CAP_PROP_FPS)

# Create an output video file
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_movie = cv2.VideoWriter('encrypted/' + sys.argv[1], fourcc, fps, (w, h))

os.mkdir('./key_values/' + sys.argv[1] + '_keys')

frame_num = 1
while True:
    # Grab a single frame of video
    ret, frame = input_movie.read()

    # Quit when the input video file ends
    if not ret:
        break

#---------------------------------------- face_detection ------------------------------------------------------------------------------------------------------------------------
    image = frame
    face_locations = face_recognition.face_locations(image)

    face_num = len(face_locations)

    os.mkdir('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values')
    f_num = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/face_num.txt','w+')
    f_num.write(str(face_num))

    face_num = 1# number of detected faces
    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        #print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        f_loc = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '_loc.txt','w+')
        f_loc.write(str(top) + '\n')
        f_loc.write(str(bottom) + '\n')
        f_loc.write(str(left) + '\n')
        f_loc.write(str(right) + '\n')
        
        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]

#---------------------------------------- encryption ------------------------------------------------------------------------------------------------------------------------
        im = Image.fromarray(face_image)
        pix = im.load()

        #Obtaining the RGB matrices
        r = []
        g = []
        b = []
        for i in range(im.size[0]):
                r.append([])
                g.append([])
                b.append([]) 
                for j in range(im.size[1]):
                        rgbPerPixel = pix[i,j]
                        r[i].append(rgbPerPixel[0])
                        g[i].append(rgbPerPixel[1])
                        b[i].append(rgbPerPixel[2])

        m = im.size[0]
        n = im.size[1]

        # Vectors Kr and Kc
        alpha = 8
        Kr = [randint(0,pow(2,alpha)-1) for i in range(m)]
        Kc = [randint(0,pow(2,alpha)-1) for i in range(n)]

        f_Kr = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '_Kr_keys.txt','w+')
        f_Kc = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '_Kc_keys.txt','w+')

        for a in Kr:
                f_Kr.write(str(a) + '\n')
                
        for a in Kc:
                f_Kc.write(str(a) + '\n')

        #The number of iterations of encryption to be performed can be adjusted by changing the ITER_MAX value
        #Larger values will make encryption more secure but it is more time consuming
        ITER_MAX = 1
        for iterations in range(ITER_MAX):
                # For each row
                for i in range(m):
                        rTotalSum = sum(r[i])
                        gTotalSum = sum(g[i])
                        bTotalSum = sum(b[i])
                        rModulus = rTotalSum % 2
                        gModulus = gTotalSum % 2
                        bModulus = bTotalSum % 2
                        if(rModulus==0):
                                r[i] = numpy.roll(r[i],Kr[i])
                        else:
                                r[i] = numpy.roll(r[i],-Kr[i])
                        if(gModulus==0):
                                g[i] = numpy.roll(g[i],Kr[i])
                        else:
                                g[i] = numpy.roll(g[i],-Kr[i])
                        if(bModulus==0):
                                b[i] = numpy.roll(b[i],Kr[i])
                        else:
                                b[i] = numpy.roll(b[i],-Kr[i])
                # For each column
                for i in range(n):
                        rTotalSum = 0
                        gTotalSum = 0
                        bTotalSum = 0
                        for j in range(m):
                                rTotalSum += r[j][i]
                                gTotalSum += g[j][i]
                                bTotalSum += b[j][i]
                        rModulus = rTotalSum % 2
                        gModulus = gTotalSum % 2
                        bModulus = bTotalSum % 2
                        if(rModulus==0):
                                upshift(r,i,Kc[i])
                        else:
                                downshift(r,i,Kc[i])
                        if(gModulus==0):
                                upshift(g,i,Kc[i])
                        else:
                                downshift(g,i,Kc[i])
                        if(bModulus==0):
                                upshift(b,i,Kc[i])
                        else:
                                downshift(b,i,Kc[i])
                # For each row
                for i in range(m):
                        for j in range(n):
                                if(i%2==1):
                                        r[i][j] = r[i][j] ^ Kc[j]
                                        g[i][j] = g[i][j] ^ Kc[j]
                                        b[i][j] = b[i][j] ^ Kc[j]
                                else:
                                        r[i][j] = r[i][j] ^ rotate180(Kc[j])
                                        g[i][j] = g[i][j] ^ rotate180(Kc[j])
                                        b[i][j] = b[i][j] ^ rotate180(Kc[j])
                # For each column
                for j in range(n):
                        for i in range(m):
                                if(j%2==0):
                                        r[i][j] = r[i][j] ^ Kr[i]
                                        g[i][j] = g[i][j] ^ Kr[i]
                                        b[i][j] = b[i][j] ^ Kr[i]
                                else:
                                        r[i][j] = r[i][j] ^ rotate180(Kr[i])
                                        g[i][j] = g[i][j] ^ rotate180(Kr[i])
                                        b[i][j] = b[i][j] ^ rotate180(Kr[i])

        for i in range(m):
                for j in range(n):
                        pix[i,j] = (r[i][j],g[i][j],b[i][j])

        image[top:bottom, left:right] = im

        cv2.imwrite('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '.PNG',image[top:bottom, left:right])

        face_num = face_num + 1

    output_movie.write(image)
    print("Writing frame {} / {}".format(frame_num, length))
    frame_num = frame_num + 1

input_movie.release()
output_movie.release()
cv2.destroyAllWindows()
