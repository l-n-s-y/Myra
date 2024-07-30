

def read_file(f): return open(f,"r").read()

#def write_file(f,d): return open(f,"w").write(d)

# TRAINING WHEELS
out_dir = "testing_output\\"
def write_file(f,*d): 
    print(f,d)
    return open(out_dir+f,"w").write(" ".join(d))



