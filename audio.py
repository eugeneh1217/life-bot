import speech_recognition as sr
import time
from array import array
import pyaudio
import wave

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024
BUFFER_TIME=2
MIN_VOLUME=1000
FILE_NAME="audio.wav"
frames=[]

def start_record(stream):
    data=stream.read(CHUNK)
    data_chunk=array('h',data)
    vol=max(data_chunk)
    if(vol>=MIN_VOLUME):
        print("something said")
        frames.append(data)
        return True
    return False

#recording prerequisites
def get_audio():
    audio=pyaudio.PyAudio()
    stream=audio.open(format=FORMAT,channels=CHANNELS, 
                      rate=RATE,
                      input=True,
                      frames_per_buffer=CHUNK)
    isRecording = False
    while(True):
        if start_record(stream) == True:
            isRecording = True
        elif isRecording:
            print("nothing")
            for i in range(0,int(RATE/CHUNK*BUFFER_TIME)):
                data=stream.read(CHUNK)
                data_chunk=array('h',data)
                vol=max(data_chunk)
                if(vol>=MIN_VOLUME):
                    print("something said")
                    frames.append(data)
            break

    #end of recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    #writing to file
    wavfile=wave.open(FILE_NAME,'wb')
    wavfile.setnchannels(CHANNELS)
    wavfile.setsampwidth(audio.get_sample_size(FORMAT))
    wavfile.setframerate(RATE)
    wavfile.writeframes(b''.join(frames))#append frames recorded to file
    wavfile.close()

    r = sr.Recognizer()
    recorded_audio = sr.AudioFile('audio.wav')
    with recorded_audio as source:
        audio = r.record(source)
        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception: " + str(e))
            return

    return said