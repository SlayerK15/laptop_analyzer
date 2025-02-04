from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Path to the CSV file
CSV_FILE_PATH = "data.csv"

# Ensure the CSV file exists
if not os.path.exists(CSV_FILE_PATH):
    raise FileNotFoundError(f"CSV file not found at {CSV_FILE_PATH}")

# Load the CSV into a Pandas DataFrame
data = pd.read_csv(CSV_FILE_PATH)

@app.route('/')
def index():
    """Homepage displaying the CSV data."""
    return render_template('index.html', data=data.to_dict(orient='records'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    """Edit a specific row in the CSV."""
    if request.method == 'POST':
        # Update the data based on form input
        for key in request.form:
            data.loc[index, key] = request.form[key]
        # Save the updated data back to the CSV
        data.to_csv(CSV_FILE_PATH, index=False)
        if 'save_next' in request.form:
            next_index = index + 1
            if next_index < len(data):
                return redirect(url_for('edit', index=next_index))
            else:
                return redirect(url_for('index'))
        return redirect(url_for('index'))

    # Display the current data for the selected row
    row = data.loc[index].to_dict()
    return render_template('edit.html', index=index, row=row)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new row to the CSV."""
    if request.method == 'POST':
        # Add a new row based on form input
        new_row = {key: request.form[key] for key in request.form}
        data.loc[len(data)] = new_row
        # Save the updated data back to the CSV
        data.to_csv(CSV_FILE_PATH, index=False)
        return redirect(url_for('index'))

    # Display a form to add new data
    return render_template('add.html', columns=data.columns)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    """Delete a specific row in the CSV."""
    global data
    data = data.drop(index).reset_index(drop=True)
    # Save the updated data back to the CSV
    data.to_csv(CSV_FILE_PATH, index=False)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)