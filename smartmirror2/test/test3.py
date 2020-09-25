import cv2
import numpy as np

properties = { 
    0: "CV_CAP_PROP_POS_MSEC Current position of the video file in milliseconds.",
    1: "CV_CAP_PROP_POS_FRAMES 0-based index of the frame to be decoded/captured next.",
    2: "CV_CAP_PROP_POS_AVI_RATIO Relative position of the video file",
    3: "CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream.",
    4: "CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream.",
    5: "CV_CAP_PROP_FPS Frame rate.",
    6: "CV_CAP_PROP_FOURCC 4-character code of codec.",
    7: "CV_CAP_PROP_FRAME_COUNT Number of frames in the video file.",
    8: "CV_CAP_PROP_FORMAT Format of the Mat objects returned by retrieve().",
    9: "CV_CAP_PROP_MODE Backend-specific value indicating the current capture mode.",
    10: "CV_CAP_PROP_BRIGHTNESS Brightness of the image (only for cameras).",
    11: "CV_CAP_PROP_CONTRAST Contrast of the image (only for cameras).",
    12: "CV_CAP_PROP_SATURATION Saturation of the image (only for cameras).",
    13: "CV_CAP_PROP_HUE Hue of the image (only for cameras).",
    14: "CV_CAP_PROP_GAIN Gain of the image (only for cameras).",
    15: "CV_CAP_PROP_EXPOSURE Exposure (only for cameras).",
    16: "CV_CAP_PROP_CONVERT_RGB Boolean flags indicating whether images should be converted to RGB.",
    17: "CV_CAP_PROP_WHITE_BALANCE Currently unsupported",
    18: "CV_CAP_PROP_RECTIFICATION Rectification flag for stereo cameras (note: only supported by DC1394 v 2.x backend currently)"
}

cam = cv2.VideoCapture(0)
#for i in range(len(properties.keys())):
    #print(i, properties[i], cam.get(i))

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
fgbg = cv2.createBackgroundSubtractorMOG2()

ret, init_frame = cam.read()
init_frame = cv2.resize(init_frame, (640, 480))
init_frame = cv2.flip(init_frame, 1)

ROI_SIZE = 250
begin_X, begin_Y = int(init_frame.shape[1] - ROI_SIZE), 0
end_X, end_Y = init_frame.shape[1], ROI_SIZE

while True:
    ret, frame = cam.read()
    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)

    #roi = frame[begin_Y:end_Y, begin_X:end_X]

    fgmask = fgbg.apply(frame)
    #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cv2.filter2D(fgmask, -1, disc, fgmask)

    ret, thresh = cv2.threshold(fgmask, 0, 250, cv2.THRESH_BINARY)
    #thresh = cv2.merge((thresh, thresh, thresh))

    cv2.GaussianBlur(fgmask, (3,3), 0, fgmask)

    fgmask = cv2.bitwise_and(fgmask, thresh)

    cv2.imshow('frame',fgmask)    # if the 'q' key is pressed, stop the loop
    if cv2.waitKey(100) & 0xFF == ord("q"):
        break
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()