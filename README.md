# Web Video Viewer

This is a simple Flask application for viewing video feeds from multiple subpages and downloading them. It is based on my other Project [WebVideoViewer](https://github.com/TzurSoffer/webVideoViewer/) Each subpage represents a different video stream. The application captures frames from a webcam and updates the subpages with the latest frames.

## Usage
1. update the submoduel by running `git submodule update --init`.

2. Install the necessary dependencies by running `pip install -r requirements.txt`.

3. Run the `main.py` script.

4. Access the home page by navigating to `http://localhost:80` or the specified port in your web browser. The home page lists all available subpages.

5. Click on a subpage to view the corresponding video feed.

## Customization

- To customize the appearance of the video feed page, modify the templates under the `templates` folder.

## Dependencies

- Flask
- OpenCV
- av
