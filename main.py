import time, os
from datetime import datetime
from collections import deque
import io

import cv2
import av
from flask import render_template, Response

from webVideoViewer import webViewer

class Downloader():
    """Class responsible for downloading and creating videos."""
    def __init__(self, downloadEvery, downloadResWidth, downloadPreviousTime=24):
        """
        Initialize the Downloader object.

        Args:
            downloadEvery (float): The time interval between frame downloads in seconds.
            downloadResWidth (int): The width of the downloaded frames.
            downloadPreviousTime (int, optional): The maximum amount of time to save frames for downloading in hours.
        """
        self.buffer = deque(maxlen=int(downloadPreviousTime*60*60*downloadEvery)) #< the max amount of frames in the video 
        self.first = True
        self.downloadPreviousTime = downloadPreviousTime                          #< the max amount of time to save in bugger for downloading                         
        self.timeBetweenReads = 1/downloadEvery                                   #< the amount of time to wait in seconds between reading frames
        self.downloadResWidth = downloadResWidth                                  #< the resolution to set the frame for downloading
        self.lastFrameTimestamp = time.time()                                     #< timestamp of the last frame added to the buffer

    def addFrame(self, frame) -> None:
        """
        Add a frame to the buffer.

        Args:
            frame (numpy.ndarray): The frame to add.
        """
        shape = (frame.shape[1], frame.shape[0])                                  #< the shape of the image
        if self.first == True:                                                    #< is it the first frame added
            self.first = False
            scaleFactor = self.downloadResWidth/shape[0]                          #< get the scale factor for resizing the image
            self.newWidth = int(self.downloadResWidth)                            #< the new width of the image
            self.newHeight = int(shape[1]*scaleFactor)                            #< the new height of the image

        if time.time()-self.lastFrameTimestamp >= self.timeBetweenReads:          #< is timeBetweenReads past since last frame was read
            if len(frame.shape) == 3:                                             #< Check if the frame is in color (has 3 channels)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                   #< Convert the frame to grayscale

            scaled = cv2.resize(frame, (self.newWidth, self.newHeight))           #< Resize the frame to the specified resolution

            self.buffer.append(scaled)                                            #< Add the resized frame to the buffer
            self.lastFrameTimestamp = time.time()                                 #< Update the timestamp of the last frame added

    def download(self):
        """
        Create a video file from the frames in the buffer.

        Returns:
            bytes: The video file data.
        """
        output = io.BytesIO()                                                     #< Create a BytesIO object to store the video file data
        container = av.open(output, 'w', format='mp4')                            #< Create a container with a video stream

        stream = container.add_stream('h264', rate=20)                            #< Add a video stream to the container
        stream.width = self.downloadResWidth                                      #< Set the width of the video stream
        stream.height = self.buffer[0].shape[0]                                   #< Set the height of the video stream

        buffer_copy = self.buffer.copy()                                          #< Create a copy of the buffer so i dont iterate over it while adding a frame to it

        for frame in buffer_copy:
            # Convert the frame to an AVFrame object
            av_frame = av.VideoFrame.from_ndarray(frame, format='gray')           #< Convert the frame to an AVFrame object

            packet = stream.encode(av_frame)                                      #< Encode the frame and write it to the video stream
            container.mux(packet)

        packet = stream.encode()                                                  #< Flush any remaining frames
        container.mux(packet) 
        container.close()

        output.seek(0)
        return(output.getvalue())

class VideoStream(webViewer.VideoStream):
    """Class representing a video streaming application."""
    def __init__(self,
                 homePageTemplate="./webVideoViewer/templates/home.html",
                 subpageTemplate="./templates/subpage.html",
                 port=80,
                 downloadEvery=0.5,
                 downloadResWidth=200,
                 downloadPreviousTime=24 #< in hours
                 ):
        """
        Initialize the VideoStream object.

        Args:
            homePageTemplate (str, optional): Path to the home page template file.
            subpageTemplate (str, optional): Path to the subpage template file.
            port (int, optional): The port number for running the Flask application.
            downloadEvery (float, optional): The time interval between frame downloads in seconds.
            downloadResWidth (int, optional): The width of the downloaded frames.
            downloadPreviousTime (int, optional): The maximum amount of time to save frames for downloading in hours.
        """

        super().__init__(homePageTemplate=homePageTemplate,
                         subpageTemplate=subpageTemplate,
                         port=port, currentFolder = os.path.dirname(os.path.abspath(__file__)))

        self.downloadPreviousTime = downloadPreviousTime                           #< The maximum amount of time to save frames for downloading (in hours)
        self.downloadEvery = downloadEvery                                         #< The time interval between frame downloads in seconds
        self.downloadResWidth = downloadResWidth                                   #< The width of the downloaded frames
        self.downloaders = {}                                                      #< Dictionary to store Downloader objects for each subpage

    def _getTimestamp(self) -> str:
        """
        Get the current timestamp as a formatted string.

        Returns:
            str: The formatted timestamp.
        """
        now = datetime.now()
        formattedTime = now.strftime('%Y-%m-%d___%H-%M-%S')
        return(formattedTime)

    def setupRoutes(self):
        """Set up the routes for the Flask application."""
        super().setupRoutes()
        self.app.route('/<name>/download')(self.download)                          #< Define the route for downloading the recorded video

    def renderTemplate(self, name):
        """
        Render the template for a given name.

        Args:
            name (str): The name of the template.

        Returns:
            str: The rendered template.
        """
        return(render_template(self.subpageTemplate,
                               video_feed=f"/{name}/videoFeed",
                               download_url=f"/{name}/download",
                               download_length=str(self.downloadPreviousTime))
               ) #< Render the subpage template

    def download(self, name):
        """
        Download the recorded video for a given name.

        Args:
            name (str): The name(subpage) associated with the video.

        Returns:
            Response: The response object containing the video file data.
        """
        try:
            downloader = self.downloaders[name]
            video_data = downloader.download()                                     #< Call the download method of the corresponding Downloader object
            fileName = f"last_{self.downloadPreviousTime}_hours_{self._getTimestamp()}.mp4"

            return(Response(
                video_data,
                mimetype='video/mp4',
                headers={'Content-Disposition': f'attachment; filename={fileName}'}
            ))
        except Exception as e:
            print(e)
            return('Error')

    def imshow(self, name, image):
        """
        Display an image on the subpage with the given name.

        Args:
            name (str): The name of the subpage.
            image (numpy.ndarray): The image to display.
        """
        super().imshow(name, image)                                                #< Call the imshow method of the parent class
        if name not in self.downloaders.keys():
            self.downloaders[name] = Downloader(self.downloadEvery,
                                                self.downloadResWidth,
                                                downloadPreviousTime=self.downloadPreviousTime
                                                )                                  #< Create a Downloader object for the subpage if it doesn't exist
        self.downloaders[name].addFrame(image)                                     #< Add the frame to the corresponding Downloader object

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    app = VideoStream(downloadPreviousTime=24)
    app.run()

    # Continuously capture frames from the webcam and update subpages
    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        app.imshow("frame", frame)
        app.imshow("gray", gray)
