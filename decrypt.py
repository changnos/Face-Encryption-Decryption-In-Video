from PIL import Image
import face_recognition
import cv2
import os
from random import randint
import numpy
import sys
from Image_Cryptography_master.helper import *

# Open the input video file
input_movie = cv2.VideoCapture('encrypted/' + sys.argv[1])
length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
w = round(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))
h = round(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = input_movie.get(cv2.CAP_PROP_FPS)

# Create an output video file
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_movie = cv2.VideoWriter('decrypted/' + sys.argv[1], fourcc, fps, (w, h))

frame_num = 1
while True:
    # Grab a single frame of video
    ret, frame = input_movie.read()

    # Quit when the input video file ends
    if not ret:
        break

    image = frame
   
    f_num = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/face_num.txt','r')
    face_num_value = int(f_num.readline())

    for face_num in range (1, face_num_value + 1):
            f_loc = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '_loc.txt','r')
            top = int(f_loc.readline())
            bottom = int(f_loc.readline())
            left = int(f_loc.readline())
            right = int(f_loc.readline())

#---------------------------------------- decryption ------------------------------------------------------------------------------------------------------------------------
            im = Image.open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '.PNG')
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

            Kr = []
            Kc = []

            f_Kr = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '_Kr_keys.txt','r')
            f_Kc = open('./key_values/' + sys.argv[1] + '_keys/' + str(frame_num) + 'frame_key_values/' + str(face_num) + '_Kc_keys.txt','r')

            for i in range(m):
                    Kr.append(int(f_Kr.readline()))

            for i in range(n):
                    Kc.append(int(f_Kc.readline()))

            #The number of iterations of encryption to be performed can be adjusted by changing the ITER_MAX value
            #Larger values will make encryption more secure but it is more time consuming
            ITER_MAX = 1
            for iterations in range(ITER_MAX):
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
                                    downshift(r,i,Kc[i])
                            else:
                                    upshift(r,i,Kc[i])
                            if(gModulus==0):
                                    downshift(g,i,Kc[i])
                            else:
                                    upshift(g,i,Kc[i])
                            if(bModulus==0):
                                    downshift(b,i,Kc[i])
                            else:
                                    upshift(b,i,Kc[i])

                    # For each row
                    for i in range(m):
                            rTotalSum = sum(r[i])
                            gTotalSum = sum(g[i])
                            bTotalSum = sum(b[i])
                            rModulus = rTotalSum % 2
                            gModulus = gTotalSum % 2
                            bModulus = bTotalSum % 2
                            if(rModulus==0):
                                    r[i] = numpy.roll(r[i],-Kr[i])
                            else:
                                    r[i] = numpy.roll(r[i],Kr[i])
                            if(gModulus==0):
                                    g[i] = numpy.roll(g[i],-Kr[i])
                            else:
                                    g[i] = numpy.roll(g[i],Kr[i])
                            if(bModulus==0):
                                    b[i] = numpy.roll(b[i],-Kr[i])
                            else:
                                    b[i] = numpy.roll(b[i],Kr[i])

            for i in range(m):
                    for j in range(n):
                            pix[i,j] = (b[i][j],g[i][j],r[i][j])

            image[top:bottom, left:right] = im

            face_num = face_num + 1

    output_movie.write(image)
    print("Writing frame {} / {}".format(frame_num, length))
    frame_num = frame_num + 1
    
input_movie.release()
output_movie.release()
cv2.destroyAllWindows()
