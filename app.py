from elasticsearch import Elasticsearch, exceptions 
from langchain_core.prompts import PromptTemplate 
from langchain_upstage import ChatUpstage 
from langdetect import detect
import wikipediaapi
# from eng_retrieval import return_query
import re
import numpy as np
from question_ingest import Question, Quest
import os

ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
# WIKI_NAME = os.getenv("WIKI_NAME")

class MiniRAG:
    ELASTIC_CLOUD_ID = ELASTIC_CLOUD_ID

    def __init__(self, ELASTIC_API_KEY, UPSTAGE_API_KEY, wikiproj_name=None):
        def server_connector(ELASTIC_API_KEY):
            try:
                client = Elasticsearch(
                        api_key=ELASTIC_API_KEY,
                        cloud_id=ELASTIC_CLOUD_ID,
                    )
                # print(client.info())
                if client.info().get("name", None) == None:
                    print(client.info()) 
            except ValueError as ve:
                print(f"ValueError: {ve}")
            except Exception as e:
                print(f"Error: {e}")
            return client
        
        self._client = server_connector(ELASTIC_API_KEY)
        self._llm = ChatUpstage(api_key=UPSTAGE_API_KEY) #model="solar-1-mini-chat"
        self._promptstr = None
        self._prompter = PromptTemplate.from_template(self.promptstr) if self._promptstr != None else None
        self._chain = self._prompter | self._llm if self._prompter != None else None
        # self._wiki_client = wikipediaapi.Wikipedia(wikiproj_name, language="en")
        self._question_set = None
        
    @property
    def prompt(self):
        return self._promptstr 
    
    @prompt.setter 
    def prompt(self, promptstring: str):
        """ Example prompt_obj:

        Please provide the most correct answer from the following context.
        If the answer is not present in the context, please  provide a reasonable guess of the answer.
        The answer must look like this: 
        Answer: (<answer>)
        ---
        Question: {question}
        ---
        Context: {context}
        """
        self._promptstr = promptstring
        self._prompter = PromptTemplate.from_template(promptstring)
        self._chain = self._prompter | self._llm

    @property
    def client(self):
        return self._client.info()
    
    @property 
    def question_set(self):
        return self._question_set
    
    @question_set.setter
    def question_set(self, data_path):
        if self._promptstr == None: 
            print("Must set prompt first!")
            return None
        else:
            qset_instance = Question(self._promptstr, data_path)

            self._question_set = qset_instance

    def retrieval(self, qset: Question):

        def context_query(question: Quest ,index="ewhapdf_chunked_index"):
                    
            def parse_query_results(query_results):

                _concat = " ".join([res["_source"]["text"] for res in query_results["hits"]["hits"]])
            
                return _concat

            if question.lang == "en":
                all_results = question.question
            elif question.lang == "ko":
                # question_str = question.question
                question_str = question.question.split("\n")[0] # remove the multiple choice options
                query_results = self._client.search(index=index,query={"match":
                                                            {"text": {"query":question_str}}})
                number_results = query_results["hits"]["total"]["value"]
                question.no_documents = number_results #query_results["hits"]["total"]["value"]

                if number_results != 0:
                    all_results = parse_query_results(query_results)
                  
                else: 
                    all_results = question.question
                
            else:
                print("Language not allowed!")  
            return all_results
        
        for question in qset.qset_: 
            context = context_query(question)
           
            res = self._chain.invoke({"question": question.question, "context":context})
          
            matches = list(re.finditer(r'\([a-zA-Z]\)', res.content))
            
            model_answer = matches[-1].group() if matches else None
        
            question.model_answer = model_answer
            print(question.id, question.question)
            if question.answer != model_answer:
                print(f"Answer: {question.answer},  model answer: {model_answer} => incorrect \n")
            
            else: 
                print(f"Answer: {question.answer},  model answer: {model_answer} \n")

        return qset.stats_compute()
    

if __name__ == "__main__":
    mini_rag = MiniRAG(ELASTIC_API_KEY, UPSTAGE_API_KEY)
    prompt = """ 
         Please provide the most correct answer from the following context. Understand the entire full sentence for completeness.
        Q: Who likes to eat chips? Context says that Ha, Lam, Bun like to eat chips. 
        (A): Ha 
        (B): Lam
        (C): Bun
        (D): All of the above
        A: (D)

        If the answer is not present in the context, please  provide a reasonable guess of the answer.

        Also, once you find the answer in the context, ignore the remainder of the context.

        The answer must look like this always! 
        Answer: (<answer>)
        ---
        Question: {question}
        ---
        Context: {context}
        """
    mini_rag.prompt = prompt
    mini_rag.question_set = "test_samples_ewha.csv"
    outcome = mini_rag.retrieval(mini_rag.question_set)
    print(outcome)

