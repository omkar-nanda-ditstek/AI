#!/usr/bin/env python3

from custom_trainer import CustomInterviewTrainer

def add_your_training_data():
    trainer = CustomInterviewTrainer()
    
    # Add your custom questions and responses
    training_examples = [
        {
            "skill": "Node.js",
            "question": "I see you have Node.js experience. Can you walk me through a specific Node.js project you built?",
            "keywords": ["api", "backend", "server"],
            "response": "That's a solid backend approach! How did you handle authentication and security?"
        },
        {
            "skill": "React",
            "question": "Tell me about your React development experience. What kind of applications have you built?",
            "keywords": ["component", "state", "hooks"],
            "response": "Great! Can you explain how you structured your React components?"
        },
        {
            "skill": "IoT",
            "question": "IoT projects are fascinating! Can you describe the IoT systems you've worked on?",
            "keywords": ["sensor", "device", "communication"],
            "response": "That sounds complex! How did you handle device communication and data processing?"
        },
        {
            "skill": "JavaScript",
            "question": "What JavaScript frameworks and libraries do you prefer working with?",
            "keywords": ["async", "promise", "callback"],
            "response": "Excellent! How do you handle asynchronous operations in your JavaScript code?"
        }
    ]
    
    # Add all training examples
    for example in training_examples:
        trainer.add_training_example(
            skill=example["skill"],
            question=example["question"],
            keywords=example["keywords"],
            response=example["response"]
        )
    
    print("✅ Training data added successfully!")
    print("Your custom questions will now be used in interviews.")

if __name__ == "__main__":
    add_your_training_data()