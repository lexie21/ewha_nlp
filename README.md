**Ewha Quiztaker**

Ewha Quiztaker is a quiz-answering machine that runs on Upstage's Solar Minichat. It makes use of in-context learning and adaptation techniques such as prompt engineering and RAG to offset the model's still-limited builtin knowledge base and reasoning capabilities without any fine-tuning.

- Quick start:

To reproduce the main experiments, open `main.ipynb` and execute all cells.

In addition, we also provide a different implementation of the quiztaker to enhance the context retrieval's speed and relevance using the search engine powered by elastic search (free-trial cloud server expired before January so might not work at your clone time). In order to run this, you need to provide the path to the test sample inside `main()`. You can also change the prompt to reflect your test cases and run:
```python
python app.py
```





