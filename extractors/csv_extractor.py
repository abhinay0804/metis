"""
CSV content extractor.
Reads CSV into rows with header inference.
"""

from typing import Dict, Any, List
import csv


class CSVExtractor:
    """Extract rows and headers from CSV files."""

    def extract(self, file_path: str) -> Dict[str, Any]:
        content: Dict[str, Any] = {
            "headers": [],
            "rows": []
        }
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                sniffer = csv.Sniffer()
                sample = f.read(2048)
                f.seek(0)
                dialect = sniffer.sniff(sample) if sample else csv.excel
                reader = csv.reader(f, dialect)
                rows: List[List[str]] = list(reader)
            if not rows:
                return content
            # header detection
            content["headers"] = rows[0]
            content["rows"] = rows[1:] if len(rows) > 1 else []
            return content
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
            if not rows:
                return content
            content["headers"] = rows[0]
            content["rows"] = rows[1:] if len(rows) > 1 else []
            return content
        except Exception as e:
            raise Exception(f"Error extracting CSV content: {str(e)}")


