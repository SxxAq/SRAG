"""
Document loading from various file types (PDF, TXT, Markdown, etc.).
"""

import os
from pathlib import Path
from typing import List, Union
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    PyMuPDFLoader,
    DirectoryLoader
)
from langchain_core.documents import Document
from srag.exceptions import DocumentLoadingException
from srag.logging_config import logger


class DocumentProcessor:
    """Load documents from various sources (PDFs, text files, directories)."""
    
    @staticmethod
    def load_text_files(
        directory_path: Union[str, Path],
        recursive: bool = True,
        encoding: str = "utf-8"
    ) -> List[Document]:
        """
        Load all text files from a directory.
        
        Args:
            directory_path: Path to directory containing text files
            recursive: Whether to search subdirectories
            encoding: File encoding to use
        
        Returns:
            List of LangChain Document objects
        
        Raises:
            DocumentLoadingException: If loading fails
        """
        try:
            logger.info(f"Loading text files from: {directory_path}")
            
            glob_pattern = "**/*.txt" if recursive else "*.txt"
            loader = DirectoryLoader(
                str(directory_path),
                glob=[glob_pattern],
                loader_cls=TextLoader,
                loader_kwargs={"encoding": encoding},
                show_progress=True
            )
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} text files")
            return documents
        except Exception as e:
            logger.error(f"Error loading text files: {e}")
            raise DocumentLoadingException(f"Failed to load text files: {e}") from e
    
    @staticmethod
    def load_pdfs(
        directory_path: Union[str, Path],
        recursive: bool = True
    ) -> List[Document]:
        """
        Load all PDF files from a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            recursive: Whether to search subdirectories
        
        Returns:
            List of LangChain Document objects with metadata
        
        Raises:
            DocumentLoadingException: If loading fails
        """
        try:
            logger.info(f"Loading PDFs from: {directory_path}")
            
            glob_pattern = "**/*.pdf" if recursive else "*.pdf"
            pdf_dir = Path(directory_path)
            pdf_files = list(pdf_dir.glob(glob_pattern))
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            all_docs = []
            for pdf_path in pdf_files:
                try:
                    logger.info(f"Processing: {pdf_path.name}")
                    loader = PyMuPDFLoader(str(pdf_path))
                    documents = loader.load()
                    
                    # Add source metadata
                    for doc in documents:
                        doc.metadata['source_file'] = pdf_path.name
                        doc.metadata['file_type'] = 'pdf'
                    
                    all_docs.extend(documents)
                    logger.info(f"Loaded {len(documents)} pages from {pdf_path.name}")
                except Exception as e:
                    logger.warning(f"Error processing {pdf_path.name}: {e}")
                    continue
            
            logger.info(f"Total pages loaded from PDFs: {len(all_docs)}")
            return all_docs
        except Exception as e:
            logger.error(f"Error loading PDFs: {e}")
            raise DocumentLoadingException(f"Failed to load PDFs: {e}") from e
    
    @staticmethod
    def load_mixed_documents(
        pdf_directory: Union[str, Path] = None,
        text_directory: Union[str, Path] = None,
        markdown_directory: Union[str, Path] = None
    ) -> List[Document]:
        """
        Load documents from multiple directories.
        
        Args:
            pdf_directory: Path to PDF directory
            text_directory: Path to text files directory
            markdown_directory: Path to markdown files directory
        
        Returns:
            Combined list of all loaded documents
        
        Raises:
            DocumentLoadingException: If any loading fails
        """
        all_documents = []
        
        if pdf_directory:
            try:
                pdfs = DocumentProcessor.load_pdfs(pdf_directory)
                all_documents.extend(pdfs)
            except DocumentLoadingException as e:
                logger.warning(f"Skipping PDFs: {e}")
        
        if text_directory:
            try:
                texts = DocumentProcessor.load_text_files(text_directory)
                all_documents.extend(texts)
            except DocumentLoadingException as e:
                logger.warning(f"Skipping text files: {e}")
        
        if markdown_directory:
            try:
                markdowns = DocumentProcessor.load_text_files(markdown_directory)
                all_documents.extend(markdowns)
            except DocumentLoadingException as e:
                logger.warning(f"Skipping markdown files: {e}")
        
        logger.info(f"Total documents loaded: {len(all_documents)}")
        return all_documents
