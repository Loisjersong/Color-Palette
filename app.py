from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = request.files['image']
        filename = image.filename
        filepath = os.path.join('static/uploads', filename)
        image.save(filepath)

        # Convert image to RGB format
        img = cv2.imread(filepath)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Generate color palette
        palette = generate_color_palette(img)

        return jsonify(palette)

    return render_template('index.html')

@app.route('/brightness')
def brightness():
    color = request.args.get('color').split(',')
    color = np.array(color, dtype=np.uint8)
    brightness_palette = generate_brightness_palette(color)
    return jsonify(brightness_palette)




def generate_color_palette(image):
    # Resize image
    height, width, channels = image.shape
    resized_image = cv2.resize(image, (100, 100))

    # Flatten image to a 1D array
    image_array = resized_image.reshape(-1, 3)

    # Convert to float32 data type
    image_array = np.float32(image_array)

    # Cluster pixels using KMeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    K = 10
    ret, labels, centers = cv2.kmeans(image_array, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert centers to RGB format
    palette = [(int(c[0]), int(c[1]), int(c[2])) for c in centers]

    return palette

def generate_brightness_palette(color):
    # Create a single pixel image with the given color
    color_image = np.zeros((1, 1, 3), dtype=np.uint8)
    color_image[0, 0] = color

    # Convert the single pixel image to HSV
    hsv = cv2.cvtColor(color_image, cv2.COLOR_RGB2HSV)[0][0]

    brightness_palette = []
    initial_value = hsv[2]  # Initial value of Value component
    for i in range(10):
        brightness_scale = (i + 1) / 10.0  # Scale the brightness from 1/10 to 1
        hsv[2] = min(initial_value * brightness_scale, 255)  # Adjust brightness proportionally
        hsv_color = np.array(hsv, dtype=np.uint8).reshape((1, 1, 3))
        rgb_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2RGB)[0][0]
        brightness_palette.append(rgb_color.tolist())  # Convert NumPy array to list

    return brightness_palette






if __name__ == '__main__':
    app.run(debug=True)