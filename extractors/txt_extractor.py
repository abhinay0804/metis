"""
TXT content extractor.
Reads plain text files and returns content as a single string and by lines.
"""

from typing import Dict, Any


class TXTExtractor:
    """Extract text from .txt files."""

    def extract(self, file_path: str) -> Dict[str, Any]:
        content: Dict[str, Any] = {
            "text": "",
            "lines": []
        }
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()

            content["text"] = text
            content["lines"] = [line.rstrip('\n') for line in text.splitlines()]
            return content
        except Exception as e:
            raise Exception(f"Error extracting TXT content: {str(e)}")


