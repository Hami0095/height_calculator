import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def load_image(image_path, target_height=387):
    """Load an image from a given path and resize it to a target height while maintaining aspect ratio."""
    image = cv2.imread(image_path)

    # Check if the image was loaded properly
    if image is None:
        raise ValueError(f"Image not found at {image_path}")

    print(f"Original Image Size: {image.shape}")  # Debug statement

    # Calculate the new width while keeping the aspect ratio
    height, width = image.shape[:2]
    aspect_ratio = width / height
    new_width = int(target_height * aspect_ratio)

    # Resize the image to the new dimensions
    image_resized = cv2.resize(image, (new_width, target_height))

    return image_resized


def detect_landmarks(image):
    """Detect body landmarks using MediaPipe and return head and foot coordinates."""
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
        print("MediaPipe results:", results)
        raise ValueError("No person detected in the image.")


def calculate_height(image, head, foot, pixel_height_in_cm=0.6034751773049):
    """
    Calculate the height of the person in the image using head and foot coordinates.
    Adjust for how far the person is from the camera by adding distances.
    """
    image_height = image.shape[0]  # Total height of the image in pixels

    # Pixel distance between the head and foot
    pixel_height = foot[1] - head[1]

    # Convert pixel height to centimeters using the given conversion factor
    estimated_height = pixel_height * pixel_height_in_cm

    # Convert height to feet and inches
    height_in_inches = estimated_height * 0.393701
    feet = int(height_in_inches // 12)
    inches = height_in_inches % 12

    return estimated_height, feet, inches


def main(image_path):
    """Main function to estimate the height of a person in the image."""
    # Load the image and resize it with aspect ratio maintained
    image = load_image(image_path)

    # Show the loaded image for debugging
    cv2.imshow('Loaded Image', image)
    cv2.waitKey(5000)  # Show for 5 seconds
    cv2.destroyAllWindows()

    # Detect landmarks (head and foot)
    head, foot = detect_landmarks(image)

    # Calculate height based on detected landmarks
    estimated_height_cm, feet, inches = calculate_height(image, head, foot)

    # Print the estimated height
    print(f"Estimated Height: {
          estimated_height_cm:.2f} cm ({feet} ft {inches:.1f} inches)")

    # Return the calculated height
    return {
        "height_cm": estimated_height_cm,
        "height_ft": feet,
        "height_inch": inches
    }


if __name__ == "__main__":
    # Example usage; replace with actual image path in production
    main('c:/development/Computer Vision/height_calculator/height_calculator/server/img5.jpg')
