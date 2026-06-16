<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard Logo" width="400">
  <br>
  <br>
</p>

# Mastercard ISO8583-1993 Parser (Python)

A Python parser developed for reading and interpreting messages in the **ISO8583-1993** standard, with a focus on **Mastercard** files.

## About the Project

This project aims to parse ISO8583 messages, converting raw data (typically from files or streams) into understandable and manipulable structures in Python.
It was designed to facilitate analyses, reconciliations, and integrations with financial systems.

## Features

- Reading of ISO8583 messages (Mastercard)
- Interpretation of:
  - MTI (Message Type Indicator)
  - Bitmap (primary and secondary)
  - Data Elements (variable and fixed fields)
- Support for the **ISO8583-1993** standard
- Ready structure for expanding new fields
- Conversion to Python objects (dict / classes)

## How It Works

The parser performs the following steps:
1. Identifies the **MTI**
2. Reads the **Bitmap** (to know which fields are present)
3. Interprets each **Data Element** according to:
   - Type (fixed or variable)
   - Size
   - Format

## Technologies Used

- Python 3.x
- Typing with `typing`
- String manipulation and binary parsing
- Starkbank library for final parsing of elements
- (Optional) Integration with database (PostgreSQL)

## License

This project is under the [MIT license](LICENSE).

## Author

Developed by **Heitor Dairel**