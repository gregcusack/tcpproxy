from flask import Flask, render_template
import os

class Count:
    def __init__(self):
        self.count = 0
    
    def incr_count(self):
        self.count += 1

    def get_count(self):
        return self.count

app = Flask(__name__)

@app.route('/')
def home():
    count.incr_count()
    ret_string = "what up fam: " + str(count.get_count()) + "\n"
    return ret_string


if __name__ == "__main__":
    count = Count()
    print("hey")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)