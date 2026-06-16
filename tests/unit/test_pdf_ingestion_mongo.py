"""
Unit tests for the PDF Ingestion Module of Project Tarantula.

Validates extraction behavior, tracking integrity,
and error boundaries.
"""

from unittest.mock import MagicMock, patch

import pytest

# Broken into multiple lines to pass strict Flake8 limits
from src.ingestion.pdf_ingestion import (
    extract_pdf_text,
    process_pdf_pipeline,
)


@pytest.fixture
def mock_pdf_document():
    """Fixtures a mocked PyMuPDF (fitz) Document with sample pages."""
    mock_doc = MagicMock()

    # Simulate a 2-page PDF document
    page1 = MagicMock()
    page1.get_text.return_value = "Attention is all you need."

    page2 = MagicMock()
    page2.get_text.return_value = "Multi-head text extraction works."

    mock_doc.__iter__.return_value = [page1, page2]
    mock_doc.__enter__.return_value = mock_doc
    mock_doc.__exit__.return_value = None
    return mock_doc


class TestPDFTextExtraction:
    """Tests the text isolation and extraction layer using PyMuPDF."""

    @patch("fitz.open")
    def test_extract_pdf_text_success(self, mock_fitz_open, mock_pdf_document):
        """Verifies text is successfully extracted page-by-page."""
        mock_fitz_open.return_value = mock_pdf_document

        result = extract_pdf_text("fake_path.pdf")

        assert "Attention is all you need." in result
        assert "Multi-head text extraction works." in result

        # Implicit string joining inside parentheses to satisfy Flake8
        assert result == (
            "Attention is all you need.\n" "Multi-head text extraction works."
        )
        mock_fitz_open.assert_called_once_with("fake_path.pdf")

    @patch("fitz.open")
    def test_extract_pdf_text_exception_handling(self, mock_fitz_open):
        """Ensures exceptions during file opens return empty strings."""
        mock_fitz_open.side_effect = RuntimeError("OS read failure")

        result = extract_pdf_text("corrupted.pdf")

        assert result == ""


class TestPDFPipelineOrchestration:
    """Tests transactional loops between Mongo and Chroma states."""

    @patch("src.ingestion.pdf_ingestion.register_ingestion")
    @patch("src.ingestion.pdf_ingestion.extract_pdf_text")
    @patch("src.ingestion.pdf_ingestion.mark_as_completed")
    def test_pipeline_skips_if_already_ingested(
        self, mock_mark, mock_extract, mock_register
    ):
        """Ensures pipeline early-exits when content hash exists."""
        mock_register.return_value = None

        process_pdf_pipeline("duplicate_file.pdf")

        mock_extract.assert_not_called()
        mock_mark.assert_not_called()

    @patch("src.ingestion.pdf_ingestion.register_ingestion")
    @patch("src.ingestion.pdf_ingestion.extract_pdf_text")
    @patch("src.ingestion.pdf_ingestion.mark_as_completed")
    def test_pipeline_aborts_on_empty_extracted_text(
        self, mock_mark, mock_extract, mock_register
    ):
        """Guards against pushing blank PDFs to the vector store."""
        mock_register.return_value = "mock_object_id_123"
        mock_extract.return_value = "   \n   "  # Empty spacing

        process_pdf_pipeline("empty.pdf")

        mock_mark.assert_not_called()

    @patch("src.ingestion.pdf_ingestion.register_ingestion")
    @patch("src.ingestion.pdf_ingestion.extract_pdf_text")
    @patch("src.ingestion.pdf_ingestion.mark_as_completed")
    def test_pipeline_closes_loop_on_success(
        self, mock_mark, mock_extract, mock_register
    ):
        """Verifies complete transactional path under healthy conditions."""
        mock_register.return_value = "mock_object_id_123"
        mock_extract.return_value = "Valid text payload for embeddings."

        process_pdf_pipeline("healthy.pdf")

        mock_register.assert_called_once_with("healthy.pdf")
        mock_extract.assert_called_once_with("healthy.pdf")
        mock_mark.assert_called_once_with("mock_object_id_123")
