# README for Web Viewer

## Introduction
The Flask Subpage App is a Python application that allows you to create subpages with live video streams from a webcam. It uses the Flask framework to handle web requests and displays video frames in real-time.

## Requirements
- Python 3.x
- OpenCV (cv2) library
- Flask library

## Installation
1. Clone the repository or download the code files.
2. Install the required dependencies by running the following command:
   ```
   pip install opencv-python flask
   ```

## Usage
1. Import the necessary modules:
   ```python
   from flask import Flask, Response
   import threading
   import cv2
   import os
   import base64
   ```

2. Create an instance of the `VideoStream` class:
   ```python
   app = VideoStream()
   ```

3. Start the Flask web server on a specified port (default is 80):
   ```python
   app.run()
   ```

4. Continuously capture frames from the webcam and update subpages:
   ```python
   cap = cv2.VideoCapture(0)
   
   while True:
       _, frame = cap.read()
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       app.imshow("frame", frame)
       app.imshow("gray", gray)
   ```

5. Access the subpages:
   - The home page lists all the available subpages. Visit the root URL (e.g., `http://localhost:80/`) to see the home page.
   - Each subpage displays a live video stream. Append the subpage name to the root URL (e.g., `http://localhost:80/<name>`) to access a specific subpage.

## Customization
You can customize the following aspects of the Flask Subpage App:

- **Templates**: The app uses HTML templates to render the home page and subpages. By default, it looks for the templates in the `templates` folder relative to the script's location. You can specify custom template paths when creating a `VideoStream` instance:
   ```python
   app = VideoStream(homePageTemplate="path/to/home.html", subpageTemplate="path/to/subpage.html")
   ```

- **Port**: The default port for the Flask web server is 80. If you want to use a different port, specify it when creating a `VideoStream` instance:
   ```python
   app = VideoStream(port=5000)
   ```


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). Feel free to modify and use it according to your needs.

## Acknowledgments

-

 This application was inspired by the Flask video streaming tutorial from the [Official Flask Documentation](https://flask.palletsprojects.com/)
- OpenCV - Open Source Computer Vision Library: [https://opencv.org/](https://opencv.org/)
- Flask - A micro web framework written in Python: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)