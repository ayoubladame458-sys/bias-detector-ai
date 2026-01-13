"""
Document processing service for handling various file formats
"""
import PyPDF2
import docx
from pathlib import Path
from typing import List
import aiofiles
import uuid


class DocumentService:
    """Service for processing and extracting text from documents"""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text
        """
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file

        Args:
            file_path: Path to the DOCX file

        Returns:
            Extracted text
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    @staticmethod
    async def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from TXT file

        Args:
            file_path: Path to the TXT file

        Returns:
            Extracted text
        """
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                text = await file.read()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")

    @staticmethod
    async def extract_text(file_path: str, file_type: str) -> str:
        """
        Extract text from file based on its type

        Args:
            file_path: Path to the file
            file_type: Type of file (pdf, docx, txt)

        Returns:
            Extracted text
        """
        file_type = file_type.lower()

        if file_type == "pdf":
            return DocumentService.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return DocumentService.extract_text_from_docx(file_path)
        elif file_type == "txt":
            return await DocumentService.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)

                if break_point > chunk_size * 0.5:  # Only break if it's not too short
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    @staticmethod
    def generate_document_id() -> str:
        """
        Generate a unique document ID

        Returns:
            UUID string
        """
        return str(uuid.uuid4())


# Singleton instance
document_service = DocumentService()
