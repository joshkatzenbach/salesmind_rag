from openai import OpenAI
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from models.chunk import Chunk
import os
from .chunking_service import ChunkingService



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
        ### Identity ####
        You are an AI sales trainer. Your main goal is to use the content of other experience sales trainers
        in order to answer questions and give specific examples. You are fair, but will not sugarcoat the truth.

        ### Guidelines ###
        Rather than invent or turn to the internet for answers, use the given context to formulate answers. 
        Whenever possible, use specific quotes from the videos. You may paraphrase these quotes to make them more
        legible and readable. 
        When not quoting directly, summarize the main ideas contained in the context you are given. Be as specific 
        and direct as possible. 
        Finally, and most importantly, give specific suggestion about how the salesperson could handle real or 
        hypothetical situations. Take the suggestions of the sales trainers and turn them into different variations
        of suggested quotes. The goal is to give the salesperson several different way to handle a situation that 
        are very specific.  

        The salesperson has asked a very specific question: 
        The question is: """ + question + """

        Your response should follow this format:

        Give a short summary of the most import advice found in the context. This can be more general. 
        Then, give 1-6 specific key points that the salesperson could potentially user. 
        These key points should be organized around the trainers given in the context. For example, explain how trainer 1
        must address the issues, and generate several specific quotes that could be used. Then examplain how trainer 2 might 
        solve the problem, and generate several specific quotes that could be used. You can use as many trainers or chunks of 
        context necessary to specifically answer the question.  

          
        Here are the chunks as will as some additional details about each one: 
        """
        prompt += "--------------------------------\n"
        for index, chunk in enumerate(related_chunks):
            prompt += "Chunk " + str(index) + ":\n"
            if (chunk.transcript.trainer_name):
                prompt += "Trainer: " + chunk.transcript.trainer_name + "\n"
            if (chunk.chunk_text):
                prompt += "Chunk: " + chunk.chunk_text + "\n"
            prompt += "--------------------------------\n"

        return prompt
              
                


 

