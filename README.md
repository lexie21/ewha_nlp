**Ewha Quiztaker**

Ewha Quiztaker is a lightweight quiz-answerer that runs on Upstage's Solar Minichat. It makes use of in-context learning and adaptation techniques such as prompt engineering and RAG to offset the model's still-limited builtin knowledge base and reasoning capabilities without resorting to any fine-tuning.

- Quick start:

To reproduce the main experiments, open `main.ipynb` and execute all cells. We have provided 2 sample test files including one on Ewha regulations but you can put in your own test file path, specify the context extraction method and whether you want to use the wikipedia api for English questions or not. Likewise, adapt the preceding codes for your own use case. Despite having experimented with different embedders before feeding them to Solar, we found that even with the correct context provided as is, the results are not very promising. 

In addition, we also provide a different implementation of the quiztaker to enhance the context retrieval's speed and relevance using the search engine powered by elastic search (free-trial cloud server expired before January so might not work at your clone time). In order to run this, you need to similarly provide the path to the test sample inside `main()`. You can also change the prompt to reflect your test cases and run:
```python
python search_enhanced/app.py
```





