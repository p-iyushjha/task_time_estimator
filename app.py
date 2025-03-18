from flask import Flask, request, render_template
import numpy as np

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        try:
            # Get user inputs
            median_time = float(request.form.get("median_time"))
            sigma = float(request.form.get("sigma"))
            
            # Calculate mu from the median (median = exp(mu))
            mu = np.log(median_time)
            
            # Predicted Mean: exp(mu + sigma^2/2)
            mean_time = np.exp(mu + sigma**2 / 2)
            
            # Standard deviation: sqrt((exp(sigma^2)-1) * exp(2*mu + sigma^2))
            std_dev = np.sqrt((np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2))
            
            # 95% Confidence Interval
            lower_bound = np.exp(mu - 1.96 * sigma)
            upper_bound = np.exp(mu + 1.96 * sigma)
            
            result = {
                "median_time": median_time,
                "sigma": sigma,
                "mean_time": mean_time,
                "std_dev": std_dev,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            }
        except Exception as e:
            result["error"] = "Invalid input. Please ensure you enter valid numbers."
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
