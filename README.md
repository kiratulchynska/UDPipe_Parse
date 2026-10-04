# UDPipe_Parse

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MPL%202.0-green)](https://mozilla.org/MPL/2.0/)

## Description

**UDPipe_Parse** is a Python-based project designed to process and analyze subtitle files using UDPipe. It provides functionality for parsing subtitles, handling diacritics, formatting parsed data into a parallel treebank structure, and extracting linguistic features from CoNLL-U files. The project supports multilingual subtitles and leverages UDPipe models for linguistic analysis and dependency parsing.

---

## Features

- Parse subtitle files into CoNLL-U format using UDPipe.
- Normalize and separate diacritics for specific languages.
- Format parsed subtitles into a parallel treebank structure.
- Extract linguistic features (e.g., dependency relations) from CoNLL-U files.
- Support multiple languages with UDPipe models.

---

## Prerequisites

- **Python**: 3.8 or higher.
- **Dependencies**: Install from `requirements.txt`.
- **UDPipe**: Ensure UDPipe models are available and accessible via API or locally.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/UDPipe_Parse.git
   ```

2. Navigate to the project directory:
    ```bash
    cd UDPipe_Parse
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## How to Run
1. Parse Subtitles
    Run the `main.py` script to parse subtitles, format them, and extract data:

2. Customize Dependency Relations
    Edit the `deprels_to_extract.txt` file to specify the dependency relations you want to extract.

---

## Output

* **Parsed Files:** Saved in the `TEMP_DIR` and `OUTPUT_DIR` directories.

* **Formatted Treebank**: Parallel treebank structure generated from parsed subtitles.

---

## Additional Tools

* **Data Extraction**: `data_extraction.py`
    Extract linguistic features from CoNLL-U files:


* **UDPipe Wrapper**: `udpipe_wrapper.py`
    Interact with the UDPipe API for parsing and processing.

---

## License

This project is licensed under the Mozilla Public License 2.0.

---

## Acknowledgments

* UDPipe: https://github.com/ufal/udpipe
* Universal Dependencies: https://universaldependencies.org/
