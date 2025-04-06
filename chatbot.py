import json
import random

# Load responses from JSON file
with open(r'C:/Users/Eshita/OneDrive/Desktop/main_ai_project/modules/data/responses.json') as f:
    responses = json.load(f)

def basic_chatbot(user_input):
    user_input = user_input.lower()

    # Check for greetings
    if any(greeting in user_input for greeting in ['hi', 'hello', 'hey', 'how_are_you']):
        return random.choice(responses['greetings'])  # Random greeting response

    # Check for career options
    elif "career" in user_input:
        return random.choice(responses['career_options'])  # Random career option response

    # Check for trending careers
    elif "trending" in user_input:
        # Fix: Pick a random category from the list of trending careers
        return random.choice(random.choice([
            responses['trending_careers'],
            responses['careers_with_high_salary'],
            responses['demand']
        ]))  # Random trending career response

    # Check for basic requirements for a career
    elif "requirements" in user_input:
        # Fix: Pick a random category for career requirements
        return random.choice(random.choice([
            responses['basic_requirements'],
            responses['requirements'],
            responses['essential_skills'],
            responses['skills']
        ]))  # Random basic requirement response

    # Check for languages required for a career
    elif "language" in user_input or "languages" in user_input:
        # Fix: Pick a random category for languages required
        return random.choice(random.choice([
            responses['languages_for_careers'],
            responses['programming_languages'],
            responses['technical_skills']
        ]))  # Random language response

    # Check for career advice
    elif "advice" in user_input:
        # Fix: Pick a random category for career advice
        return random.choice(random.choice([
            responses['career_advice'],
            responses['updations']
        ]))  # Random career advice response

    # Check for specific roles in CSE
    elif "roles" in user_input or "job" in user_input:
        # Fix: Pick a random category for specific roles in CSE
        return random.choice(random.choice([
            responses['specific_roles'],
            responses['roles']
        ]))  # Random specific role response
    
    # Check for creators or created
    elif "creators" in user_input or "created" in user_input:
        return random.choice(responses['creators'])  # Random creator or created response

    # Default response if no conditions match
    else:
        return "I'm just a basic bot! Try asking about your career."
