import os
import pandas as pd
from typing import List, Dict, Any, Optional

# 1️⃣ OpenAI LLM (chat completion)
try:
    import openai
except ImportError:
    raise ImportError("Install the OpenAI library: pip install openai")

# 2️⃣ ChromaDB client
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    raise ImportError("Install the ChromaDB client: pip install chromadb")

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generic wrapper around OpenAI's ChatCompletion API.

    Args:
        messages: List of message dicts (role, content) to feed into the model.
        model:  The OpenAI model name.
        temperature: Controls randomness.
        max_tokens: Optional token limit for the response.

    Returns:
        The assistant's reply as a plain string.
    """
    url = f"{http://localhost:11434}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": messages}],
        "options": {"temperature": temperature, "num_predict": max_tokens},
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        logging.info("Request sent to Ollama")
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Ollama LLM-Aufruf fehlgeschlagen: {e}")

def retrieve_context(
    chroma_client: chromadb.Client,
    collection_name: str,
    query_text: str,
    k: int = 3,
    embedding_fn=None,
) -> str:
    """
    Query ChromaDB for the `k` most relevant documents for `query_text`.

    Returns the concatenated text of the retrieved documents.
    """
    #TODO: Connect to ChromaDBConnector
    #TODO: implement query function
    return ""

# --------------------------------------------------------------------------- #
# Evaluation class
# --------------------------------------------------------------------------- #

class Evaluation:
    """
    Run two evaluation paths over a CSV of questions.

    Parameters
    ----------
    csv_path : str
        Path to a CSV file that must contain at least a column named
        `question`. Additional columns will be carried over unchanged.
    chroma_host : str
        Hostname/IP of the ChromaDB server.
    chroma_port : int
        Port of the ChromaDB server.
    chroma_collection : str
        Name of the ChromaDB collection that holds the context documents.
    llm_model : str, default="gpt-4o-mini"
        OpenAI model to use for answering questions.
    short_prompt : str, default="You are a helpful assistant."
        System prompt used for the no‑context path.
    context_prompt : str, default="Using the following context, answer the question."
        System prompt used for the context‑augmented path.
    temperature : float, default=0.2
        Temperature for the LLM calls.
    """

    def __init__(
        self,
        csv_path: str,
        chroma_host: str = "localhost",
        chroma_port: int = 8000,
        chroma_collection: str = "default",
        llm_model: str = "gpt-4o-mini",
        short_prompt: str = "You are a helpful assistant.",
        context_prompt: str = (
            "Using the following context, answer the question. "
            "If the context does not contain enough information, say that you do not know."
        ),
        temperature: float = 0.2,
        context_k: int = 3,
    ) -> None:
        # Store config
        self.csv_path = csv_path
        self.chromadb_uri = f"http://{chroma_host}:{chroma_port}"
        self.chromadb_collection = chroma_collection
        self.llm_model = llm_model
        self.short_prompt = short_prompt
        self.context_prompt = context_prompt
        self.temperature = temperature
        self.context_k = context_k

        # Load questions
        self.df_questions = pd.read_csv(csv_path)

        # Validate required column
        if "question" not in self.df_questions.columns:
            raise ValueError("CSV must contain a 'question' column")

        # Create Chroma client
        self.chromadb_client = chromadb.Client(
            settings=chromadb.Settings(
                chroma_server_host=chroma_host,
                chroma_server_port=chroma_port,
            )
        )

    # ----------------------------------------------------------------------- #
    # Core public method
    # ----------------------------------------------------------------------- #
    def run(self) -> pd.DataFrame:
        """
        Execute both evaluation paths and return a DataFrame with the results.

        The returned DataFrame has the following columns:

        - All original columns from the CSV
        - `context`: the concatenated ChromaDB context (or empty string)
        - `answer_no_context`: answer from LLM with only the short prompt
        - `answer_with_context`: answer from LLM that also receives the context
        """
        results = []

        for idx, row in self.df_questions.iterrows():
            question = str(row["Fragen"]).strip()
            # 1️⃣ Get context from ChromaDB
            context = self._get_context_for_question(question)

            # 2️⃣ Ask LLM without context
            answer_no_ctx = self._ask_llm(question)

            # 3️⃣ Ask LLM with context
            answer_with_ctx = self._ask_llm_with_context(question, context)

            # Build a new record
            record = row.to_dict()
            record.update(
                {
                    "context": context,
                    "answer_no_context": answer_no_ctx,
                    "answer_with_context": answer_with_ctx,
                }
            )
            results.append(record)

        # Return as DataFrame
        return pd.DataFrame(results)

    # ----------------------------------------------------------------------- #
    # Helper methods (private)
    # ----------------------------------------------------------------------- #
    def _get_context_for_question(self, question: str) -> str:
        """
        Wrapper around the `retrieve_context` helper.  Returns an empty string
        if no documents were found.
        """
        try:
            context = retrieve_context(
                chroma_client=self.chromadb_client,
                collection_name=self.chromadb_collection,
                query_text=question,
                k=self.context_k,
            )
            return context.strip() if context else ""
        except Exception as e:
            # Log and return empty context; in production you might want to raise
            print(f"[WARNING] ChromaDB query failed for '{question}': {e}")
            return ""

    def _ask_llm(self, question: str) -> str:
        """
        LLM call that only receives the short prompt + question.
        """
        messages = [
            {"role": "system", "content": self.short_prompt},
            {"role": "user", "content": question},
        ]
        return call_llm(
            messages=messages,
            model=self.llm_model,
            temperature=self.temperature,
        )

    def _ask_llm_with_context(self, question: str, context: str) -> str:
        """
        LLM call that receives a context string in addition to the question.
        """
        # If no context, fall back to the short prompt + question
        if not context:
            return self._ask_llm(question)

        messages = [
            {"role": "system", "content": self.context_prompt},
            {"role": "user", f"content": f"Question: {question}\n\nContext:\n{context}"},
        ]
        return call_llm(
            messages=messages,
            model=self.llm_model,
            temperature=self.temperature,
        )