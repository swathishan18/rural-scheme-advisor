"""RAG layer: loads government scheme documents (.txt / .pdf), chunks them,
embeds them locally and retrieves the most relevant chunks."""
import os
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL, DATA_DIR


def _read_file(path: str) -> str:
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _chunk(text: str, size: int = 700, overlap: int = 100):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) <= size:
            cur += ("\n\n" if cur else "") + p
        else:
            if cur:
                chunks.append(cur)
            cur = cur[-overlap:] + "\n\n" + p if cur else p
    if cur:
        chunks.append(cur)
    return chunks


class SchemeRetriever:
    def __init__(self, data_dir: str = DATA_DIR):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.chunks = []
        for name in sorted(os.listdir(data_dir)):
            if name.lower().endswith((".txt", ".pdf")):
                text = _read_file(os.path.join(data_dir, name))
                for c in _chunk(text):
                    self.chunks.append({"text": c, "source": name})
        if not self.chunks:
            raise RuntimeError("No documents found in data/ folder.")
        self.emb = self.model.encode(
            [c["text"] for c in self.chunks], normalize_embeddings=True
        )

    def search(self, query: str, k: int = 4):
        q = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.emb @ q
        idx = np.argsort(-scores)[:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in idx]
