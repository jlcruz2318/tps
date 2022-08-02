import boto3
from itertools import groupby
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image

SCALE_FACTOR = 50

def detect_vehicles():
    client = boto3.client('rekognition')


    with open('test-image.png', 'rb') as source_image:
        source_bytes = source_image.read()

    response = client.detect_labels(Image={'Bytes': source_bytes}, MaxLabels=1)
    image = Image.open("test-image.png")
    img_width, img_height = image.size
    ones = np.ones(img_width, dtype = int)
    
    car_detection_data = {}
    print('[x1,x2 COORDINATES FOR DETECTTIONS BELOW]')
    for label in response['Labels']:
        for boundingbox in label['Instances']:
            width, left = boundingbox['BoundingBox']['Width'], \
                boundingbox['BoundingBox']['Left']
            x = int(img_width*left)
            y = int((img_width*width)+(img_width*left))
            ones[x:y] = 0
            print(f'x1-Coordinate: {x}, x2-Coordinate: {y}')

    print(f'[DETECTIONS AS ARRAY]\n {ones}') 

    # # Debug - Plot the ones in an image - can be overlayed with image    
    plt.imshow((ones,ones,ones), interpolation='nearest')
    plt.title('[DETECTION ARRAY AS A PLOT]')
    plt.savefig('image_data_img.png',bbox_inches='tight', pad_inches=0)
    # plt.show() # Debug

    # Check if the length of pixels able to fit a car is smaller than
    # the largest available space in the picture
    x = 'green' if max([len(list(g)) for k, g in groupby(ones) if k == 1])>\
        SCALE_FACTOR else 'red'

    print('[SPACE AVAILABLE' if x == 'green' else '[NO SPACE AVAILABLE]')
    return x
      
detect_vehicles()
