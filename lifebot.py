import audio

COMMANDS = [
    'log'
]

def next_command_index(current_index, command_data):
    next_command = len(command_data) - 1
    keys = list(command_data.keys())
    for key in keys:
        if command_data[key]['index'] > current_index and command_data[key]['index'] < next_command:
            next_command = command_data[key]['index']
    return next_command

isRunning = True

while(isRunning):
    command_data = {}
    transcript = audio.get_audio()
    individual_words = transcript.split(" ")
    for command in COMMANDS:
        if command in individual_words:
            command_data[command] = {'index': individual_words.index(command)}
    for command in range(len(command_data)):
        command['args'] = individual_words[command['index'] + 1:next_command_index(command['index'], command_data)]
    # if "robot" in individual_words:
    #     print("botro")
    # else:
    #     print(individual_words[0])

