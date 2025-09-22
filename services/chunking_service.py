import traceback
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai 
from sqlalchemy.orm import Session
import os

from models.chunk import Chunk
from models.transcript import Transcript

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
MAX_BATCH_TOKENS = int(os.getenv("MAX_BATCH_SIZE", "7000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))



class ChunkingService:
    @staticmethod 
    def run_chunk_pipeline(transcript, db : Session):
        chunk_texts = ChunkingService.chunk_text(transcript.transcript_text)
        embeddings = ChunkingService.batch_embeddings(chunk_texts)
        chunks = ChunkingService.create_chunks(chunk_texts, embeddings, transcript.id)
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
        try: 
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.embeddings.create(
                input=chunk_texts,
                model="text-embedding-3-small"
            )
            embeddings = [data.embedding for data in response.data]
        except Exception as e:
            print(e)
            traceback.print_exc()
            return []
        return embeddings

    @staticmethod
    def batch_embeddings(chunk_texts : list[str]) -> list[list[float]]:
        batch_size : int = MAX_BATCH_TOKENS // CHUNK_SIZE;
        num_chunks : int = len(chunk_texts)
        embeddings : list[list[float]] = []
        for i in range(0, num_chunks, batch_size):
            upperIndex = i + batch_size if i + batch_size < num_chunks else num_chunks
            batch_texts = chunk_texts[i:upperIndex]
            batch_embeddings = ChunkingService.get_embeddings(batch_texts)
            embeddings.extend(batch_embeddings)
        return embeddings

    @staticmethod
    def create_chunks(chunk_texts : list[str], embeddings : list[list[float]], transcript_id : int) -> list[Chunk]:
        chunks : list[Chunk] = []
        for index, chunk_text in enumerate(chunk_texts):
            chunks.append(Chunk(
                chunk_text=chunk_text,
                embedding=embeddings[index],
                transcript_id=transcript_id,
                chunk_index=index
            ))
        return chunks