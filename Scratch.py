from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
from robotpi_Cmd import UPComBotCommand
from robotpi_serOp import serOp
from rev_cam import rev_cam


class QRscan:
    def __init__(self):
        # construct the argument parser and parse the arguments
        self.cmd = UPComBotCommand()
        self.ser = serOp()
        self.ap = argparse.ArgumentParser()
        self.ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                             help="path to output CSV file containing barcodes")
        self.args = vars(self.ap.parse_args())
        self.text = ""

        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        # vs = VideoStream(usePiCamera=True).start()

        # open the output CSV file for writing and initialize the set of
        # barcodes found thus far
        self.csv = open(self.args["output"], "w")
        self.found = set()

        # loop over the frames from the video stream
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels

    def scan(self, frame):
        name = ""
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)
        (x, y, w, h) = (0, 0, 0, 0)
        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw
            # the bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            name = barcodeData
            # draw the barcode data and barcode type on the image
            self.text = "{} ".format(barcodeData)
            cv2.putText(frame, self.text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # if the barcode text is currently not in our CSV file, write
            # the timestamp + barcode to disk and update the set
            if barcodeData not in self.found:
                self.csv.write("{},{}\n".format(datetime.datetime.now(),
                                                barcodeData))
                self.csv.flush()
                self.found.add(barcodeData)

        # show the output frame
        cv2.imshow("Barcode Scanner", frame)
        return name, (x, y, w, h)


def sendQR(text, location):
    ascData = [0] * 12
    asc = 0
    for i in location:
        ascData[asc] = ((i << 8) >> 8) & 0xFF
        ascData[asc + 1] = (i >> 8) & 0xFF
        asc += 2
    if text:
        for k in text:
            ascData.append(ord(k))
    else:
        return
    command, length = s.cmd.GenerateCmd(0x09, 0x50, len(ascData), ascData)
    s.ser.write_serial(command)



if __name__ == '__main__':
    s = QRscan()
    vs = VideoStream(src=0, resolution=(160, 120), framerate=10).start()
    time.sleep(2.0)
    text = ""

    while True:
        frame = vs.read()
        frame = rev_cam(frame)
        frame = imutils.resize(frame, width=400)

        text, location = s.scan(frame)
        print("text:", text, "location:", location)
        sendQR(text, location)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
