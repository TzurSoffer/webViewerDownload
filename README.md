# Web Video Viewer

This is a simple Flask application for viewing and downloading video feeds from multiple streams. It is based off my other Project [WebVideoViewer](https://github.com/TzurSoffer/webVideoViewer/) Each subpage represents a different video stream.

## Usage

1. Install the necessary dependencies by running `pip install -r requirements.txt`.

2. Run the `main.py` script.

3. Access the home page by navigating to `http://localhost:80` or the specified port in your web browser. The home page lists all available subpages.

4. Click on a subpage to view the corresponding video feed.

## How It Works

The Web Video Viewer and Downloader application is built on the [WebViewer](https://github.com/TzurSoffer/webVideoViewer/) framework, providing users with a seamless video viewing and downloading experience. Here's how it works:

1. **Server Setup**: The application is built using the Flask web framework in Python. The server-side code runs on the server machine, which hosts the video source and handles client requests.

2. **Client Interaction**: Users access the application through a web browser on their device. The client-side code, written in HTML and CSS renders the user interface and sends requests to the server for video content.

3. **Video Download**: The application allows users to download videos from previous hours for offline viewing. The client can request specific video streams from the server, and the server responds by providing the requested video streams for download.

## Dependencies

- Flask
- OpenCV
- av