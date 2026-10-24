import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from google import genai
import pypdf

from src.config import (
    KB_DIR,
    VECTOR_INDEX_PATH,
    GEMINI_API_KEY,
    GEMINI_EMBED_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RETRIEVAL,
    SIMILARITY_THRESHOLD,
)

def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)

def compute_file_hash(filepath: Path) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def extract_text_from_file(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif suffix == ".pdf":
        text_parts = []
        try:
            reader = pypdf.PdfReader(str(filepath))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
        except Exception as e:
            print(f"Error reading PDF {filepath.name}: {e}")
        return "\n\n".join(text_parts)
    return ""

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into coherent overlapping chunks respecting paragraphs."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue
        para_len = len(para_clean)
        
        # If single paragraph is larger than chunk_size, split by lines or sentences
        if para_len > chunk_size:
            lines = para_clean.split("\n")
            for line in lines:
                line_clean = line.strip()
                if not line_clean:
                    continue
                if current_len + len(line_clean) > chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    # Retain last piece for overlap
                    current_chunk = [current_chunk[-1]] if current_chunk else []
                    current_len = sum(len(c) for c in current_chunk)
                current_chunk.append(line_clean)
                current_len += len(line_clean)
        else:
            if current_len + para_len > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [current_chunk[-1]] if current_chunk else []
                current_len = sum(len(c) for c in current_chunk)
            current_chunk.append(para_clean)
            current_len += para_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return [c.strip() for c in chunks if len(c.strip()) > 30]

class VectorStore:
    def __init__(self):
        self.index_path = VECTOR_INDEX_PATH
        self.chunks: List[Dict[str, Any]] = []
        self.file_hashes: Dict[str, str] = {}
        self.client = None
        self.load()

    def _get_client(self):
        if self.client is None:
            self.client = get_genai_client()
        return self.client

    def load(self):
        if self.index_path.exists():
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", [])
                    self.file_hashes = data.get("file_hashes", {})
            except Exception as e:
                print(f"Failed to load vector index: {e}")
                self.chunks = []
                self.file_hashes = {}
        else:
            self.chunks = []
            self.file_hashes = {}

    def save(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump({
                "chunks": self.chunks,
                "file_hashes": self.file_hashes
            }, f, ensure_ascii=False)

    def sync_knowledge_base(self, force: bool = False) -> Dict[str, int]:
        """Scan KB_DIR, chunk new or modified files, compute embeddings, and update index."""
        client = self._get_client()
        kb_files = list(KB_DIR.glob("*.md")) + list(KB_DIR.glob("*.txt")) + list(KB_DIR.glob("*.pdf"))
        
        current_file_hashes = {f.name: compute_file_hash(f) for f in kb_files}
        
        # Check files to remove
        active_filenames = set(current_file_hashes.keys())
        initial_chunk_count = len(self.chunks)
        self.chunks = [c for c in self.chunks if c.get("source") in active_filenames]
        
        added_files = 0
        added_chunks = 0
        
        for file in kb_files:
            file_name = file.name
            current_hash = current_file_hashes[file_name]
            
            # If unchanged and not forcing, keep existing chunks
            if not force and self.file_hashes.get(file_name) == current_hash:
                continue

            # Remove previous chunks for this file if re-indexing
            self.chunks = [c for c in self.chunks if c.get("source") != file_name]
            
            text = extract_text_from_file(file)
            if not text.strip():
                continue
                
            raw_chunks = chunk_text(text)
            if not raw_chunks:
                continue

            # Batch embed in slices of up to 20
            batch_size = 20
            file_embeddings = []
            for i in range(0, len(raw_chunks), batch_size):
                batch = raw_chunks[i:i + batch_size]
                try:
                    res = client.models.embed_content(
                        model=GEMINI_EMBED_MODEL,
                        contents=batch
                    )
                    for emb in res.embeddings:
                        file_embeddings.append(emb.values)
                except Exception as e:
                    print(f"Error embedding batch for {file_name}: {e}")
                    # Fallback single embed
                    for chunk in batch:
                        try:
                            res_single = client.models.embed_content(
                                model=GEMINI_EMBED_MODEL,
                                contents=chunk
                            )
                            file_embeddings.append(res_single.embeddings[0].values)
                        except Exception as e2:
                            print(f"Skipping chunk due to error: {e2}")

            for idx, (chunk_text_content, emb) in enumerate(zip(raw_chunks[:len(file_embeddings)], file_embeddings)):
                self.chunks.append({
                    "id": f"{file_name}_{idx}",
                    "source": file_name,
                    "text": chunk_text_content,
                    "embedding": emb
                })
                added_chunks += 1
                
            self.file_hashes[file_name] = current_hash
            added_files += 1

        self.save()
        return {
            "total_files": len(kb_files),
            "updated_files": added_files,
            "total_chunks": len(self.chunks),
            "added_chunks": added_chunks
        }

    def search(self, query: str, top_k: int = TOP_K_RETRIEVAL, threshold: float = SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
        """Perform semantic cosine-similarity search against indexed knowledge base chunks."""
        if not self.chunks:
            return []

        client = self._get_client()
        try:
            query_res = client.models.embed_content(
                model=GEMINI_EMBED_MODEL,
                contents=query
            )
            query_emb = np.array(query_res.embeddings[0].values, dtype=np.float32)
        except Exception as e:
            print(f"Failed to embed query: {e}")
            return []

        query_norm = np.linalg.norm(query_emb)
        if query_norm == 0:
            return []

        doc_embeddings = np.array([c["embedding"] for c in self.chunks], dtype=np.float32)
        doc_norms = np.linalg.norm(doc_embeddings, axis=1)
        doc_norms[doc_norms == 0] = 1e-10

        # Cosine similarity: (A . B) / (||A|| * ||B||)
        similarities = np.dot(doc_embeddings, query_emb) / (doc_norms * query_norm)

        top_indices = np.argsort(similarities)[::-1]
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                chunk = self.chunks[idx].copy()
                chunk["score"] = round(score, 4)
                # Omit raw vector from search results
                chunk.pop("embedding", None)
                results.append(chunk)
                if len(results) >= top_k:
                    break

        return results

# Singleton vector store instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
