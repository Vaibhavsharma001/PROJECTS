import speech_recognition as sr
import webbrowser
import pyttsx3 


recognizer = sr.Recognizer()
engine= pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()
    
def processcommand(c):
    if "open google" in c.lower():
        webbrowser.open('https://google.com')
        
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")

    elif "open github" in c.lower():
        webbrowser.open("https://github.com")
    
if __name__ == "__main__":
    speak("initializing ultron.....")
    
    while True:
        r = sr.Recognizer()      
        
        try:
            with sr.Microphone() as source:
                print("Listening.....")
                audio = r.listen(source,timeout=2,phrase_time_limit=1)
                print("recognizing...")  
            word = r.recognize_google(audio)
            if(word.lower()=="ultron"):
                speak("ya")
                
                with sr.Microphone() as source:
                    print("Ultron Active")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    
                    processcommand(command)
                    
        except sr.WaitTimeoutError:
            print("Listening timed out")     
        except sr.UnknownValueError:
            print("i dont understand")
        except sr.RequestError as e:
            print("ultron error; {0}".format(e))

        

      

    

