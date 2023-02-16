from flask import Flask, render_template, make_response, redirect, url_for
from flask_api import status
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config[''] = ''

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    # form = UploadFileForm()
    # if form.validate_on_submit():
        # file = form.file.data # First grab the file
        # file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
    return redirect(url_for('partition', vul_idx=0, part_idx=0))
    # return render_template('index.html', form=form)

@app.route('/partition/<int:part_idx>/sample/<int:vul_idx>', methods=['GET'])
def partition(vul_idx=None, part_idx=None):
    folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], "data_partitions")
    if not os.path.exists(folder_path):
        return make_response(f"folder path {folder_path} does not exist", status.HTTP_404_NOT_FOUND)
    if not os.path.isdir(folder_path):
        return make_response(f"folder path {folder_path} is not a folder", status.HTTP_404_NOT_FOUND)
    partitions = []
    for path in os.scandir(folder_path):
        if path.is_dir() and os.listdir(path):
            partitions.append(path)
    partitions.sort(key=lambda partition: partition.name)
    if part_idx < 0 or part_idx >= len(partitions):
        return make_response(f"partition index {part_idx} out of bounds", status.HTTP_404_NOT_FOUND)
    partition_path = partitions[part_idx];
    if not os.path.exists(partition_path):
        return make_response(f"partition path {partition_path} does not exist", status.HTTP_404_NOT_FOUND)
    if not os.path.isdir(partition_path):
        return make_response(f"partition path {partition_path} is not a folder", status.HTTP_404_NOT_FOUND)
    samples = []
    for path in os.scandir(partition_path):
        if path.is_dir() and os.listdir(path):
            samples.append(path)
    if vul_idx < 0 or vul_idx >= len(samples):
        return make_response(f"sample index {vul_idx} out of bounds", status.HTTP_404_NOT_FOUND)
    sample_path = samples[vul_idx]
    if not os.path.exists(sample_path):
        return make_response(f"Sample path {sample_path} does not exist", status.HTTP_404_NOT_FOUND)
    if not os.path.isdir(sample_path):
        return make_response(f"Sample path {sample_path} is not a folder", status.HTTP_404_NOT_FOUND)
    sample_name = sample_path.name + "_nonvul.c"
    file_path = None
    names = []
    for path in os.scandir(sample_path):
        if not path.is_dir():
            names.append(path.name)
        if not path.is_dir() and path.name == (sample_name):
            if file_path is not None:
                file_path = None
                break
            file_path = path
    if file_path is None:
        return make_response(f"no unique sample file {names} found", status.HTTP_404_NOT_FOUND)
    with open(file_path, 'r') as file:
        file_content = file.read()
    return render_template('label.html', sample_text=file_content)

if __name__ == '__main__':
    app.run(debug=True)