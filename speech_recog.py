import speech_recognition as sr

def microphone_transcribe():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        #text = r.recognize_sphinx(audio)
        try:
            text = r.recognize_google(audio)

        except sr.UnknownValueError:
            print("[SPEECH] Google could not recognise speech")
            return ""
        except sr.RequestError as e:
            print("[SPEECH] Google request failed. {0}".format(e))
            print(e)
            return r.recognize_sphinx(audio)
        return text
