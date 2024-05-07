# License Plate Recognition System

A simple License Plate Recognition (LPR) system implemented in Python using Flask, OpenCV, and TensorFlow.

## Description

This project is a real-time license plate recognition system that detects license plates from a video feed, recognizes the characters using Optical Character Recognition (OCR), validates the license plate number format, and stores the results in a MySQL database.

## Features

- Real-time video feed processing
- Object detection using TensorFlow and OpenCV
- Optical Character Recognition (OCR) for license plate number extraction
- Validation of license plate number format
- Storage of detected license plate numbers in a database
- Filtering and searching results by date and time

## Installation

1. Clone the repository:


2. Navigate to the project directory
  
3. Install dependencies: pip install -r requirements.txt

  
4. Set up MySQL database:

   - Create a MySQL database named `npd`.
   - Set the database URI in `app.py` to match your MySQL database configuration.

5. Run the application: python app.py

6. Access the application in your web browser at `http://localhost:5000`.

## Usage

1. Start the application.
2. Upload a video file or use the provided sample video.
3. The application will process the video feed, detect license plates, and store the results in the database.
4. View the detected license plate numbers and search/filter results as needed.

## Contributors

- [Your Name](https://github.com/your_username)
- [Another Contributor](https://github.com/another_username)








