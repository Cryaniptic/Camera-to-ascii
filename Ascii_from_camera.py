import sys

import cv2

import curses
stdscr = curses.initscr()

#=== OPTIONS ===

#Use terminal colours (warning: colours are very resouce intensive)
COLOUR_ON = True

#Open a cv2 window to view camera input
VEIWER_WINDOW = False

#===============

#Initialise Curses terminal
curses.noecho()
curses.cbreak()
stdscr.nodelay(1)
curses.start_color()

#Initialise OpenCV Window
if VEIWER_WINDOW:
    cv2.namedWindow("preview") #open a window
vc = cv2.VideoCapture(0) #Get camera input (set 0 to other values to get diffrent cameras)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

#get the size of the terminal
rows, cols = stdscr.getmaxyx() 
Width = cols - 1 #reduce size to make sure curses doesnt die
Height = rows -1

grad = [" ",".",":","-","=","+","*","#","%","@","█"]
grad.reverse()
#gradient for brightness
#add more characters if you want (just remember to make sure brightness is right (dark to light))

grad2_text = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,^`'. "
grad2 = [char for char in grad2_text] #a slightly bigger gradient (looks garbage, dont use)

if COLOUR_ON:
    # get rgb of all the terminal colours for calculating nearest colour
    colours = ( (255, 255, 255, 0),
                (197, 15, 31, 1),
                (19, 161, 14, 2),
                (193, 156, 0, 3),
                (0, 55, 218, 4),
                (136, 23, 152, 5),
                (58, 150, 221, 6),
                (0,0,0,7))

    #initialise all the colour pairs (curses is really dumb with this)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)


def nearest_colour( subjects, query ): 
    return min( subjects, key = lambda subject: sum( (s - q) ** 2 for s, q in zip( subject, query ) ) )
    #function to get nearest colour
    #does some stuff with cartesian distance and sorting

def image_to_grid(im, size_x,size_y):    
    #image processing
    im = cv2.resize(im,(size_x,size_y)) #Resizing to grid size
    if COLOUR_ON:
        im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB) #if colour is on, save a copy of the image as rgb colourspace
    imBk = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) #convert to black and white for gradient conversion
    imBk = cv2.equalizeHist(imBk) #Increase contrast to make sure the whole range of the gradient is covered
    
    max = 255 #max and min values that a pixel can go to
    min = 0
    
    for y in range(size_y):
        for x in range(size_x): #looping through every grid pos
            img_px = imBk[y][x] #getting a pixels value
            if COLOUR_ON:
                colour = nearest_colour(colours, im_rgb[y][x]) #get the nearest colour
                stdscr.addch(y, x, grad[round(translate(img_px, max, min, 0, len(grad)-1))], curses.color_pair(colour[3]))
                #setting each char on the terminal to corresponding pixel value (in colour)
            else:
                stdscr.addch(y, x, grad[round(translate(img_px, max, min, 0, len(grad)-1))])
                #same as above, just with only gradient values (without colour)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

while rval:
    if VEIWER_WINDOW:
        cv2.imshow("preview", frame) #display camera onto the window (if it is open)
        
    stdscr.clear() #clear the terminal
    
    rval, frame = vc.read() #set frame to the current camera frame
    
    image_to_grid(frame, Width, Height) #calling the function to set the terminal to the camera frame
    
    stdscr.refresh() #display terminal
    
    key = stdscr.getch() #exit condition
    if key == 27: # exit on ESC
        break
    
if VEIWER_WINDOW:
    cv2.destroyWindow("preview")
curses.endwin() #close/end stuff
