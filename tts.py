import pyttsx3

SPEECH_RATE = 225

engine = pyttsx3.init()
engine.setProperty('rate',SPEECH_RATE)


def say(t):
    global engine
    engine.say(t)
    engine.runAndWait()
