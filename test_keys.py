from dotenv import load_dotenv
import os

load_dotenv()

news = os.getenv('NEWS_API_KEY')
groq = os.getenv('GROQ_API_KEY')

print('NewsAPI Key loaded:', 'YES' if news else 'NO')
print('Groq Key loaded:', 'YES' if groq else 'NO')