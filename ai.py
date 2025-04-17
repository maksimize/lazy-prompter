
from ollama import chat
from ollama import ChatResponse
import json

class Ai:
    
    def get_questions(self, prompt: str):
        # return [
        #     {
        #         "question": "What is the capital of Germany?",
        #         "answers": ["Cairo", "Stockholm", "Kuala lumpur"]
        #     },
        #     {
        #         "question": "What is the capital of Egypt?",
        #         "answers": ["Cairo", "Kuala lumpur", "Stockholm"]
        #     }
        # ]
        response: ChatResponse = chat(model='lazy-prompter:10', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ])
        
        try:
            return json.loads(response.message.content)
        except json.JSONDecodeError:
            print(response.message.content)
            return json.loads({})
        
    
    def get_answer(self, prompt: str):
        # return "here is your answer"
        response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ])
        
        return response.message.content
        