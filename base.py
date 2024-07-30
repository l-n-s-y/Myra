import subprocess,threading,os,sys
import multiprocessing
from tts import say
from speech_recog import microphone_transcribe

import util_extensions

# constants
LLAMA_COMMAND = ["ollama.exe","run","llama3"]

HISTORY_PROMPT_PREFIX = "AI]"
UTIL_EXTENSION_PREFIX = "UTIL]"

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


def run_extension(command,*a):
    # This should never be run with privilege. Think of the children
    if command not in util_extensions.__dir__():
        print("Unsupported command")
        return
    args = ",".join(a)
    print(args)
    command_string = f"util_extensions.{command}({args})"
    print(command_string)
    return eval(command_string) # This is a terrible idea


name_retained = False
name_retention_timeout = 60 # seconds til she forgets you're talking to her
def reset_name_retained():
    global name_retained
    name_retained = False


def read_stdout(fd,tts=False):
    global history
    lines = []
    for line in iter(fd.readline,b""):
        line = line.decode().lstrip()
        lines.append(line)
        if line == "\n": continue
        history.append(HISTORY_PROMPT_PREFIX+" "+line)
        fd.flush()
        print(line)
        
        if line.startswith(UTIL_EXTENSION_PREFIX):
            argv = line[5:].split(" ")
            func = argv[0]
            args = ",".join(["'"+arg.replace('"','')+"'" for arg in argv[1:]]).replace('\n','')
            print(f"[EXT] Running: {func}({args})")
            ext_out = str(run_extension(func,args))
            print(ext_out)
            lines.append([l for l in ext_out.split("\n")])



    #if len(lines) > 5: return # disable speech on large outputs
    if not tts: return
    [say(line) for line in lines]

global_prompt = ""
def main(voice_control,use_tts=False):
    print("== Myra .2 ==\n(Give command or 'exit')\n")

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
