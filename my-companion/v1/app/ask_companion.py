# ask_companion.py
import os
import json
import uuid
import requests
import streamlit as st
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from pathlib import Path
from utils.data_store import load_data
from docx import Document
from PyPDF2 import PdfReader
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------
# Configuration from .env file
# ---------------------------
LMSTUDIO_URL = os.getenv("LLM_ENDPOINT", "http://localhost:1234/v1/chat/completions")
LM_MODEL = os.getenv("LLM_MODEL", "local-model")
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "data/attachments")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
INDEX_DIR = os.getenv("INDEX_DIR", ".kb_index")

# Retrieval params
TOP_K = int(os.getenv("TOP_K", "6"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# LM request params
LM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LM_MAX_TOKENS = int(os.getenv("LM_MAX_TOKENS", "512"))
LM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "300"))

# ---------------------------
# Utilities: text extraction
# ---------------------------
def extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

def extract_text_from_pdf(path: str) -> str:
    text_chunks = []
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            try:
                text_chunks.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(text_chunks)
    except Exception:
        return ""

def extract_text_from_file(path: str) -> str:
    path = str(path)
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    if path.lower().endswith(".docx"):
        return extract_text_from_docx(path)
    if path.lower().endswith(".txt"):
        return extract_text_from_txt(path)
    # fallback: empty
    return ""

# ---------------------------
# Utilities: chunking
# ---------------------------
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if start >= length:
            break
    return chunks

# ---------------------------
# Embedding + FAISS index management
# ---------------------------
class Retriever:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME, index_dir: str = INDEX_DIR):
        self.embedder = SentenceTransformer(model_name)
        self.index_dir = Path(index_dir)
        self.index_path = self.index_dir / "faiss.index"
        self.meta_path = self.index_dir / "meta.json"
        self.id_to_meta: Dict[int, Dict[str, Any]] = {}
        self.index = None
        self._load_index()

    def _load_index(self):
        if not self.index_dir.exists():
            self.index_dir.mkdir(parents=True, exist_ok=True)
        if self.index_path.exists() and self.meta_path.exists():
            # load
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                # meta is dict of str(id)->metadata
                self.id_to_meta = {int(k): v for k, v in meta.items()}
                return
            except Exception as e:
                st.warning(f"Failed to load existing index: {e}")
        # otherwise init empty index
        self.index = None
        self.id_to_meta = {}

    def _create_index_from_embeddings(self, embeddings: np.ndarray):
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index

    def build_from_documents(self, docs: List[Dict[str, Any]]):
        """
        docs: list of { 'text': str, 'source': 'basic_info|other_activities|project|attachment', 'meta': {...} }
        """
        # build embeddings in batches
        texts = [d["text"] for d in docs]
        if not texts:
            self.index = None
            self.id_to_meta = {}
            return

        embeddings = self.embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        # create index and store metas
        self.index = self._create_index_from_embeddings(embeddings)
        self.id_to_meta = {i: {**docs[i].get("meta", {}), "source": docs[i].get("source", "")} for i in range(len(docs))}
        # persist
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in self.id_to_meta.items()}, f, ensure_ascii=False, indent=2)

    def add_documents(self, docs: List[Dict[str, Any]]):
        # add docs to existing index
        texts = [d["text"] for d in docs]
        if not texts:
            return
        embeddings = self.embedder.encode(texts, convert_to_numpy=True)
        if self.index is None:
            self.index = self._create_index_from_embeddings(embeddings)
            start_id = 0
        else:
            start_id = self.index.ntotal
            self.index.add(embeddings)
        for i, d in enumerate(docs):
            self.id_to_meta[start_id + i] = {**d.get("meta", {}), "source": d.get("source", "")}
        # persist
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in self.id_to_meta.items()}, f, ensure_ascii=False, indent=2)

    def retrieve(self, query: str, top_k: int = TOP_K) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None or self.index.ntotal == 0:
            return []
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        D, I = self.index.search(q_emb, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            meta = self.id_to_meta.get(int(idx), {})
            results.append((meta, float(dist)))
        return results

    def get_text_by_meta(self, meta) -> str:
        return meta.get("text", "")

# ---------------------------
# Build knowledge documents from data + attachments
# ---------------------------
def build_documents_from_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    docs = []
    # Basic Info: include name, role, summary, urls, attachments names (attachments separately processed)
    ui = data.get("user_profile", {})
    basic_text = f"Name: {ui.get('name','')}\nRole: {ui.get('current_role','')}\nSummary: {ui.get('profile_summary','')}\n"
    docs.append({"text": basic_text, "source": "basic_info", "meta": {"section": "basic_info", "text": basic_text}})

    # Technical skills - either under user_profile or top-level technical_skills
    skills = data.get("technical_skills", data.get("user_profile", {}).get("technical_skills", {}))
    if skills:
        for cat, items in skills.items():
            text = f"{cat}: {', '.join(items)}"
            docs.append({"text": text, "source": "technical_skills", "meta": {"section": "technical_skills", "category": cat, "text": text}})

    # Projects
    projects = data.get("projects", [])
    for i, p in enumerate(projects):
        responsibilities = p.get('responsibilities', '')
        if isinstance(responsibilities, list):
            # Handle legacy format (array)
            responsibilities = ', '.join(responsibilities)
        
        text = (
            f"Project {i+1} Domain: {p.get('domain','')}\nRole: {p.get('role','')}\nDescription: {p.get('description','')}\n"
            f"Responsibilities: {responsibilities}\nRelated Skills: {', '.join(p.get('related_skills',[]))}\nTags: {', '.join(p.get('tags',[]))}"
        )
        docs.append({"text": text, "source": "project", "meta": {"section": "projects", "index": i, "text": text}})

    # Other activities
    other_acts = data.get("other_activities", [])
    for i, a in enumerate(other_acts):
        text = (
            f"Activity {i+1} Title: {a.get('title','')}\nDescription: {a.get('description','')}\n"
            f"Related Skills: {', '.join(a.get('related_skills',[]))}\nTags: {', '.join(a.get('tags',[]))}\n"
        )
        docs.append({"text": text, "source": "other_activities", "meta": {"section": "other_activities", "index": i, "text": text}})

    # Attachments: ingest attachment text from attachments folder
    # Look through attachments referenced in user_profile and other places
    referenced_files = set()
    # user_profile attachments
    up_att = ui.get("/data/attachments", [])
    for a in up_att:
        referenced_files.add('/basic_info/' + a)
    # other activities attachments
    for a in other_acts:
        for f in a.get("/data/attachments", []):
            referenced_files.add('/other_activities/' + f)
    # project attachments may be stored similarly if used; adapt if necessary

    for fname in tqdm(list(referenced_files), desc="Reading attachments", disable=False):
        path = os.path.join(ATTACHMENTS_DIR, fname)
        if not os.path.exists(path):
            continue
        text = extract_text_from_file(path)
        if not text:
            continue
        # chunk and create docs with attachment source and filename in meta
        chunks = chunk_text(text)
        for idx, c in enumerate(chunks):
            docs.append({
                "text": c,
                "source": "attachment",
                "meta": {"section": "attachment", "filename": fname, "chunk_index": idx, "text": c}
            })
    return docs

# ---------------------------
# Build prompt with retrieved context
# ---------------------------
def build_prompt(query: str, retrieved: List[Tuple[Dict[str, Any], float]]) -> str:
    system_instructions = (
        "You are a helpful assistant that answers questions only using the provided context from the user's profile and attachments. "
        "If the answer is not contained in the context, say 'I don't know' or ask for clarification. "
        #"Always list the sources used (section or filename) at the end. Avoid fabricating facts."
    )

    context_blocks = []
    sources = []
    for meta, dist in retrieved:
        text = meta.get("text") or meta.get("content") or ""
        # include small snippet and meta info
        source = meta.get("filename") or meta.get("section") or meta.get("source") or "unknown"
        snippet = text[:800].strip()
        context_blocks.append(f"[Source: {source}]\n{snippet}\n")
        sources.append(source)

    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No context available."

    prompt = (
        f"{system_instructions}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query}\n\n"
        "INSTRUCTIONS:\n"
        "1) Answer concisely using ONLY the context above.\n"
        "2) If context is insufficient, say 'I don't know' and ask what more is needed.\n"
        #"3) At the end, include a 'SOURCES:' section listing each source used.\n"
    )
    return prompt

# ---------------------------
# Call LM Studio (local) chat/completions
# ---------------------------
def call_local_lm(prompt: str, model: str = LM_MODEL, temperature: float = LM_TEMPERATURE, max_tokens: int = LM_MAX_TOKENS) -> str:
    """
    Sends a single-message system+user style prompt to LM Studio's chat/completions endpoint.
    LM Studio's API is OpenAI-compatible-ish; adjust if needed.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        resp = requests.post(LMSTUDIO_URL, headers=headers, json=payload, timeout=LM_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # try to extract text: for OpenAI-like responses it's data["choices"][0]["message"]["content"]
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            if "text" in choice:
                return choice["text"]
        # fallback
        return json.dumps(data)
    except requests.exceptions.Timeout:
        return f"[LM call failed] Request timed out after {LM_TIMEOUT} seconds. The model might be processing a complex query."
    except Exception as e:
        return f"[LM call failed] {e}"

# ---------------------------
# Streamlit UI
# ---------------------------
def show(data):
    st.title("🤖 Ask Companion")
    # ensure retriever singleton in session_state
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "docs_built" not in st.session_state:
        st.session_state.docs_built = False

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("🔧 Rebuild index"):
            st.session_state.retriever = None
            st.session_state.docs_built = False
    with col2:
        if st.button("🔄 Reload data"):
            data = load_data()
            st.session_state.retriever = None
            st.session_state.docs_built = False

    st.markdown("---")

    # Build retriever lazily
    if st.session_state.retriever is None:
        st.info("Building index (this may take a few seconds)...")
        retriever = Retriever()
        docs = build_documents_from_data(data)
        retriever.build_from_documents(docs)
        # also store text in metadata for prompt building
        # we stored meta.text earlier when building docs; ensure id_to_meta includes 'text'.
        # But above we used meta without text; ensure here we augment id_to_meta entries with text:
        # We rebuild id_to_meta when creating index; for simplicity, we re-run embedding step in retriever.build_from_documents
        st.session_state.retriever = retriever
        st.session_state.docs_built = True
        st.success("Index built.")
    else:
        retriever = st.session_state.retriever

    st.markdown("### Ask a question about your profile / experience")
    query = st.text_input("Enter your question here", key="ask_query")
    ask_btn = st.button("Ask")

    if ask_btn and query.strip():
        with st.spinner("Retrieving relevant context..."):
            retrieved = retriever.retrieve(query, top_k=TOP_K)
            # fetch actual meta texts for context; if the stored meta doesn't include the text, we can't show snippet.
            # To keep things simple, we will use meta.get('text') where available.
        prompt = build_prompt(query, retrieved)
        with st.spinner("Calling local model..."):
            answer = call_local_lm(prompt)
        st.markdown("### ✅ Answer")
        st.write(answer)

        # st.markdown("### 📚 Sources / retrieved snippets")
        # if retrieved:
        #     for meta, dist in retrieved:
        #         src = meta.get("filename") or meta.get("section") or meta.get("source") or "unknown"
        #         snippet = (meta.get("text") or "")[:1000]
        #         st.markdown(f"**Source:** {src} — distance {dist:.4f}")
        #         if snippet:
        #             st.code(snippet)
        # else:
        #     st.info("No context retrieved; model had to answer without profile context.")

    st.markdown("---")
