from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from sqlalchemy.orm import Session

from models.chunk import Chunk
from models.transcript import Transcript

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
MAX_BATCH_TOKENS = int(os.getenv("MAX_BATCH_SIZE", "7000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))



class ChunkingService:
    @staticmethod 
    def run_chunk_pipeline(transcript : Transcript, db : Session):
        chunk_texts = ChunkingService.chunk_text(transcript.transcript_text)
        embeddings = ChunkingService.get_embeddings(chunk_texts)
        chunks : list[Chunk] = []
        
        for index, chunk_text in enumerate(chunk_texts, start=0):
            chunks.append(Chunk(
                transcript_id=transcript.id,
                chunk_index=index,
                chunk_text=chunk_text,
                embedding=embeddings[index]
            ))
        db.add_all(chunks)
        db.commit()

    @staticmethod
    def chunk_text(text : str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP,   
            separators=["\n\n", "\n", ".", "!", "?"]
        )
        chunk_texts = splitter.split_text(text)
        return chunk_texts

    
    @staticmethod
    def get_embeddings(chunk_texts : list[str]) -> list[list[float]]:
        client = OpenAI()
        response = client.embeddings.create(
            input=chunk_texts,
            model="text-embedding-3-small"
        )
        embeddings = [data.embedding for data in response.data]
        return embeddings

    def batch_embeddings(chunk_texts : list[str]) -> list[list[float]]:
        batch_size = MAX_BATCH_TOKENS // CHUNK_SIZE;
        currentIndex = 0
        