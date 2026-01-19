from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface.embeddings import HuggingFaceEmbeddings  
from dotenv import load_dotenv

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

# ----------------------------
# Step 1a: Transcript ingestion
# ----------------------------
video_id = "Gfr50f6ZBvo"

try:
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    transcript = transcript_list.find_transcript(["en"])  # ✅ corrected language code
    captions = transcript.fetch()

    # Convert captions to single text string
    full_text = " ".join(line.text for line in captions)

except TranscriptsDisabled:
    print("Transcript is disabled for this video.")
    full_text = ""  # avoid crashing if transcript disabled

# ----------------------------
# Step 1b: Text splitting
# ----------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

documents = splitter.create_documents([full_text])

# ----------------------------
# Step 1c/1d: Embeddings + Vector store using HuggingFace
# ----------------------------
# Use HuggingFace embeddings instead of OpenAI
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # lightweight, fast
)

vector_store = FAISS.from_documents(documents, embeddings)

# ----------------------------
# Step 2: Retriever
# ----------------------------
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# ----------------------------
# Step 3: LLM + Prompt
# ----------------------------
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="text-generation"
)

model = ChatHuggingFace(llm=llm)

prompt = PromptTemplate(
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

# ----------------------------
# Step 4: Ask question
# ----------------------------
question = "Is the topic of aliens discussed in this video? If yes, what was discussed?"

retrieved_docs = retriever.invoke(question)
context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

final_prompt = prompt.invoke({
    "context": context_text,
    "question": question
})

answer = model.invoke(final_prompt)

print(answer.content)
