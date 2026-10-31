"""
File Type & Format Detector.
Inspects file magic bytes (signatures) and content heuristics to accurately determine true MIME/format,
preventing extension spoofing vulnerabilities.
"""
from pathlib import Path
from typing import Tuple
import json
import csv
from app.core.exceptions import FileDetectionError
from app.config.logger import get_logger

logger = get_logger(__name__)


class FileTypeDetector:
    """Sniffs file content headers and magic bytes to classify datasets."""

    MAGIC_SIGNATURES = {
        b"PAR1": ("application/x-parquet", "parquet"),
        b"%PDF": ("application/pdf", "pdf"),
        b"\x1f\x8b": ("application/gzip", "gzip"),
        b"BZh": ("application/x-bzip2", "bzip2"),
    }

    @classmethod
    def detect(cls, file_path: Path) -> Tuple[str, str]:
        """
        Determines the MIME type and canonical format identifier of a file.
        Returns: (mime_type, format_code) e.g. ("text/csv", "csv")
        """
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise FileDetectionError(f"File is empty or does not exist: {file_path}")

        file_size = file_path.stat().st_size

        # Read first 512 bytes for header magic numbers
        with open(file_path, "rb") as f:
            header = f.read(512)

        # 1. Check fixed magic byte signatures
        for magic, (mime, fmt) in cls.MAGIC_SIGNATURES.items():
            if header.startswith(magic):
                return mime, fmt

        # 2. Check for Zip format (ZIP or XLSX)
        if header.startswith(b"PK\x03\x04"):
            # Check if this is an XLSX (Office Open XML spreadsheet)
            if file_path.suffix.lower() in [".xlsx", ".xlsm"]:
                return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
            return "application/zip", "zip"

        # 3. Check for Tar format (magic 'ustar' at offset 257)
        if len(header) >= 262 and header[257:262] == b"ustar":
            return "application/x-tar", "tar"

        # 4. Text-based detection: JSON vs CSV / TSV
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_lines = [f.readline() for _ in range(5)]
                sample = "".join(first_lines).strip()

            if not sample:
                raise FileDetectionError(f"Cannot decode text content from: {file_path}")

            # Check JSON or JSONL
            if sample.startswith("{") or sample.startswith("["):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        json.load(f)
                    return "application/json", "json"
                except json.JSONDecodeError:
                    # Check if valid JSON Lines (first line is valid JSON object)
                    try:
                        json.loads(first_lines[0].strip())
                        return "application/x-ndjson", "jsonl"
                    except Exception:
                        pass

            # Check CSV / TSV using csv Sniffer
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
                fmt = "tsv" if dialect.delimiter == "\t" else "csv"
                return "text/csv", fmt
            except Exception:
                pass

        except Exception as e:
            logger.debug(f"Text sniffing failed for {file_path}: {e}")

        # 5. Extension Fallback as last resort
        ext = file_path.suffix.lower().lstrip(".")
        if ext in ["csv", "tsv", "json", "jsonl", "parquet", "xlsx", "xls", "pdf", "zip", "tar", "gz"]:
            return f"application/{ext}", ext

        raise FileDetectionError(f"Unsupported or unrecognized file type for: {file_path.name}")
