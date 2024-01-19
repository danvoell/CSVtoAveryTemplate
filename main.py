from flask import Flask, request, send_file
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os

app = Flask(__name__)

# Function to generate Avery labels for Avery 5160
def generate_avery_labels(addresses, file_path):
    # Avery 5160 label dimensions and settings
    label_width = 2.625 * 72  # in points
    label_height = 1.0 * 72  # in points
    labels_per_row = 3
    labels_per_column = 10
    margin_left = 0.1875 * 72  # in points
    margin_top = 0.5 * 72  # in points
    spacing_x = 0.125 * 72  # in points
    spacing_y = 0  # in points

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    for index, row in addresses.iterrows():
        column_index = index % labels_per_row
        row_index = index // labels_per_row

        if row_index >= labels_per_column:  # Start a new page if the current one is full
            c.showPage()
            row_index = 0

        x = margin_left + (label_width + spacing_x) * column_index
        y = height - margin_top - label_height - (label_height + spacing_y) * row_index

        c.drawString(x + 4, y + label_height - 12, row['Name'])
        c.drawString(x + 4, y + label_height - 24, row['Address Line 1'])
        c.drawString(x + 4, y + label_height - 36, row['Address Line 2'])

    c.save()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            df = pd.read_csv(file)

            # Create a temporary file
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, 'labels.pdf')
            generate_avery_labels(df, temp_file)

            return send_file(temp_file, as_attachment=True, download_name='labels.pdf', mimetype='application/pdf')

    return '''
    <!doctype html>
    <title>Upload CSV for Avery Labels</title>
    <h1>Upload CSV File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
