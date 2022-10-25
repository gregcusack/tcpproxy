from flask import Flask, render_template
from functools import wraps
import os
from Count import Count


app = Flask(__name__)

def increment_req_count(func):
    @wraps(func)
    def incr_func(**kwargs):
        count.incr_count()
        return func(**kwargs)
    return incr_func

@app.route('/get')
@increment_req_count
def run_get():
    # count.incr_count()
    return {"what is up!?!": count.get_count()}

@app.route('/mirror/<t0>/<t1>')
@increment_req_count
def run_mirror(t0, t1):
    # count.incr_count()
    return {"received": {"t0": t0, "t1": t1}, "count": count.get_count() }

@app.route('/')
@increment_req_count
def home():
    # count.incr_count()
    ret_string = "what up fam: " + str(count.get_count()) + "\n"
    return ret_string


if __name__ == "__main__":
    count = Count()
    print("hey")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)