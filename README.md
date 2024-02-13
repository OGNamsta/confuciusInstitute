# Confucius Institute Data Processor (Work in Progress)

This Python script processes label keys, fetches corresponding country data from an API endpoint, and caches the data for future use.

## Requirements
- Python 3.7 or higher
- Required Python libraries: asyncio, httpx

## Usage
Run the script by executing the following command:
`python labelkey_data_processor.py`
The script will process label keys, fetch country data, and cache the results for future use. It logs information to the app.log file.

## Description
- The script processes a set of label keys and fetches corresponding country data asynchronously.
- It logs HTTP requests and responses for debugging and monitoring purposes.
- Label keys and country data are cached for efficient retrieval in subsequent runs.
- Error handling is implemented to handle potential issues during data retrieval and caching.
- The script then uses the stored label keys to traverse another API endpoint to fetch additional data which is country specific.

## Acknowledgment
This script is currently under development and may contain errors or incomplete functionality. Further testing and refinement are needed to ensure its reliability and accuracy.

## License
This project is licensed under the MIT License - see the LICENSE file for details.