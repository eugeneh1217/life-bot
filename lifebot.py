import audio
from datetime import datetime
from datastax_api import DataStaxApi, LogKey
COMMANDS = [
    'logs'
]

def find_command(command, words):
    # return index of command
    return words.index(command)

isRunning = True

db = DataStaxApi()

current_index = 0
while(isRunning):
    command_data = {}
    transcript = audio.get_audio()
    individual_words = transcript.split(" ")
    individual_words = individual_words[current_index:]
    print(individual_words)
    for command in COMMANDS:
        command_index = find_command(command, individual_words)
    args = individual_words[command_index + 1:]
    if individual_words[command_index] == 'logs':
        if args[0] == 'read':
            
            message = db.get('logs', primary_key=LogKey('lougene', datetime.today().strftime('%m/%d/%y')))['content']
            print(f"log_0: {message}")
        elif args[0] == 'new':
            message = ' '.join(args[1:])
            db.insert('logs', {'owner': 'lougene', 'date': datetime.today().strftime('%m/%d/%y'), 'content': message})
            print("Log recorded")
    current_index = len(individual_words)

