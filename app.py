from flask import Flask, render_template, request
import numpy as np
import json
from datetime import datetime
import logging

app = Flask(__name__)
app.debug = True

# Set up logging for error debugging
logging.basicConfig(level=logging.DEBUG)

# Inject the current time into templates (for the footer)
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

def parse_tasks(task_input):
    """
    Parse each line of the textarea input.
    Expected format per line:
    ID, Task Name, Optimistic, Most Likely, Pessimistic, Dependencies (optional; use semicolons if multiple)

    Example lines:
      1, Task A, 2, 4, 8, 
      2, Task B, 1, 2, 3, 1
      3, Task C, 3, 5, 10, 1;2
    """
    tasks = []
    lines = task_input.strip().splitlines()
    for line in lines:
        parts = line.split(',')
        if len(parts) < 5:
            continue  # Skip invalid lines
        try:
            task_id = parts[0].strip()
            name = parts[1].strip()
            optimistic = float(parts[2].strip())
            most_likely = float(parts[3].strip())
            pessimistic = float(parts[4].strip())
            # Handle dependencies (optional)
            if len(parts) >= 6:
                dep_str = parts[5].strip()
                dependencies = [d.strip() for d in dep_str.split(';') if d.strip()] if dep_str else []
            else:
                dependencies = []
            tasks.append({
                'id': task_id,
                'name': name,
                'optimistic': optimistic,
                'most_likely': most_likely,
                'pessimistic': pessimistic,
                'dependencies': dependencies
            })
        except Exception as e:
            app.logger.error(f"Error parsing line: {line}. Error: {e}")
            continue
    return tasks

def topological_sort(tasks):
    """
    Perform a topological sort of tasks based on their dependencies.
    Uses Kahn's algorithm. Raises an exception if a cycle is detected.
    """
    graph = {}
    indegree = {}
    task_map = {}
    for task in tasks:
        task_map[task['id']] = task
        indegree[task['id']] = 0
        graph[task['id']] = []
    for task in tasks:
        for dep in task['dependencies']:
            if dep in graph:  # Only consider dependencies that exist
                graph[dep].append(task['id'])
                indegree[task['id']] += 1
    queue = [tid for tid in indegree if indegree[tid] == 0]
    sorted_tasks = []
    while queue:
        current = queue.pop(0)
        sorted_tasks.append(task_map[current])
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    if len(sorted_tasks) != len(tasks):
        raise Exception("Cycle detected in task dependencies.")
    return sorted_tasks

def sample_beta_pert(O, M, P, size=1):
    """
    Sample from a Beta-PERT distribution given optimistic (O),
    most likely (M), and pessimistic (P) estimates.
    """
    if P - O == 0:
        return np.full(size, M)
    alpha = 1 + 4 * (M - O) / (P - O)
    beta_param = 1 + 4 * (P - M) / (P - O)
    samples = np.random.beta(alpha, beta_param, size=size)
    return O + (P - O) * samples

def calculate_sprint_points(mean_duration):
    """
    Calculate sprint points based on mean duration.
    Assumes 1 sprint point is equal to 3 hours.
    """
    sprint_point_value = 3  # 1 sprint point = 3 hours
    return round(mean_duration / sprint_point_value)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    plot_json = None
    error = None
    if request.method == "POST":
        tasks_input = request.form.get("tasks")
        num_simulations = request.form.get("num_simulations")
        velocity_factor = request.form.get("velocity_factor")
        try:
            num_simulations = int(num_simulations) if num_simulations else 10000
        except ValueError:
            num_simulations = 10000
        try:
            velocity_factor = float(velocity_factor) if velocity_factor else 1.0
        except ValueError:
            velocity_factor = 1.0

        if tasks_input:
            tasks = parse_tasks(tasks_input)
            if not tasks:
                error = ("No valid tasks found. Please ensure each line follows the format: "
                         "ID, Task Name, Optimistic, Most Likely, Pessimistic, Dependencies (optional).")
            else:
                try:
                    sorted_tasks = topological_sort(tasks)
                except Exception as e:
                    error = str(e)
                    return render_template("index.html", error=error)
                
                simulation_results = np.zeros(num_simulations)
                try:
                    for i in range(num_simulations):
                        finish_times = {}
                        # Process tasks in topological order so that dependencies are respected.
                        for task in sorted_tasks:
                            duration_sample = sample_beta_pert(
                                task['optimistic'], task['most_likely'], task['pessimistic'], size=1
                            )[0]
                            # Apply velocity adjustment factor (e.g., if >1, tasks take longer)
                            duration_sample *= velocity_factor
                            # Determine start time from dependencies (if any)
                            if task['dependencies']:
                                start_time = max([finish_times.get(dep, 0) for dep in task['dependencies']])
                            else:
                                start_time = 0
                            finish_times[task['id']] = start_time + duration_sample
                        project_duration = max(finish_times.values())
                        simulation_results[i] = project_duration
                except Exception as e:
                    app.logger.error(f"Error during simulation: {e}")
                    error = f"Error during simulation: {e}"
                    return render_template("index.html", error=error)

                mean_duration = np.mean(simulation_results)
                sprint_points = calculate_sprint_points(mean_duration)
                median_duration = np.median(simulation_results)
                std_duration = np.std(simulation_results)
                ci_lower = np.percentile(simulation_results, 2.5)
                ci_upper = np.percentile(simulation_results, 97.5)
                results = {
                    "num_tasks": len(tasks),
                    "mean_duration": mean_duration,
                    "sprint_points": sprint_points,
                    "median_duration": median_duration,
                    "std_duration": std_duration,
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper
                }
                plot_data = {
                    "data": [{
                        "x": simulation_results.tolist(),
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
