import random

class Expert:
    def __init__(self, name, specialty):
        self.name = name
        self.specialty = specialty

    def generate_response(self, question, previous_responses=None):
        base_response = f"[{self.name} - {self.specialty}] Відповідь на питання: '{question}'"
        # Імітація врахування попередніх думок
        if previous_responses:
            base_response += " (з урахуванням думок інших експертів)"
        return base_response

def create_experts():
    specialties = ['економіст', 'соціолог', 'технічний експерт', 'етик', 'аналітик']
    return [Expert(f'Експерт {i+1}', random.choice(specialties)) for i in range(5)]
