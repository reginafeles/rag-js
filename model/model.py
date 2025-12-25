import re
import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class RAG:
    def __init__(
        self,
        data_file: str = "data/dataset_js.csv",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        llm_model: str = "openai/gpt-oss-20b",
        persist_directory: str = "./chroma_db_js"
    ):
        self.data_file = data_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model_name = embedding_model_name
        self.llm_model = llm_model
        self.persist_directory = persist_directory
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY ERROR")

        self.chunks = self._load_and_split_text()

        self.embedding_function = HuggingFaceEmbeddings(model_name=self.embedding_model_name)

        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function
        )

        if len(self.vector_db.get()["ids"]) == 0:
            self._add_documents_to_db()

        self.llm = ChatGroq(
            model=self.llm_model,
            temperature=0.1,
            max_tokens=1024,
            api_key=api_key
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in JavaScript and web development. Answer ONLY based on the context provided."
                        "If you don't have the information for the ninth time, say, 'I don't know based on the information provided.'"),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])

    def _load_and_split_text(self) -> List[str]:
        with open(self.data_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        clean_text = re.sub(r"<[^>]+>", "", raw_text)
        clean_text = re.sub(r'""', '"', clean_text)
        clean_text = re.sub(r"\\", "", clean_text)
        blocks = [b.strip() for b in clean_text.split("\n\n") if len(b.strip()) > 30]
        full_text = "\n\n".join(blocks)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        return text_splitter.split_text(full_text)

    def _add_documents_to_db(self):
        self.vector_db.add_texts(self.chunks)
        print(f"Добавлено {len(self.chunks)} чанков в ChromaDB")

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        results = self.vector_db.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def generate_answer(self, question: str, k: int = 3) -> str:
        relevant_docs = self.retrieve(question, k=k)
        context = "\n\n".join(relevant_docs)
        messages = self.prompt_template.format_messages(context=context, question=question)
        response = self.llm.invoke(messages)
        return response.content.strip()

    def ask(self, question: str, k: int = 3) -> str:
        return self.generate_answer(question, k=k)

    def ask_with_history(self, messages: list[dict], last_question: str) -> str:
        relevant_docs = self.retrieve(last_question, k=3)
        context = "\n\n".join(relevant_docs)

        langchain_messages = [
            SystemMessage(
                content=(
                        "You are an expert in JavaScript and web development. "
                        "Answer ONLY based on the context provided below. "
                        "If the context does not contain the answer, say: "
                        "'I don't know based on the information provided.'\n\n"
                        "Context:\n" + context
                )
            )
        ]

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))

        response = self.llm.invoke(langchain_messages)
        return response.content.strip()

if __name__ == "__main__":
    rag = RAG()

    test_questions = [
        "What is the try catch construct?"
    ]

    for q in test_questions:
        print(f"\n +++++++++++????????????++++++++++++\n {q}")
        print(f"\n++++++++++++++++!!!!!!!!!!!!+++++++++++\n{rag.ask(q)}")
        print("-" * 80)