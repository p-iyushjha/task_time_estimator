from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    mean, std_dev, ci_low, ci_high = None, None, None, None
    
    if request.method == 'POST':
        try:
            estimates = request.form.getlist('task_estimates[]', type=float)
            if len(estimates) > 0:
                mean = np.mean(estimates)
                std_dev = np.std(estimates)
                ci_low, ci_high = mean - 1.96 * std_dev, mean + 1.96 * std_dev
        except Exception as e:
            return f"Error: {str(e)}"
    
    return render_template('index.html', mean=mean, std_dev=std_dev, ci_low=ci_low, ci_high=ci_high)

if __name__ == '__main__':
    app.run(debug=True)
