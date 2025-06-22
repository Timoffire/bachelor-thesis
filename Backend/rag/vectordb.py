import chromadb
import PyPDF2
from typing import List, Optional, Any
import hashlib

class ChromaDBConnector:
    """
    Verwaltet die Verbindung zur lokalen ChromaDB VectorDB.
    """
    def __init__(self, path: str, embedding_model: str = None):
        self.client = chromadb.PersistentClient(path=path)
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
            """Split text into overlapping chunks."""
            if len(text) <= chunk_size:
                return [text]

            chunks = []
            start = 0

            while start < len(text):
                end = start + chunk_size

                # If this isn't the last chunk, try to break at a sentence or word boundary
                if end < len(text):
                    # Look for sentence boundary (. ! ?)
                    sentence_end = max(
                        text.rfind('.', start, end),
                        text.rfind('!', start, end),
                        text.rfind('?', start, end)
                    )

                    if sentence_end > start:
                        end = sentence_end + 1
                    else:
                        # Fall back to word boundary
                        word_end = text.rfind(' ', start, end)
                        if word_end > start:
                            end = word_end

                chunk = text[start:end].strip()
                if chunk:  # Only add non-empty chunks
                    chunks.append(chunk)

                # Move start position with overlap
                start = end - overlap
                if start <= 0 or start >= len(text):
                    break

            return chunks

        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_path)

        if not pdf_text:
            raise ValueError("No text could be extracted from the PDF")

        # Split into chunks
        text_chunks = chunk_text(pdf_text, chunk_size, chunk_overlap)

        # Prepare documents for ChromaDB
        documents = []
        metadatas = []
        ids = []

        # Generate a unique identifier for this PDF
        pdf_hash = hashlib.md5(pdf_path.encode()).hexdigest()[:8]

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
            collection = self.client.get_or_create_collection(name="docs")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            print(f"Successfully added {len(text_chunks)} chunks from {pdf_path} to collection")
            return ids

        except Exception as e:
            raise Exception(f"Error adding documents to ChromaDB: {str(e)}")

    def delete_collection(self, collection_name = "docs"):
        self.client.delete_collection(name=collection_name)
        print("Collection deleted")

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

            # Format results as 2D array [document_id, document_text]
            formatted_array = []

            if results.get('ids') and results.get('documents'):
                # ChromaDB returns nested lists, so we access the first (and usually only) query result
                ids = results['ids'][0] if results['ids'] else []
                documents = results['documents'][0] if results['documents'] else []

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
