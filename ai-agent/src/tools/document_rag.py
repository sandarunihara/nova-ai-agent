"""
src/tools/document_rag.py
Local document RAG engine for NOVA.
Supports PDF and Markdown/text files with semantic search via sentence-transformers.
"""

import os
import re
import numpy as np
from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    """A single chunk of text from a loaded document."""
    text: str
    doc_name: str
    page_num: int  # 1-indexed page number (PDF) or 0 for text files
    chunk_index: int
    embedding: np.ndarray = field(default_factory=lambda: np.array([]))


class DocumentStore:
    """
    In-memory document manager with semantic search.
    Loads PDFs and Markdown/text files, chunks them, embeds them,
    and retrieves relevant chunks via cosine similarity.
    """

    def __init__(self, embedding_model_id: str, chunk_size: int = 500,
                 chunk_overlap: int = 50, cache_dir: str = None):
        self.embedding_model_id = embedding_model_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.cache_dir = cache_dir
        self._model = None  # Lazy-loaded sentence-transformer
        self._documents: dict[str, list[DocumentChunk]] = {}  # doc_name -> chunks

    # --- Public API ---

    @property
    def has_documents(self) -> bool:
        return len(self._documents) > 0

    def load_document(self, filepath: str) -> dict:
        """
        Load a PDF or Markdown/text file, chunk it, embed it, and store it.
        Returns a dict with status info: {doc_name, pages, chunks, success, error}.
        """
        filepath = filepath.strip().strip('"').strip("'")

        if not os.path.isfile(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}

        doc_name = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()

        # Extract text
        try:
            if ext == ".pdf":
                pages = self._extract_pdf(filepath)
            elif ext in (".md", ".markdown", ".txt", ".text", ".rst", ".log", ".csv", ".json"):
                pages = self._extract_text_file(filepath)
            else:
                return {"success": False, "error": f"Unsupported file type: {ext}. Supported: .pdf, .md, .txt"}
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}

        if not pages or all(not p.strip() for p in pages):
            return {"success": False, "error": "File appears to be empty or contains no extractable text."}

        # Chunk the text
        chunks = self._chunk_pages(pages, doc_name)

        if not chunks:
            return {"success": False, "error": "No text chunks could be created from the file."}

        # Compute embeddings
        self._ensure_model_loaded()
        texts = [c.text for c in chunks]
        embeddings = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]

        # Store (replace if same name already loaded)
        self._documents[doc_name] = chunks

        return {
            "success": True,
            "doc_name": doc_name,
            "pages": len(pages),
            "chunks": len(chunks),
        }

    def unload_document(self, doc_name: str) -> dict:
        """Remove a loaded document by name."""
        if doc_name in self._documents:
            chunk_count = len(self._documents[doc_name])
            del self._documents[doc_name]
            return {"success": True, "doc_name": doc_name, "chunks_removed": chunk_count}

        # Try partial match
        matches = [name for name in self._documents if doc_name.lower() in name.lower()]
        if len(matches) == 1:
            name = matches[0]
            chunk_count = len(self._documents[name])
            del self._documents[name]
            return {"success": True, "doc_name": name, "chunks_removed": chunk_count}

        if len(matches) > 1:
            return {"success": False, "error": f"Ambiguous name. Matches: {', '.join(matches)}"}

        return {"success": False, "error": f"No document named '{doc_name}' is loaded."}

    def list_documents(self) -> list[dict]:
        """Return a list of loaded documents with their stats."""
        result = []
        for doc_name, chunks in self._documents.items():
            page_nums = set(c.page_num for c in chunks)
            result.append({
                "name": doc_name,
                "pages": max(page_nums) if page_nums else 0,
                "chunks": len(chunks),
            })
        return result

    def search(self, query: str, top_k: int = 5) -> list[tuple[DocumentChunk, float]]:
        """
        Search all loaded documents for chunks relevant to the query.
        Returns list of (chunk, similarity_score) tuples, sorted by descending similarity.
        """
        if not self._documents:
            return []

        self._ensure_model_loaded()

        # Embed query
        query_embedding = self._model.encode([query], normalize_embeddings=True)[0]

        # Compute cosine similarity against all chunks
        results = []
        for chunks in self._documents.values():
            for chunk in chunks:
                similarity = float(np.dot(query_embedding, chunk.embedding))
                results.append((chunk, similarity))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    # --- Text Extraction ---

    @staticmethod
    def _extract_pdf(filepath: str) -> list[str]:
        """Extract text from a PDF file using PyMuPDF, one string per page."""
        import fitz  # PyMuPDF

        pages = []
        with fitz.open(filepath) as doc:
            for page in doc:
                text = page.get_text("text")
                if text and text.strip():
                    pages.append(text.strip())
        return pages

    @staticmethod
    def _extract_text_file(filepath: str) -> list[str]:
        """Read a text/markdown file as a single 'page'."""
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if content.strip():
            return [content.strip()]
        return []

    # --- Chunking ---

    def _chunk_pages(self, pages: list[str], doc_name: str) -> list[DocumentChunk]:
        """Split pages into overlapping chunks."""
        chunks = []
        chunk_index = 0

        for page_num, page_text in enumerate(pages, start=1):
            # Split by paragraphs first
            paragraphs = re.split(r'\n\s*\n', page_text)

            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # If adding this paragraph exceeds chunk size, save current chunk
                if current_chunk and (len(current_chunk) + len(para) + 2) > self.chunk_size:
                    chunks.append(DocumentChunk(
                        text=current_chunk.strip(),
                        doc_name=doc_name,
                        page_num=page_num,
                        chunk_index=chunk_index,
                    ))
                    chunk_index += 1

                    # Overlap: keep the tail of the current chunk
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        current_chunk = current_chunk[-self.chunk_overlap:] + "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para

                # If a single paragraph is very long, split it by sentences
                if len(current_chunk) > self.chunk_size * 1.5:
                    sentence_chunks = self._split_long_text(current_chunk, doc_name, page_num, chunk_index)
                    chunks.extend(sentence_chunks)
                    chunk_index += len(sentence_chunks)
                    current_chunk = ""

            # Flush remaining content for this page
            if current_chunk.strip():
                chunks.append(DocumentChunk(
                    text=current_chunk.strip(),
                    doc_name=doc_name,
                    page_num=page_num,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1

        return chunks

    def _split_long_text(self, text: str, doc_name: str, page_num: int,
                         start_index: int) -> list[DocumentChunk]:
        """Split a long text block into sentence-boundary chunks."""
        # Split by sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current = ""
        idx = start_index

        for sentence in sentences:
            if current and (len(current) + len(sentence) + 1) > self.chunk_size:
                chunks.append(DocumentChunk(
                    text=current.strip(),
                    doc_name=doc_name,
                    page_num=page_num,
                    chunk_index=idx,
                ))
                idx += 1
                # Overlap
                if self.chunk_overlap > 0 and len(current) > self.chunk_overlap:
                    current = current[-self.chunk_overlap:] + " " + sentence
                else:
                    current = sentence
            else:
                current = (current + " " + sentence).strip() if current else sentence

        if current.strip():
            chunks.append(DocumentChunk(
                text=current.strip(),
                doc_name=doc_name,
                page_num=page_num,
                chunk_index=idx,
            ))

        return chunks

    # --- Embedding Model ---

    def _ensure_model_loaded(self):
        """Lazy-load the sentence-transformer model on first use."""
        if self._model is None:
            print(f"📄 [Nova Docs] Loading embedding model '{self.embedding_model_id}'...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self.embedding_model_id,
                cache_folder=self.cache_dir,
            )
            print(f"📄 [Nova Docs] Embedding model ready.")
