from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import pdfplumber
from typing import List, Dict
import os

class ChromaDBConnector:
    """
    Verwaltet die Verbindung zur lokalen ChromaDB VectorDB.
    """
    
    def __init__(self, settings: Settings = None, persist_directory: str = "./chroma_db"):
        # Settings ggf. anpassen, damit persist_directory gesetzt wird
        #TODO: make it persistent
        if settings is None:
            settings = Settings(persist_directory=persist_directory)
        else:
            # Settings überschreiten, falls persist_directory nicht gesetzt ist
            if not hasattr(settings, 'persist_directory') or getattr(settings, 'persist_directory', None) is None:
                settings.persist_directory = persist_directory
        self.client = Client(settings)
        self.embed_fn = embedding_functions.OllamaEmbeddingFunction(model_name="nomic-embed-text")

    def get_collection(self, collection_name: str = "docs") -> Client:
        """
        Lädt eine Collection aus der lokalen ChromaDB oder erstellt sie, falls sie nicht existiert.
        """
        try:
            collection = self.client.get_collection(collection_name)
        except:
            #TODO: make the collection persistent if created completetly new

            # Collection nicht gefunden, erstelle neue + Embedding-Funktion anpassen
            collection = self.client.create_collection(collection_name, embedding_function=self.embed_fn)
        return collection

    def add_pdf_to_collection(self, pdf_path: str, collection_name: str = "docs") -> None:
        """
        Fügt ein PDF-Dokument zu einer Collection hinzu.
        """
        collection = self.get_collection(collection_name)
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
            # split into chunks of 1000 words
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            # Embedding des Dokuments erstellen
            doc_embedding = self.embed_fn(chunks)
            # IDs und Metadaten für jeden Chunk erzeugen
            ids = [f"{os.path.basename(pdf_path)}_{i}" for i in range(len(chunks))]
            metadatas = [{'filename': os.path.basename(pdf_path)} for _ in chunks]
            # Dokument in der Collection speichern
            collection.add(
                documents=chunks,
                embeddings=doc_embedding,
                metadatas=metadatas,
                ids=ids
            )

    def query(self, query_text: str, metric: str, collection_name: str = "docs", top_k: int = 5) -> List[Dict]:
        """
        Führt eine Retrieval-Abfrage durch: Embedding für die Anfrage erstellen und relevante Dokumente zurückgeben.
        """
        collection = self.get_collection(collection_name)
        # Query in der Collection durchführen
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where_document={"$contains": metric}
        )
        # Ergebnisse formatieren
        retrieved = []
        if results and results.get('ids') and results['ids'][0]:
            num_results = len(results['ids'][0])
            metadatas = results.get('metadatas', [[{}] * num_results])[0] # Standardwert falls nicht inkludiert
            documents = results.get('documents', [[None] * num_results])[0] # Standardwert falls nicht inkludiert

            for i in range(num_results):
                doc_info = {
                    "text": documents[i] if documents[i] is not None else "", # Dokumententext
                    "metadata": metadatas[i] if metadatas[i] is not None else {} # Metadaten
                }
                retrieved.append(doc_info)
        # Wenn keine Ergebnisse gefunden wurden (oder ein unerwartetes Format vorliegt),
        # bleibt 'retrieved' eine leere Liste.
        # Kontext und Quellen extrahieren
        context = "\n".join([item["text"] for item in retrieved])
        sources = [item["metadata"] for item in retrieved]
        return context, sources