"""
Digital Scope render a cross over the video feed.
Move the cross hair to the clicked location. 
You can also click and drag to the correct location and then
release the mouse button.
"""

import cv2
import numpy
from threading import Thread

CROSSHAIR_COLOR = (0, 0, 255)
CROSSHAIR_CENTER_SPACE = 10
CROSSHAIR_ACCENT1_LENGTH = 21
CROSSHAIR_ACCENT2_LENGTH = 20
CV_CAP_PROP_FPS = 5
CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4
TITLE = 'Digital Scope - Q to quit.'


def setCrossHair(mouseX, mouseY, mouseDown):
    """
    Set the crossHairY and crossHairX variable
    @param mouseX: The recorded x mouse location
    @type mouseX: int
    @param mouseY: The recorded y mouse location
    @type mouseY: int
    """
    if not mouseDown:
        return
    global crossHairY
    global crossHairX
    crossHairY = mouseY
    crossHairX = mouseX


def getMouseCoordinates(event, x, y, flags, param):
    """
    Manage mouse interactions with the rendering of the cross hair
    @param event: A cv event(cv enum)
    @type event: int 
    @param x: The recorded x location
    @type x: int
    @param y: The recorded y location
    @type y: int
    @param flags: required but not used
    @param param: required but not used
    """
    global mouseDown
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseDown = True
        setCrossHair(x, y, mouseDown)
    elif event == cv2.EVENT_LBUTTONUP:
        mouseDown = False
    elif event == cv2.EVENT_MOUSEMOVE:
        setCrossHair(x, y, mouseDown)


def renderLine(image, point1, point2, color, thickness):
    """
    Add a line to the passed image
    @param image: An image
    @type image: numpy array
    @param point1: First point of the line segment
    @type point1: tuple
    @param point2: Second point of the line segment
    @type point2: tuple
    @param color: BGR Color
    @type color: tuple
    @param thickness: Line thickness
    @type thickness: int
    @return: img
    @rtype: numpy array
    """
    return cv2.line(image, point1, point2, color, thickness)


def renderCircle(image, center, radius, color, thickness):
    """
    Add a cirle to the passed image
    @param image: An image
    @type image: numpy array
    @param center: Center point of the circle
    @type center: tuple
    @param radius: Radius of the circle
    @type radius: int
    @param color: BGR Color
    @type color: tuple
    @param thickness: Positive - Thickness of the circle outline.
                      Negative - A filled circle is to be drawn.
    @type thickness: int
    @return: img
    @rtype:  numpy array
    """
    return cv2.circle(image, center, radius, color, thickness)


def renderCrossHair(frame, crossHairX, crossHairY, imageWidth, imageHeight):
    """
    Render the crosshair over the passed image
    @param frame: An image
    @type frame: numpy array
    @param crossHairX: Screen x location
    @type crossHairX: int
    @param crossHairY: Screen y location
    @type crossHairY: int
    @param imageWidth: Width of the image
    @type imageWidth: int
    @param imageHeight: Height of the image
    @type imageHeight: int
    """
    img = renderLine(frame,
                     (0, crossHairY),
                     (crossHairX - CROSSHAIR_CENTER_SPACE, crossHairY),
                     CROSSHAIR_COLOR,
                     1)
    img = renderLine(img,
                     (crossHairX + CROSSHAIR_CENTER_SPACE, crossHairY),
                     (imageWidth - 1, crossHairY),
                     CROSSHAIR_COLOR,
                     1)
    img = renderLine(img,
                     (crossHairX, 0),
                     (crossHairX, crossHairY - CROSSHAIR_CENTER_SPACE),
                     CROSSHAIR_COLOR,
                     1)
    img = renderLine(img,
                     (crossHairX, crossHairY + CROSSHAIR_CENTER_SPACE),
                     (crossHairX, imageHeight - 1 ),
                     CROSSHAIR_COLOR,
                     1)
    img = renderCircle(img,
                       (crossHairX, crossHairY),
                       1,
                       CROSSHAIR_COLOR,
                       -1)
    img = renderLine(img,
                     (0, crossHairY),
                     (CROSSHAIR_ACCENT2_LENGTH, crossHairY),
                     CROSSHAIR_COLOR,
                     3)
    img = renderLine(img,
                     (imageWidth - CROSSHAIR_ACCENT1_LENGTH, crossHairY),
                     (imageWidth - 1, crossHairY),
                     CROSSHAIR_COLOR,
                     3)
    img = renderLine(img,
                     (crossHairX, 0),
                     (crossHairX, CROSSHAIR_ACCENT2_LENGTH),
                     CROSSHAIR_COLOR,
                     3)
    img = renderLine(img,
                     (crossHairX, imageHeight - CROSSHAIR_ACCENT1_LENGTH),
                     (crossHairX, imageHeight - 1),
                     CROSSHAIR_COLOR,
                     3)
    return img


def defaultCrossHair(capture):
    """
    Set the mouse and crossHair values for a perfectly centered crossHair
    @return: imageWidth, imageHeight, crossHairX, crossHairY
    @rtype: int, int, int, int
    """
    imageWidth = int(capture.stream.get(CV_CAP_PROP_FRAME_WIDTH))
    imageHeight = int(capture.stream.get(CV_CAP_PROP_FRAME_HEIGHT))
    crossHairY = imageHeight/2
    crossHairX = imageWidth/2
    return imageWidth, imageHeight, crossHairX, crossHairY


class VideoStream:
    """
    Video Stream class to increase the performance of the video feed
    Referenced: http://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
    """
    def __init__(self, source=0):
        """
        Initialize the stream and read the first image
        @param source: Video source device
        @type source: int
        """
        self.stream = cv2.VideoCapture(source)
        self.grabbed = None
        self.frame = None
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        """
        Start the tread for reading frames
        """
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """
        Read frames until self.stopped is True
        """
        while True:
            if self.stopped:
                return
            self.grabbed, self.frame = self.stream.read()

    def read(self):
        """
        Returns the last frame read
        """
        return self.frame

    def stop(self):
        """
        Stops the thread
        """
        self.stopped = True
        self.stream.release()


mouseDown = False

cv2.namedWindow(TITLE)
cv2.setMouseCallback(TITLE, getMouseCoordinates)
capture = VideoStream().start()
if not capture.stream.isOpened():
    capture.stream.open(0)
imageWidth, imageHeight, crossHairX, crossHairY = defaultCrossHair(capture)

while True:
    # Capture frame-by-frame
    frame = capture.read()
    img = renderCrossHair(frame, crossHairX, crossHairY, imageWidth, imageHeight)
    cv2.imshow(TITLE, img)
    # Use the "Q" key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
capture.stop()
cv2.destroyAllWindows()
