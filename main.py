from flask import Flask, render_template, Response, send_file
import cv2
import av
import os
import base64
import threading
import time
import io
from datetime import datetime
from collections import deque

from webVideoViewer import webViewer

class Downloader:
    def __init__(self, downloadFPS, downloadResWidth):
        self.buffer = deque(maxlen=int(60*60*downloadFPS))
        self.first = True
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.timeBetweenReads = 1/downloadFPS
        self.downloadResWidth = downloadResWidth
        self.lastFrameTimestamp = time.time()

    def addFrame(self, frame):
        shape = (frame.shape[1], frame.shape[0])
        if self.first == True:
            self.first = False
            scaleFactor = self.downloadResWidth/shape[0]
            self.newWidth = int(self.downloadResWidth)
            self.newHeight = int(shape[1]*scaleFactor)



        if time.time()-self.lastFrameTimestamp >= self.timeBetweenReads:
            if len(frame.shape) == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            scaled = cv2.resize(frame, (self.newWidth, self.newHeight))

            self.buffer.append(scaled)
            self.lastFrameTimestamp = time.time()

    def download(self):
        output = io.BytesIO()
        # Create a container with a video stream
        container = av.open(output, 'w', format='mp4')

        # Add a video stream to the container
        stream = container.add_stream('h264', rate=20)
        stream.width = self.downloadResWidth
        stream.height = self.buffer[0].shape[0]

        # Create a copy of the buffer before iterating over it
        buffer_copy = self.buffer.copy()

        for frame in self.buffer:
            # Convert the frame to an AVFrame object
            av_frame = av.VideoFrame.from_ndarray(frame, format='gray')

            # Rescale the frame if necessary
##            if frame.width != stream.width or frame.height != stream.height:
##                av_frame = av_frame.reformat(stream.width, stream.height)

            # Encode the frame and write it to the video stream
            packet = stream.encode(av_frame)
            container.mux(packet)

        # Flush any remaining frames
        packet = stream.encode()
        container.mux(packet)
        container.close()

        output.seek(0)
        return(output.getvalue())

    def _getTimestamp(self):
        now = datetime.now()
        formattedTime = now.strftime('%Y-%m-%d___%H-%M-%S')
        return (formattedTime)

class VideoStream(webViewer.VideoStream):
    def __init__(self,
                 homePageTemplate="./webVideoViewer/templates/home.html",
                 subpageTemplate="./templates/subpage.html",
                 port=80,
                 downloadFPS=0.5,
                 downloadResWidth=200
                 ):

        super().__init__(homePageTemplate=homePageTemplate,
                         subpageTemplate=subpageTemplate,
                         port=port, currentFolder = os.path.dirname(os.path.abspath(__file__)))

        self.downloadFPS = downloadFPS
        self.downloadResWidth = downloadResWidth
        self.downloaders = {}

        # Buffer to hold frames for 1 hour (60 minutes * 60 seconds)


    def setupRoutes(self):
        super().setupRoutes()
        self.app.route('/<name>/download')(self.download)

    def renderTemplate(self, name):
        return render_template(self.subpageTemplate, video_feed=f"/{name}/videoFeed", download_url=f"/{name}/download")

    def download(self, name):
        try:
            downloader = self.downloaders[name]
            video_data = downloader.download()

            return Response(
                video_data,
                mimetype='video/mp4',
                headers={'Content-Disposition': 'attachment; filename=last_24_hours.mp4'}
            )
        except Exception as e:
            print(e)
            return 'Error'

    def imshow(self, name, image):
        super().imshow(name, image)
        if name not in self.downloaders.keys():
            self.downloaders[name] = Downloader(self.downloadFPS, self.downloadResWidth)
        self.downloaders[name].addFrame(image)

if __name__ == '__main__':
    app = VideoStream()
    cap = cv2.VideoCapture(0)
    
    app.run()
    
    # Continuously capture frames from the webcam and update subpages
    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        app.imshow("frame", frame)
        app.imshow("gray", gray)
