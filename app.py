from flask import Flask, render_template, request
import numpy as np
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    plot_json = None
    error = None

    if request.method == "POST":
        tasks_input = request.form.get("tasks")
        num_simulations = request.form.get("num_simulations")
        try:
            num_simulations = int(num_simulations) if num_simulations else 10000
        except ValueError:
            num_simulations = 10000

        if tasks_input:
            # Each line should be: optimistic, most likely, pessimistic
            lines = tasks_input.strip().splitlines()
            tasks = []
            for line in lines:
                try:
                    # Convert comma-separated values to floats
                    parts = [float(x.strip()) for x in line.split(",")]
                    if len(parts) != 3:
                        continue
                    O, M, P = parts
                    # Ensure valid order: O < M < P
                    if not (O < M < P):
                        continue
                    tasks.append((O, M, P))
                except Exception:
                    continue

            if not tasks:
                error = "No valid tasks found. Ensure each line is formatted as: optimistic, most likely, pessimistic (with O < M < P)."
            else:
                # Monte Carlo simulation: For each simulation, sample each task's duration and sum them.
                total_durations = np.zeros(num_simulations)
                for task in tasks:
                    O, M, P = task
                    # Calculate parameters for Beta-PERT:
                    # alpha = 1 + 4*(M - O)/(P - O)
                    # beta  = 1 + 4*(P - M)/(P - O)
                    alpha = 1 + 4 * (M - O) / (P - O)
                    beta = 1 + 4 * (P - M) / (P - O)
                    # Draw samples from Beta(alpha, beta) and scale to [O, P]
                    samples = np.random.beta(alpha, beta, size=num_simulations)
                    task_durations = O + (P - O) * samples
                    total_durations += task_durations

                # Compute overall metrics
                mean_duration = np.mean(total_durations)
                median_duration = np.median(total_durations)
                std_duration = np.std(total_durations)
                ci_lower = np.percentile(total_durations, 2.5)
                ci_upper = np.percentile(total_durations, 97.5)

                results = {
                    "mean_duration": mean_duration,
                    "median_duration": median_duration,
                    "std_duration": std_duration,
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper,
                    "num_tasks": len(tasks)
                }

                # Create Plotly histogram JSON data
                plot_data = {
                    "data": [{
                        "x": total_durations.tolist(),
                        "type": "histogram",
                        "nbinsx": 30
                    }],
                    "layout": {
                        "title": "Monte Carlo Simulation: Project Duration Distribution",
                        "xaxis": {"title": "Project Duration (hours)"},
                        "yaxis": {"title": "Frequency"}
                    }
                }
                plot_json = json.dumps(plot_data)
        else:
            error = "Please enter task estimates."

    return render_template("index.html", results=results, plot_json=plot_json, error=error)

if __name__ == "__main__":
    app.run(debug=True)
