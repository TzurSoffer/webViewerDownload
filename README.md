# Web Video Viewer

This is a simple Flask application for viewing video feeds from multiple subpages and downloading them. It is based on my other Project [WebVideoViewer](https://github.com/TzurSoffer/webVideoViewer/) Each subpage represents a different video stream. The application captures frames from a webcam and updates the subpages with the latest frames.

## Usage
1. update the submodule by running `git submodule update --init`.

2. go to the submodule by running `cd webVideoViewer` and then running `git switch main`.

3. Install the necessary dependencies by running `pip install -r requirements.txt`.

4. Run the `main.py` script.

5. Access the home page by navigating to `http://localhost:80` or the specified port in your web browser. The home page lists all available subpages.

6. Click on a subpage to view the corresponding video feed.

## Customization

- To customize the appearance of the video feed page, modify the templates under the `templates` folder.

## Dependencies

- Flask
- OpenCV
- av
