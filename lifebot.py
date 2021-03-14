import audio

isRunning = True

while(isRunning):
    transcript = audio.get_audio()
    individual_words = transcript.split(" ")
    if "robot" in individual_words:
        print("botro")
    else:
        print(individual_words[0])

