# Image-Processing-Service

a service that allows users to upload and process images

## Features

- User authentication with JWT
- User signup and login
- Image upload and processing (to be implemented)

## Installation

1. Clone the repository:

    ```sh
    git clone <repository-url>
    cd Image-Processing-Service
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file and add your JWT secret and algorithm:

    ```
    secret=your_jwt_secret
    algorithm=HS256
    ```

## Usage

1. Start the FastAPI server:

    ```sh
    uvicorn main:app --reload
    ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

## API Endpoints

- `GET /`: Returns "hello world".
- `POST /signup`: Allows a new user to sign up.
- `POST /login`: Allows an existing user to log in.

## Project Structure
