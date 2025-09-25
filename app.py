from groq import Groq
import os
import glob
from dotenv import load_dotenv

load_dotenv()  # Загружает API ключ из .env

def load_documents(data_dir: str = "data"):
    docs = []

    for path in glob.glob(os.path.join(data_dir, "**", "*.txt"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    docs.append(line)

    return docs

def simple_search(query, docs):
    q = (query or "").lower()
    return [doc for doc in docs if q in doc.lower()]

def ask_question():
    question = input("Введи запрос:\n").strip() # Задача 2: получать запрос из консоли 

    documents = load_documents("data")

    # 1. Поиск по документам
    relevant_docs = simple_search(question, documents)
    context = "\n".join(relevant_docs)
    
    # 2. Генерация ответа с контекстом
    prompt = f"""
    Контекст: {context}
    
    Вопрос: {question}
    
    Ответь на вопрос на основе контекста. Если в контексте нет информации, скажи "Не знаю".
    """
    
    try:
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )

        answer = chat_completion.choices[0].message.content
    except:
        answer = "Ошибка подключения к AI"
    
    print(answer)
    return answer

if __name__ == '__main__':
    ask_question()
