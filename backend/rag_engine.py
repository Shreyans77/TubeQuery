import os
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard, short, and embed links.
    """
    # Regex for standard and short URLs
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")

def get_rag_chain(video_url: str):
    """
    Ingests a YouTube video, processes it, and returns a RAG chain (model + retriever).
    """
    video_id = extract_video_id(video_url)
    
    # 1. Transcript Ingestion
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Try to find English transcript
        try:
            transcript = transcript_list.find_transcript(["en"])
        except:
            # Fallback: take the first one found?
            # Since we don't know the exact API of transcript_list in this version, 
            # we'll stick to what project.py did or try iteration if possible.
            # Assuming find_transcript is the main way.
            # Let's try iterating if find fails.
            try:
                transcript = next(iter(transcript_list))
            except:
                 raise RuntimeError("No transcripts found.")

        captions = transcript.fetch()
        full_text = " ".join(line.text for line in captions)
        
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transcript: {str(e)}")

    if not full_text:
        raise RuntimeError("Transcript is empty.")

    # 2. Text Splitting
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents = splitter.create_documents([full_text])

    # 3. Embeddings & Vector Store
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_documents(documents, embeddings)
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # 4. LLM Setup
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        task="text-generation",
        temperature=0.1
    )
    model = ChatHuggingFace(llm=llm)

    prompt_template = PromptTemplate(
        template="""
You are a helpful assistant.
Answer only from the provided transcript context.
If the context is insufficient, say "I don't know".
Context:
{context}

Question:
{question}
""",
        input_variables=["context", "question"]
    )

    return retriever, model, prompt_template

def answer_question(retriever, model, prompt_template, question: str) -> str:
    """
    Uses the provided components to answer a question.
    """
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    final_prompt = prompt_template.invoke({
        "context": context_text,
        "question": question
    })
    
    response = model.invoke(final_prompt)
    return response.content
