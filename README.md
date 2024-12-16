# Image Processing Service

## Overview

This project is an Image Processing Service that allows users to upload, transform, and retrieve images. The service supports various image transformations such as resizing, cropping, rotating, watermarking, flipping, mirroring, compressing, changing format, and applying filters.

## Features

- **User Authentication**
  - Sign-Up: Allow users to create an account.
  - Log-In: Allow users to log into their account.
  - JWT Authentication: Secure endpoints using JWTs for authenticated access.

- **Image Management**
  - Upload Image: Allow users to upload images.
  - Transform Image: Allow users to perform various transformations (resize, crop, rotate, watermark, etc.).
  - Retrieve Image: Allow users to retrieve a saved image in different formats.
  - List Images: List all uploaded images by the user with metadata.

- **Image Transformation**
  - Resize
  - Crop
  - Rotate
  - Watermark
  - Flip
  - Mirror
  - Compress
  - Change format (JPEG, PNG, etc.)
  - Apply filters (grayscale, sepia, etc.)

## Endpoints

### Authentication Endpoints

- **Register a new user**
  - `POST /register`

  ```json
  {
    "username": "user1",
    "password": "password123"
  }
  ```

  Response: User object with a JWT.

- **Log in an existing user**
  - `POST /login`
  
  ```json
  {
    "username": "user1",
    "password": "password123"
  }
  ```

  Response: User object with a JWT.

### Image Management Endpoints

- **Upload an image**
  - `POST /images`
  - Request Body: Multipart form-data with image file
  - Response: Uploaded image details (URL, metadata).

- **Apply transformations to an image**
  - `POST /images/:id/transform`

  ```json
  {
    "transformations": {
      "resize": {
        "width": "number",
        "height": "number"
      },
      "crop": {
        "width": "number",
        "height": "number",
        "x": "number",
        "y": "number"
      },
      "rotate": "number",
      "format": "string",
      "filters": {
        "grayscale": "boolean",
        "sepia": "boolean"
      }
    }
  }
  ```

  Response: Transformed image details (URL, metadata).

- **Retrieve an image**
  - `GET /images/:id`
  - Response: The actual image.

- **Get a paginated list of images**
  - `GET /images?page=1&limit=10`
  - Response: List of images with metadata.

## Setup and Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/image-processing-service.git
   cd image-processing-service
   ```

2. **Create a virtual environment and activate it**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS CLI**

   ```bash
   aws configure
   ```

   Follow the prompts to set up your AWS credentials and region.

5. **Set up environment variables**

   Create a `.env` file in the root directory and add the following variables:

   ```properties
   secret = YOUR_SECRET_KEY
   algorithm = HS256
   BUCKET_NAME = YOUR_BUCKET_NAME
   REGION = YOUR_REGION
   ```

6. **Run the application**

   ```bash
   uvicorn main:app --reload
   ```

7. **Access the API documentation**
   Open your browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation.

## Technologies Used

- **FastAPI**: For building the API.
- **PIL (Pillow)**: For image processing.
- **JWT**: For authentication.
- **SQLite**: For database (can be replaced with any other database).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.