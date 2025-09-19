from openai import OpenAI
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from models.chunk import Chunk
import os
from chunking_service import ChunkingService



class QueryService:
    def __init__(self):
        pass
    @staticmethod
    def process_query(question: str, db: Session):
        embedding : list[float] = ChunkingService.get_embeddings([question])[0]
        related_chunks = QueryService.get_closest_chunks(embedding, 10, db)
        prompt = QueryService.build_basic_prompt(question, related_chunks, db)
        answer = QueryService.run_query(prompt)
        return answer


    @staticmethod   
    def get_closest_chunks(embedding: list[float], num_chunks: int, db: Session):
        sqlstmt = (
            select(Chunk)
                .options(joinedload(Chunk.transcript))  # load related transcript
                .order_by(Chunk.embedding.cosine_distance(embedding))  # or .cosine_similarity
                .limit(num_chunks)
        )
        chunks = db.execute(sqlstmt).scalars().all()
        return chunks

    @staticmethod
    def run_query(prompt: str):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


    @staticmethod
    def build_basic_prompt(question: str, related_chunks: list[Chunk], db: Session):

        prompt = """
        You are an AI sales trainer. Your main goal is to answer sales questions in order to help 
        salespeople improve their skills. You will be given a question from a salesperson to answer. 
        You will also be given a list of chunks that are related to the question. You will use the chunks to answer the question.
        These chunks are taken from experiences sales people. You need to use the advice in the chunks to answer the question.
        For chunks that are examples of real sales calls, you need to extract the principles and strategies they are using,
        and extend these strategies to give relevant examples. 

        The question is: """ + question + """

        Your response should be in the following format: 
        Summary (no more than 300 words)
        3-4 Key Bullet Points (no more than 200 words each)
        References to the chunks that you used to answer the question
          
        Here are the chunks as will as some additional details about each one: 
        """
        prompt += "--------------------------------\n"
        for index, chunk in related_chunks:
            if (chunk.transcript.trainer_name):
                prompt += "Trainer: " + chunk.transcript.trainer_name + "\n"
            if (chunk.chunk_text):
                prompt += "Chunk: " + chunk.chunk_text + "\n"
            prompt += "--------------------------------\n"

        return prompt
              
                


 

