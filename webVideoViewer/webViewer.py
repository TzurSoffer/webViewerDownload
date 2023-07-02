from flask import Flask, Response, render_template
import threading
import cv2
import os
import base64

class SubpageManager(dict):
    def __getitem__(self, __key):
        return(self.get(__key, None))

class VideoStream():
    """
    """
    def __init__(self, homePageTemplate="templates/home.html", subpageTemplate="templates/subpage.html", port=80, currentFolder=os.path.dirname(os.path.abspath(__file__))):
        """
        Initializes a VideoStream object.

        Args:
            homePageTemplate (str): Path to the home page template file.
            subpageTemplate (str): Path to the subpage template file.
            port (int): Port number for the Flask application.
            currentFolder (str): Path to the current folder containing the script.
        """
        self.app = Flask(__name__, template_folder=currentFolder)
        self.manager = SubpageManager()
        self.port = port

        self.setupRoutes()
        self.homePageTemplate = homePageTemplate
        self.subpageTemplate = subpageTemplate

    def setupRoutes(self) -> None:
        """Sets up the routes for the Flask application"""
        self.app.route('/')(self.index)  #< Define the route for the home page
        self.app.route('/<name>')(self.renderTemplate)  #< Define the route for the subpages
        self.app.route('/<name>/videoFeed')(self.subpage)  #< Define the route for the video feed of each subpage

    def index(self) -> str:
        """Returns the rendered HTML content for the home page"""
        return render_template(self.homePageTemplate, subpages=list(self.manager.keys()))  #< Render the home page template

    def renderTemplate(self, subpage) -> str:
        """Returns the rendered subpage(str)"""
        return render_template(self.subpageTemplate, video_feed=f"/{subpage}/videoFeed")  #< Render the subpage template

    def subpage(self, name):
        """
        Generates imgs for the subpage.

        Args:
            name (str): Name of the subpage.

        Returns:
            Response: Response object containing the generated imgs.
        """
        def generate_imgs():
            while True:
                img = self.manager[name]
                if img:
                    yield b'--img\r\n'
                    yield b'Content-Type: image/jpeg\r\n\r\n'
                    yield base64.b64decode(img)  #< Return the img in the response
                else:
                    yield b'--img\r\n'
                    yield b'Content-Type: text/html\r\n\r\n'
                    yield b'<h1>No subpage found for {name}</h1>\r\n\r\n'  #< Return a message if no img is found for the subpage

        return Response(generate_imgs(), mimetype='multipart/x-mixed-replace; boundary=img')  #< Return the response object

    def imshow(self, name, img) -> None:
        """
        Displays an image on a subpage.

        Args:
            name (str): Name of the subpage.
            img: Image to be displayed.
        """
        _, buffer = cv2.imencode('.jpg', img)          #< Encode the img as a JPEG image
        img = base64.b64encode(buffer).decode('utf-8') #< Encode the image data as base64 string
        self.manager[name] = img                       #< Store the img in the SubpageManager

    def run(self) -> None:
        """Runs the Flask application in a separate thread"""
        threading.Thread(target=self.app.run, kwargs={"host": "0.0.0.0", "port": self.port}).start()  #< Run the Flask application in a separate thread


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)  #< Open the webcam capture device
    app = VideoStream()        #< Create a VideoStream object
    app.run()                  #< Run the Flask application

    # Continuously capture imgs from the webcam and update subpages
    while True:
        _, frame = cap.read()                          #< Read a frame from the webcam
        app.imshow("frame", frame)                     #< Display the frame on the "frame" subpage

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #< Convert the frame to grayscale
        app.imshow("gray", gray)                       #< Display the grayscale frame on the "gray" subpage
