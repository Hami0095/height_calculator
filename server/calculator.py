import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def load_image(image_path):
    """
    Load an image from a given path and convert it to grayscale.
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray


def segment_image(gray_image):
    """
    Apply edge detection or thresholding to segment the person from the image.
    """
    # Using Canny edge detection to highlight the body contour
    edges = cv2.Canny(gray_image, threshold1=100, threshold2=200)

    # Optionally, apply dilation to enhance the edges
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)

    return edges_dilated


def detect_landmarks(image):
    """
    Detect body landmarks using MediaPipe.
    Returns the head and foot coordinates.
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Get head and foot coordinates
        head = landmarks[0]  # Nose
        left_foot = landmarks[31]  # Left foot
        right_foot = landmarks[32]  # Right foot

        # Convert normalized coordinates to image coordinates
        head_x, head_y = int(
            head.x * image.shape[1]), int(head.y * image.shape[0])
        foot_x_left, foot_y_left = int(
            left_foot.x * image.shape[1]), int(left_foot.y * image.shape[0])
        foot_x_right, foot_y_right = int(
            right_foot.x * image.shape[1]), int(right_foot.y * image.shape[0])

        # Average the foot coordinates to get a single foot height estimate
        foot_y = (foot_y_left + foot_y_right) // 2

        return (head_x, head_y), (foot_x_left, foot_y)
    else:
        raise ValueError("No person detected in the image.")


def calculate_height(image, head, foot, pixel_height_in_cm=1):
    """
    Calculate the height of the person in the image using head and foot coordinates.
    Adjust for the distance of the head from the top and the foot from the bottom.
    """
    # Calculate pixel height (distance between head and foot in pixels)
    pixel_height = foot[1] - head[1]

    # If head is far from the top and foot far from the bottom, adjust for distance
    top_margin = head[1]  # Distance from top of image
    bottom_margin = image.shape[0] - foot[1]  # Distance from bottom of image

    # Calculate the actual height (adjust for margins)
    adjusted_height_in_pixels = pixel_height + top_margin + bottom_margin

    # Convert to height in cm
    estimated_height = adjusted_height_in_pixels * pixel_height_in_cm

    # Convert cm to inches
    height_in_inches = estimated_height * 0.393701

    # Convert inches to feet and inches
    feet = int(height_in_inches // 12)
    inches = height_in_inches % 12

    return estimated_height, feet, inches


def draw_keypoints(image, head, foot):
    """
    Draw circles at the head and foot positions for visualization.
    """
    # Draw circles on the detected head and feet
    cv2.circle(image, head, 5, (0, 255, 0), -1)  # Green for head
    cv2.circle(image, foot, 5, (255, 0, 0), -1)  # Blue for feet

    # Display the image with keypoints
    cv2.imshow("Key Points", image)
    cv2.waitKey(0)


def main(image_path):
    """
    Main function to estimate the height of a person in the image.
    """
    # Load image and convert to grayscale
    image, gray_image = load_image(image_path)

    # Segment the image (optional: used for visualizing the human body)
    segmented_image = segment_image(gray_image)

    # Detect landmarks (head and foot)
    head, foot = detect_landmarks(image)

    # Calculate height based on detected landmarks
    estimated_height_cm, feet, inches = calculate_height(
        image, head, foot, pixel_height_in_cm=0.26)

    # Draw keypoints for visualization
    # draw_keypoints(image, head, foot)

    # Print the estimated height
    print(f"Estimated Height of Person: {
          estimated_height_cm:.2f} cm ({feet} ft {inches:.1f} inches)"
          )


if __name__ == "__main__":
    # Replace 'person_image.jpg' with your actual image path
    main('c:/development/Computer Vision/height_calculator/height_calculator/server/image.png')
