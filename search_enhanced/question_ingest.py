from dataclasses import dataclass, field
import chardet
import pandas as pd
from typing import Optional, ClassVar
from langdetect import detect
import numpy as np

@dataclass
class Quest:
    _counter: ClassVar[int] = 0
    id: int = field(init=False)
    set_id: int
    question: str 
    answer: str 
    lang: str 
    name: str
    model_answer: Optional[str] = None
    no_documents: Optional[int] = None
    category: Optional[str] = None
    prompt: Optional[str] = None

    def __post_init__(self):
        self.id = Quest._counter 
        Quest._counter += 1

class Question:
    counter = 0

    def __init__(self, prompt, data_path,coverage=1.0):
        self._id = Question.counter 
        Question.counter += 1
        new_qset = self.questionize(data_path) 
        self._qset = new_qset
        self._coverage = coverage
        self._prompt = prompt

    @property 
    def qset_(self):
        return self._qset
    
    @property 
    def coverage_(self):
        return self._coverage 
    
    @property 
    def prompt_(self):
        return self._prompt

    def stats_compute(self):
        holder = sum([question.model_answer != None for question in self._qset])
        if holder == len(self._qset):
            
            # update stats, store in db
            stats_result = {}
            stats_result["id"] = self._id
            # assume successful parsing
            stats_result["prompt"] = self._prompt
            stats_result["accuracy"] = sum([question.answer == question.model_answer for question in self._qset])/len(self._qset)
            if sum([question.category!= None for question in self._qset]) == len(self._qset):
                unique_c, counts_c = np.unique([question.category for question in self._qset], return_counts=True)
                stats_result["categories"] = dict(zip(unique_c, counts_c))
            unique_n, counts_n = np.unique([question.name for question in self._qset], return_counts=True)
            stats_result["names"] = dict(zip(unique_n, counts_n))
            return stats_result
        else: 
            print("Model hasn't answered yet!")
            return

    def questionize(self,data_path):
   
        def read_question(data_path):
                
            def encoding_check(filename):
                with open(filename, 'rb') as rawdata:
                    encoding = chardet.detect(rawdata.read(100000))
                return encoding["encoding"]
            
            encoding = encoding_check(data_path)
            try:  
                data = pd.read_csv(data_path,encoding=encoding)
            except Exception as e:
                try:
                    data = pd.read_excel(data_path)
                except Exception as ex:
                    print(f"Failed to load the data. CSV Error: {e}, Excel Error: {ex}")
                    raise

            questions = data["prompts"]
            answers = data["answers"]
            return questions, answers

        questions, answers = read_question(data_path)
     
        questionized = []

        for question, answer in zip(questions, answers):
       
            if isinstance(question,str):
                lang = detect(question)
                name = "ewha" if lang == "ko" else "mmlu"
                quest = Quest(self._id, question,answer,lang,name)
                questionized.append(quest)
                
        return questionized
