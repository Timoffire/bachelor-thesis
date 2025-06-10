import chromadb
import PyPDF2
from typing import List, Optional
import uuid
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
            collection: chromadb.Collection,
            pdf_path: str,
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            metadata: Optional[dict] = None
    ) -> List[str]:
        """
        Add a PDF document to a ChromaDB collection by extracting text and chunking it.

        Args:
            collection: ChromaDB collection object
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
            collection: chromadb.Collection,
            query_text: str,
            n_results: int = 5,
            include_distances: bool = True,
            metadata_filter: Optional[dict] = None,
            document_filter: Optional[List[str]] = None
    ) -> dict:
        """
        Query a ChromaDB collection with text input and return relevant results.

        Args:
            collection: ChromaDB collection object to search
            query_text: The text to search for
            n_results: Number of results to return (default: 5)
            include_distances: Whether to include similarity distances in results
            metadata_filter: Optional metadata filter (e.g., {"source": "document.pdf"})
            document_filter: Optional list of specific document IDs to search within

        Returns:
            Dictionary containing query results with documents, metadata, distances, and IDs
        """

        try:
            # Prepare query parameters
            query_params = {
                "query_texts": [query_text],
                "n_results": n_results
            }

            # Add optional filters
            if metadata_filter:
                query_params["where"] = metadata_filter

            if document_filter:
                query_params["where_document"] = {"$contains": document_filter}

            # Set what to include in results
            include_list = ["documents", "metadatas", "ids"]
            if include_distances:
                include_list.append("distances")
            query_params["include"] = include_list

            # Execute query
            results = collection.query(**query_params)

            # Format results for better usability
            formatted_results = {
                "query": query_text,
                "total_results": len(results["documents"][0]) if results["documents"] else 0,
                "results": []
            }

            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    result_item = {
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                    }

                    if include_distances and "distances" in results:
                        result_item["distance"] = results["distances"][0][i]
                        result_item["similarity_score"] = 1 - results["distances"][0][
                            i]  # Convert distance to similarity

                    formatted_results["results"].append(result_item)

            return formatted_results

        except Exception as e:
            raise Exception(f"Error querying collection: {str(e)}")

    def query_collection_with_context(
            collection: chromadb.Collection,
            query_text: str,
            n_results: int = 3,
            context_window: int = 1,
            metadata_filter: Optional[dict] = None
    ) -> dict:
        """
        Advanced query function that retrieves results with surrounding context chunks.

        Args:
            collection: ChromaDB collection object to search
            query_text: The text to search for
            n_results: Number of primary results to return
            context_window: Number of adjacent chunks to include before/after each result
            metadata_filter: Optional metadata filter

        Returns:
            Dictionary with results including context chunks
        """

        # Get initial results
        initial_results = query_collection(
            collection=collection,
            query_text=query_text,
            n_results=n_results,
            metadata_filter=metadata_filter
        )

        enhanced_results = {
            "query": query_text,
            "total_results": initial_results["total_results"],
            "results_with_context": []
        }

        for result in initial_results["results"]:
            # Extract chunk information from metadata
            chunk_index = result["metadata"].get("chunk_index", 0)
            pdf_hash = result["metadata"].get("pdf_hash", "")
            total_chunks = result["metadata"].get("total_chunks", 1)

            # Find context chunks
            context_chunks = {"before": [], "after": []}

            if context_window > 0 and pdf_hash:
                # Get chunks before
                for i in range(max(0, chunk_index - context_window), chunk_index):
                    context_id = f"{pdf_hash}_chunk_{i:04d}"
                    try:
                        context_result = collection.get(ids=[context_id])
                        if context_result["documents"]:
                            context_chunks["before"].append({
                                "id": context_id,
                                "document": context_result["documents"][0],
                                "metadata": context_result["metadatas"][0]
                            })
                    except:
                        pass  # Context chunk not found, skip

                # Get chunks after
                for i in range(chunk_index + 1, min(total_chunks, chunk_index + context_window + 1)):
                    context_id = f"{pdf_hash}_chunk_{i:04d}"
                    try:
                        context_result = collection.get(ids=[context_id])
                        if context_result["documents"]:
                            context_chunks["after"].append({
                                "id": context_id,
                                "document": context_result["documents"][0],
                                "metadata": context_result["metadatas"][0]
                            })
                    except:
                        pass  # Context chunk not found, skip

            enhanced_result = {
                "main_result": result,
                "context": context_chunks,
                "full_context_text": ""
            }

            # Create full context text
            full_text_parts = []
            for ctx in context_chunks["before"]:
                full_text_parts.append(ctx["document"])
            full_text_parts.append(f">>> MAIN RESULT: {result['document']} <<<")
            for ctx in context_chunks["after"]:
                full_text_parts.append(ctx["document"])

            enhanced_result["full_context_text"] = "\n\n".join(full_text_parts)
            enhanced_results["results_with_context"].append(enhanced_result)

        return enhanced_results