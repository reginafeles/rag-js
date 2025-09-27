import # библиотеки для работы с LLM, например, Groq
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает API ключ из .env файла

# Простейший набор документов. Задача 1: сделать из этого *.csv и или *.txt и загружать из папки data
documents = [
    "Машинное обучение - это метод искусственного интеллекта.",
    "Python популярный язык для Data Science.",
    "Flask - легковесный фреймворк для веб-приложений."
]

# Делаем документы .txt в папке data
os.mkdir("data")

with open ("data/ML.txt", 'w') as f:
    f.write(documents[0])

with open ("data/Python.txt", 'w') as f:
    f.write(documents[1])

with open ("data/Flask.txt", 'w') as f:
    f.write(documents[2])

def simple_search(query):
    """Простой поиск по документам"""
    results = []
    for doc in documents:
        if query.lower() in doc.lower():
            results.append(doc)
    return results

def ask_question():
    question = input("Введите запрос:") # Задача 2: получать запрос из консоли (получили)
    
    # 1. Поиск по документам
    relevant_docs = simple_search(question)
    context = "\n".join(relevant_docs)
    
    # 2. Генерация ответа с контекстом
    prompt = f"""
    Контекст: {context}
    
    Вопрос: {question}
    
    Ответь на вопрос на основе контекста. Если в контексте нет информации, скажи "Не знаю".
    """
    
    try:
        # Задача 3: заменить запрос к OpenAI на запрос к Groq; внимательно изучаем доку
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv('OPENAI_API_KEY') # Здесь меняем на ключик Groq
        )
        answer = response.choices[0].message.content
    except:
        answer = "Ошибка подключения к AI"
    
    return answer
    
if __name__ == '__main__':
    ask_question()
