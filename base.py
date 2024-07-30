import subprocess,threading,os,sys
import multiprocessing
from tts import say
from speech_recog import microphone_transcribe

# constants
LLAMA_COMMAND = ["ollama.exe","run","llama3"]

# global vars
running = True
current_prompt = ""
prompt_latch = False

timeout_period = 5

def load_prompt(file):
    with open(file) as f:
        return f.read()

MYRA_PROMPT = load_prompt("myra.txt")

history = []

name_retained = False
name_retention_timeout = 60 # seconds til she forgets you're talking to her
def reset_name_retained():
    global name_retained
    name_retained = False


def read_stdout(fd,tts=False):
    global history
    lines = []
    for line in iter(fd.readline,b""):
        line = line.decode()
        lines.append(line)
        if line == "\n": continue
        history.append("AI] "+line)
        print(line)
        fd.flush()
    #if len(lines) > 5: return
    if not tts: return
    [say(line) for line in lines]

global_prompt = ""
def main(voice_control,use_tts=False):
    print("== Myra .1 ==\n(Give command or 'exit')\n")

    global name_retained

    try:
        while True:
            llama_proc = subprocess.Popen(LLAMA_COMMAND,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,bufsize=0)
            llama_proc.stdin.write(MYRA_PROMPT.encode()+b"\n")
            llama_proc.stdin.write("".join(history).encode()+b"\n")
    
            p = multiprocessing.Process(target=read_stdout,args=[llama_proc.stdout,use_tts])
            p.daemon = True
            t = threading.Timer(name_retention_timeout,reset_name_retained)

            #prompt = input("* ")
            prompt = ""
            if voice_control:
                print("Listening...")
                prompt = microphone_transcribe()
                print("HEARD: ",prompt)
            else:
                prompt = input("* ")

            if prompt == "": continue
            if ("mira" not in prompt.lower() and "myr" not in prompt.lower()):
                if not name_retained and voice_control: continue
            else:
                name_retained = True
                t.start()

            if llama_proc.poll():
                print("[OLLAMA] ERROR: Process died X(")
                return False

            if prompt.lower() == "exit":
                t.cancel()
                llama_proc.terminate()
                llama_proc.wait(timeout=0.2)
                return False
                

            history.append(prompt)

            print(f"sending ['{prompt}']...")
            prompt+='\n' # terminate

            #outs,errs = llama_proc.communicate(input=prompt.encode(),timeout=5)

            #print(outs.decode())
            llama_proc.stdin.write(prompt.encode())



            llama_proc.stdin.close()

            p.run()


            print("send done.")
    except Exception as e:
        print(e)

    #t.join()

if __name__ == "__main__":
    voice_control = "-v" in sys.argv
    use_tts = "-t" in sys.argv

    while True:
        if not main(voice_control,use_tts): break

    print("[MYRA] Done.")
