from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    # Get the current question ID from the session
    current_question_id = session.get("current_question_id")
    print(f"Current question ID: {current_question_id}")  # Debug statement

    # Check if it's the first interaction
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session["current_question_id"] = -1  # Indicate that the next interaction will be the first question
        session.save()
        print("Sent welcome message")  # Debug statement
        return bot_responses

    # If current_question_id is -1, this means we should ask the first question
    if current_question_id == -1:
        next_question, next_question_id = get_next_question(-1)
        bot_responses.append(next_question)
        session["current_question_id"] = next_question_id
        session.save()
        print("Asked first question")  # Debug statement
        return bot_responses

    # Record the current answer if it's not the first interaction
    success, error = record_current_answer(message, current_question_id, session)
    if not success:
        return [error]

    # Fetch the next question
    next_question, next_question_id = get_next_question(current_question_id)
    if next_question:
        bot_responses.append(next_question)
        session["current_question_id"] = next_question_id
        session.save()
        print("Asked next question")  # Debug statement
    else:
        # Generate the final response if there are no more questions
        final_response = generate_final_response(session)
        bot_responses.append(final_response)
        session["current_question_id"] = None  # Reset for a new quiz
        session["answers"] = {}  # Clear answers for a fresh start
        session.save()
        print("Quiz completed")  # Debug statement

    return bot_responses

def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to Django session.
    '''
    if current_question_id == -1:
        return True, ""  # No answer to record for the welcome message

    if current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID."

    # Store the answer in the session
    if "answers" not in session:
        session["answers"] = {}
    
    session["answers"][current_question_id] = answer
    session.save()
    print(f"Recorded answer for question ID {current_question_id}")  # Debug statement
    return True, ""

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_question_id = current_question_id + 1

    if next_question_id >= len(PYTHON_QUESTION_LIST):
        return None, None  # No more questions left

    question_data = PYTHON_QUESTION_LIST[next_question_id]
    next_question = question_data["question_text"]
    options = question_data.get("options", [])
    
    if options:
        options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
        next_question = f"{next_question}\n\nOptions:\n{options_text}"

    print(f"Fetched next question ID {next_question_id}")  # Debug statement
    return next_question, next_question_id

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    correct_answers = 0
    total_questions = len(PYTHON_QUESTION_LIST)
    
    for question_id, user_answer in session.get("answers", {}).items():
        correct_answer = PYTHON_QUESTION_LIST[int(question_id)]["answer"]
        if user_answer.strip().lower() == correct_answer.strip().lower():
            correct_answers += 1
    
    score = correct_answers / total_questions * 100
    return f"Quiz completed! You scored {score:.2f}% ({correct_answers} out of {total_questions} correct)."

# Example usage of the function
class MockSession(dict):
    def save(self):
        pass

session = MockSession()
print(generate_bot_responses("hi", session))  # Initial interaction should greet
print(generate_bot_responses("ok", session))  # Should ask the first question
