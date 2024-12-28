#!/usr/bin/env python
import sys
import warnings
from screening.crew import Screening

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Define the Screening class with HR, Technical, and Manager rounds
class CrewScreening:

    def __init__(self):
        self.rounds = ['Technical', 'Manager', 'HR']
        self.candidate_status = {}
    
    def start_round(self, round_name, candidate_name):
        """
        Start a specific round for the candidate.
        """
        if round_name == 'Technical':
            print(f"Starting Technical round for {candidate_name}")
            self.technical_round(candidate_name)
        elif round_name == 'Manager':
            print(f"Starting Manager round for {candidate_name}")
            self.manager_round(candidate_name)
        elif round_name == 'HR':
            print(f"Starting HR round for {candidate_name}")
            self.hr_round(candidate_name)

    def technical_round(self, candidate_name):
        """
        Simulate the Technical round.
        """
        print(f"Evaluating technical skills for {candidate_name}...")
        # Simulate technical evaluation (e.g., coding problem, algorithm task)
        feedback = "Pass" if self.evaluate_technical(candidate_name) else "Fail"
        self.candidate_status[candidate_name] = {'Technical': feedback}
        print(f"Technical Round Feedback: {feedback}")
    
    def evaluate_technical(self, candidate_name):
        # Placeholder for technical evaluation logic (e.g., coding test)
        # Returning True means pass, False means fail
        return True  # Assume candidate passes technical round for simplicity

    def manager_round(self, candidate_name):
        """
        Simulate the Manager round.
        """
        print(f"Evaluating managerial skills for {candidate_name}...")
        # Simulate manager evaluation (e.g., problem-solving, leadership)
        feedback = "Pass" if self.evaluate_manager(candidate_name) else "Fail"
        self.candidate_status[candidate_name]['Manager'] = feedback
        print(f"Manager Round Feedback: {feedback}")
    
    def evaluate_manager(self, candidate_name):
        # Placeholder for managerial evaluation logic
        return True  # Assume candidate passes manager round for simplicity

    def hr_round(self, candidate_name):
        """
        Simulate the HR round.
        """
        print(f"Evaluating cultural and behavioral fit for {candidate_name}...")
        # Simulate HR evaluation (e.g., behavioral questions, salary expectations)
        feedback = "Pass" if self.evaluate_hr(candidate_name) else "Fail"
        self.candidate_status[candidate_name]['HR'] = feedback
        print(f"HR Round Feedback: {feedback}")
    
    def evaluate_hr(self, candidate_name):
        # Placeholder for HR evaluation logic
        return True  # Assume candidate passes HR round for simplicity

    def get_candidate_status(self, candidate_name):
        """
        Retrieve the overall status of the candidate.
        """
        return self.candidate_status.get(candidate_name, "No status available")

    def crew(self):
        """
        Initialize the screening process for multiple candidates and rounds.
        """
        # Sample candidates for screening
        candidates = ['John Doe', 'Jane Smith', 'Alice Johnson']
        
        for candidate in candidates:
            print(f"\nStarting screening for {candidate}")
            for round_name in self.rounds:
                self.start_round(round_name, candidate)

        # Output the final status for all candidates
        for candidate in candidates:
            print(f"\nFinal Status for {candidate}: {self.get_candidate_status(candidate)}")

    def kickoff(self, inputs):
        """
        Kickoff the screening process with given inputs.
        """
        print(f"Screening started for topic: {inputs['topic']}")
        self.crew()

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs'
    }
    CrewScreening().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Screening().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Screening().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Screening().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


# Running the screening process
if __name__ == "__main__":
    run()
