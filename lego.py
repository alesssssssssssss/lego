#.py version of the code

import cv2
import numpy as np
import matplotlib.pyplot as plt

#load stud image
stud1x1_path = f"Studs/1x1.png"
stud2x1_path = f"Studs/2x1.png"
stud2x2_path = f"Studs/2x2.png"
stud4x1_path = f"Studs/4x1.png"
stud2x4_path = f"Studs/2x4.png"

stud1x1 = cv2.imread(stud1x1_path, cv2.IMREAD_COLOR)
stud2x1 = cv2.imread(stud2x1_path, cv2.IMREAD_COLOR)
stud1x2 = cv2.rotate(stud2x1, cv2.ROTATE_90_CLOCKWISE)
stud2x2 = cv2.imread(stud2x2_path, cv2.IMREAD_COLOR)
stud4x1 = cv2.imread(stud4x1_path, cv2.IMREAD_COLOR)
stud1x4 = cv2.rotate(stud4x1, cv2.ROTATE_90_CLOCKWISE)
stud2x4 = cv2.imread(stud2x4_path, cv2.IMREAD_COLOR)
stud4x2 = cv2.rotate(stud2x4, cv2.ROTATE_90_COUNTERCLOCKWISE)

brick_list = {(4,2): stud4x2, 
              (2,4): stud2x4, 
              (4,1): stud4x1, 
              (1,4): stud1x4, 
              (2,2): stud2x2,
              (2,1): stud2x1,
              (1,2): stud1x2,
              (1,1): stud1x1
            }

brick_count = {
    "4x2": 0,
    "2x4": 0,
    "4x1": 0,
    "1x4": 0,
    "2x2": 0,
    "2x1": 0,
    "1x2": 0,
    "1x1": 0
}

def resize_brick(imgshape):
    #camera size is fixed as square
    img_height = imgshape[0]
    #fixed 100x100 bricks
    block_size = int(img_height/100)
    for brick in brick_list:
        w, h = brick
        brick_list[(w,h)] = cv2.resize(brick_list[(w,h)], (w*block_size, h*block_size), interpolation=cv2.INTER_NEAREST)

def pixelate(img):
    
    resize_brick(img.shape)

    img_height, img_width = img.shape[:2]
    #fixed 100x100 bricks
    block_size = int(img_height/100)

    #shrink to 100x100
    small = cv2.resize(img, (100,100), interpolation=cv2.INTER_AREA)
    #convert to grey scale
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    

    #color map for black white gray only
    #set new np array with img's shape, default all black
    bwg = np.zeros_like(gray)
    #set gray
    bwg[(gray >= 85)&(gray < 170)] = 127
    #set white
    bwg[gray >= 170] = 255

    bwg_height, bwg_width = bwg.shape[0], bwg.shape[1]
    cv2.imshow("small", small)
    cv2.imshow("gray small", gray)
    cv2.imshow("3colors", bwg)

    occupied = np.zeros((bwg_height, bwg_width), dtype=bool)

    #convert brick to (0 - 1.0)
    #brick_float = brick.astype(float) / 255.0
    
    #canvas for lego picture
    lego = np.zeros((img_height,img_width,3), dtype= np.uint8)
    

    #loop each pixel in bwg
    for x in range(bwg_width):
        for y in range(bwg_height):
            
            if occupied[y,x]:
                continue

            #get color
            color = small[y, x]
            color_float = color/255.0

            for i in brick_list:
                w, h = i
                # Boundary Check
                if y + h > bwg_height or x + w > bwg_width:
                    continue
                # Check if area is occupied
                if np.any(occupied[y:y+h, x:x+w]):
                    continue
                # Check Color Match
                region = small[y:y+h, x:x+w]
                if np.all(region == color):
                    # Place Brick
                    #change color of brick (black white gray)
                    #convert it back to (0 - 255)
                    tinted_brick = (brick_list[(w,h)] * color_float).astype(np.uint8)
                    # Calculate coordinates on canvas
                    y_start = y * block_size
                    y_end = y_start + block_size*h
                    x_start = x * block_size
                    x_end = x_start + block_size*w
                    # Paste into canvas
                    lego[y_start:y_end, x_start:x_end] = tinted_brick
                    #count brick
                    brick_count[f"{w}x{h}"] += 1
                    # Mark Occupied
                    occupied[y:y+h, x:x+w] = True
                    
                    # Break the shape loop (we found a fit for this pixel, move to next pixel)
                    break 

    print("Brick count")
    print(brick_count)
    total_bricks = sum(brick_count.values())
    print(f"Total bricks: {total_bricks}")

    return lego


def camera():
    cam = cv2.VideoCapture(0)
    #fixed it to square
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 2000)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2000)

    # Check if the camera opened successfully
    if not cam.isOpened():
        print("Error: Could not open video device.")
    else:
        print("Camera opened successfully.\nPress 'q' to exit.\nPress Spacebar to take picture")

    while True:
        
        ret, frame = cam.read()

        if ret:
            cv2.imshow('Live Camera', frame)
        else:
            print("Error: Failed to capture frame.")
            break

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):
            pixelated = pixelate(frame)
            
            cv2.imshow("pixelated capture", pixelated)
            

    # Release camera
    cam.release()
    # Destroy all windows
    cv2.destroyAllWindows()

if __name__ == "__main__": 
    camera()