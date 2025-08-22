import os

import chromadb
from chromadb.config import Settings
import PyPDF2
from typing import List, Optional, Any
import hashlib
import logging
import shutil

class ChromaDBConnector:
    """
    Verwaltet die Verbindung zur lokalen ChromaDB VectorDB.
    """
    def __init__(self, path: str, embedding_model: str = None):
        self.client = chromadb.PersistentClient(path=path, settings= Settings(allow_reset=True))
        self.embedding_model = embedding_model

    def add_or_create_collection(self):
        collection = self.client.get_or_create_collection(name="docs")
        return collection

    def add_pdf_to_collection(
            self,
            pdf_path: str,
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            metadata: Optional[dict] = None
    ) -> List[str]:
        """
        Add a PDF document to a ChromaDB collection by extracting text and chunking it.

        Args:
            self: The ChromaDBConnector instance
            pdf_path: Path to the PDF file
            chunk_size: Maximum size of each text chunk (in characters)
            chunk_overlap: Number of characters to overlap between chunks
            metadata: Optional metadata to attach to all chunks from this PDF

        Returns:
            List of document IDs that were added to the collection
        """

        def extract_text_from_pdf(pdf_path: str) -> str:
            """Extract text from PDF file."""
            text = ""
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text + "\n"
            except Exception as e:
                raise Exception(f"Error reading PDF: {str(e)}")
            return text.strip()

        def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
            """Split text into overlapping chunks with safe progress and boundary-aware ends."""
            # Parameter validieren
            if chunk_size <= 0:
                raise ValueError("chunk_size must be > 0")
            if overlap < 0 or overlap >= chunk_size:
                raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")

            n = len(text)
            if n == 0:
                return []
            if n <= chunk_size:
                return [text.strip()]

            chunks: List[str] = []
            start = 0
            step = chunk_size - overlap  # garantiert Fortschritt

            while start < n:
                # vorläufiges Ende
                end = min(start + chunk_size, n)

                # Versuche, bis zu 200 Zeichen nach hinten eine hübsche Grenze zu finden
                if end < n:
                    win_start = max(start, end - 200)
                    sentence_end = max(
                        text.rfind('.', win_start, end),
                        text.rfind('!', win_start, end),
                        text.rfind('?', win_start, end),
                    )
                    if sentence_end > start:
                        end = sentence_end + 1
                    else:
                        word_end = text.rfind(' ', win_start, end)
                        if word_end > start:
                            end = word_end

                # Fortschritt erzwingen (mind. 1 Zeichen)
                if end <= start:
                    end = min(start + 1, n)

                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)

                if end >= n:
                    break  # letzter Chunk verarbeitet

                # Nächster Startpunkt: monotone Bewegung nach vorne
                next_start = start + step
                # Sicherheitsnetz: falls die Begrenzung sehr früh endete, trotzdem weitergehen
                next_start = max(next_start, end - overlap)
                if next_start <= start:
                    next_start = start + 1  # absolute Notbremse gegen Stagnation
                start = next_start

            return chunks

        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        logging.info(f"Extracted {len(pdf_text)} characters from {pdf_path}")

        if not pdf_text:
            raise ValueError("No text could be extracted from the PDF")

        # Split into chunks
        text_chunks = chunk_text(pdf_text, chunk_size, chunk_overlap)
        logging.info(f"Split into {len(text_chunks)} chunks from {pdf_path}")
        # Prepare documents for ChromaDB
        documents = []
        metadatas = []
        ids = []

        # Generate a unique identifier for this PDF
        logging.info(f"Generating unique ID for PDF: {pdf_path}")
        pdf_hash = hashlib.md5(pdf_path.encode()).hexdigest()[:8]
        logging.info(f"Generated PDF hash: {pdf_hash}")
        for i, chunk in enumerate(text_chunks):
            # Create unique ID for each chunk
            chunk_id = f"{pdf_hash}_chunk_{i:04d}"
            ids.append(chunk_id)
            documents.append(chunk)

            # Prepare metadata
            chunk_metadata = {
                "source": pdf_path,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "pdf_hash": pdf_hash,
                "chunk_size": len(chunk)
            }

            # Add custom metadata if provided
            if metadata:
                chunk_metadata.update(metadata)

            metadatas.append(chunk_metadata)

        # Add to ChromaDB collection
        try:
            logging.info("Adding chunks to ChromaDB collection")
            collection = self.client.get_or_create_collection(name="docs")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logging.info(f"Added {len(documents)} chunks to ChromaDB collection")
            return ids

        except Exception as e:
            raise Exception(f"Error adding documents to ChromaDB: {str(e)}")

    def delete_collection(self, path: str = "rag/chroma_db") -> bool:
        abs_path = os.path.abspath(path)
        try:
            if os.path.exists(abs_path):
                shutil.rmtree(abs_path)
                logging.info(f"Deleted ChromaDB folder at {abs_path}")
                return True
            else:
                logging.info(f"No ChromaDB folder found at {abs_path}")
                return False
        except Exception as e:
            logging.error(f"Error deleting ChromaDB folder at {abs_path}: {e}")
            raise

    def query_collection(
            self,
            query_text: str,
            n_results: int = 5,
    ) -> List[List[str]]:
        """
        Query a ChromaDB collection with text input and return relevant results as 2D array.

        Args:
            self: The ChromaDBConnector instance
            query_text: The text to search for
            n_results: Number of results to return (default: 5)


        Returns:
            List[List[str]]: 2D array where each inner list contains [document_id, document_text]
        """

        try:
            # Get a collection
            collection = self.client.get_collection(name="docs")

            # Prepare query parameters
            query_params = {
                "query_texts": [query_text],
                "n_results": n_results,
                "include": ["documents", "data"]  # Only include what we need for the 2D array
            }

            # Execute query
            results = collection.query(**query_params)
            logging.info(f"Query done")
            # Format results as 2D array [document_id, document_text]
            formatted_array = []

            if results.get('ids') and results.get('documents'):
                # ChromaDB returns nested lists, so we access the first (and usually only) query result
                ids = results['ids'][0] if results['ids'] else []
                documents = results['documents'][0] if results['documents'] else []
                logging.info(f"Got {len(ids)} results")
                # Ensure both lists have the same length
                min_length = min(len(ids), len(documents))

                for i in range(min_length):
                    doc_id = ids[i]
                    doc_text = documents[i]
                    formatted_array.append([doc_id, doc_text])

            return formatted_array

        except Exception as e:
            print(f"Error querying collection: {str(e)}")
            return []  # Return an empty array instead of raising exception
