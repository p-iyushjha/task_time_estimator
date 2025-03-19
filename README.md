# Master Agile Estimator with Dependencies

## Overview
This project is a web-based project estimation tool built using Python and Flask. It uses advanced statistical models, including Beta-PERT distributions and Monte Carlo simulation, to forecast overall project durations based on multiple tasks, task dependencies, and agile adjustment factors. Designed for agile teams working on complex projects (such as software for robots and swarm drones), the tool aims to provide more accurate and data-driven time estimates.

## Features

### Beta-PERT Model
- Uses optimistic, most likely, and pessimistic estimates for each task.

### Monte Carlo Simulation
- Runs multiple iterations (default 10,000) to generate a probability distribution for the total project duration.

### Task Dependency Management
- Incorporates dependencies between tasks using topological sorting, ensuring that tasks are scheduled in the correct order.

### Agile Velocity Adjustment
- Applies a velocity adjustment factor to account for historical team performance and agile metrics.

### Interactive Visualization
- Displays an interactive histogram (using Plotly) of simulated project durations.

### Responsive UI
- The user interface is built using Bootstrap for a clean, modern, and responsive design.

## Folder Structure
```
/task_time_estimator
├── app.py                  // Main Flask application code
├── requirements.txt        // Python dependencies (Flask, numpy, gunicorn)
├── README.docx             // This README file (if saved as a Word document)
└── /templates
    └── index.html          // HTML template for the web user interface
```

## Installation and Setup

### Prerequisites
- Python 3.x (download from https://www.python.org/)
- pip (Python package manager, usually comes with Python)
- (Optional) A virtual environment (recommended for dependency management)

### Clone or Download the Repository
```
git clone https://github.com/your-username/task_time_estimator.git
```

### Create a Virtual Environment (Optional)

#### On Windows:
```
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Run the Application Locally
```
python app.py
```

Open your browser and visit:
```
http://127.0.0.1:5000
```

## Usage

### Input Format
Enter each task on a new line in the following format:
```
ID, Task Name, Optimistic, Most Likely, Pessimistic, Dependencies
```

- Dependencies are optional. For multiple dependencies, separate them with semicolons.

#### Example Input:
```
1, Task A, 2, 4, 8,
2, Task B, 1, 2, 3, 1
3, Task C, 3, 5, 10, 1;2
```

### Simulation Parameters
- **Number of Simulations:** Enter the desired number of simulation iterations (default is 10,000).
- **Velocity Adjustment Factor:** Enter a factor (default is 1.0). A factor greater than 1.0 increases task durations, accounting for lower team velocity.

### Results
The application computes and displays:
- Total number of tasks
- Mean project duration
- Median project duration
- Standard deviation
- 95% confidence interval for project duration

An interactive histogram of the simulation results is also shown.

## Deployment on Render

### Push Code to GitHub
Ensure all files are committed to your GitHub repository.

### Set Up a Web Service on Render
1. Log in to Render.
2. Create a new Web Service and connect your GitHub repository.

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
gunicorn app:app
```

Render will build and deploy your app automatically.

## Troubleshooting

### Internal Server Errors
- Check terminal logs (or Render logs) for error details.
- Ensure your input format is correct.

### Dependency Issues
- Verify that your `requirements.txt` file includes:
```
Flask
numpy
gunicorn
```

## Further Customizations
You can adjust simulation parameters or extend the application (e.g., integrating more agile metrics or dependency models) based on your team's needs.

## Contact
For questions, suggestions, or issues, please contact:
- Piyush Jha
- piyush.jha@newspace.co.in

## License
This project is licensed under the Apache License.

