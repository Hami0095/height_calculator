from flask import Flask, request, jsonify
import os
import concurrent.futures
# Import the height calculation logic from calculator
from calculator import main as calculate_height

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create a thread pool executor for handling image processing
executor = concurrent.futures.ThreadPoolExecutor()


def process_image(file_path):
    """Processes the image and calculates height in a separate thread."""
    try:
        # Call the height calculation function and get the returned dictionary
        height_info = calculate_height(file_path)

        # Return the result as-is
        return {
            'status': 'success',
            'height_info': {
                'height_cm': height_info["height_cm"],
                'height_ft': height_info["height_ft"],
                'height_inch': height_info["height_inch"]
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@app.route('/upload', methods=['POST'])
def upload_file():
    print("The Function has been Called")

    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    # Save the file to the server
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    print(f'File saved: {file_path}')

    # Submit the image processing task to the executor
    future = executor.submit(process_image, file_path)

    # Wait for the result and return the response
    result = future.result()

    return jsonify(result), 200 if result['status'] == 'success' else 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
