from fastapi import FastAPI
count = 0

app = FastAPI()
@app.post("/increment")
def increment() :
    global count 
    count += 1
    return count

@app.post("/decrement")
def decrement() : 
    global count
    count -= 1
    return count

@app.get("/")
def get_counter():
    global count
    return count