import wikipediaapi
import chardet
import yake
import os

WIKI_NAME = os.getenv("WIKI_NAME")
wiki_client = wikipediaapi.Wikipedia(WIKI_NAME, language="en")    
kw_extractor = yake.KeywordExtractor()

def encoding_check(filename):
    with open(filename, 'rb') as rawdata:
        encoding = chardet.detect(rawdata.read(100000))
    return encoding["encoding"]


def keying(query):
    keywords = kw_extractor.extract_keywords(query)
    keyword = [el for el in keywords if len(el[0].split(" "))>=2][:3]
    return keyword

def parse_keyword(keywords,client=wiki_client):
    context_dict = {}
    for kw in keywords:
        if client.page(kw):
            page = client.page(kw)
            context_dict[kw] = page.summary 
    return '\n'.join([cont for cont in context_dict.values()])

def return_query(query):
    resp = keying(query)
    context = parse_keyword(resp)
    return context

# if __name__ == "__main__":
#     filename = "test_sample_MMLU_hard.csv"
#     questions = pd.read_csv(filename,encoding=encoding_check(filename))["prompts"]
#     for i,quest in enumerate(questions):
#         print(i)
#         print(keying(quest.split("\n")[0]),"\n")
