import base64

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            # Read the image file in binary mode
            image_data = image_file.read()
            # Encode the binary data into base64
            base64_encoded = base64.b64encode(image_data).decode("utf-8")
            return base64_encoded
    except FileNotFoundError:
        print(f"Error: File '{image_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
image_path = "WhatsApp Image 2023-12-08 at 13.33.48.jpeg"  # Replace with the actual path to your image file
base64_encoded_image = encode_image_to_base64(image_path)

if base64_encoded_image:
    print("Base64 Encoded Image:")
    print(base64_encoded_image)
