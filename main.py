from flask import Flask, render_template, make_response, redirect, url_for, flash, request
from flask_api import status
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from pathlib import Path
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
    return redirect(url_for('partition', sample_idx=0, part_idx=0))
    # return render_template('index.html', form=form)

def redirect_url(default='home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

@app.route('/submit/<int:part_idx>/<int:sample_idx>', methods=['POST'])
def submit(part_idx=None,sample_idx=None):
    folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], "data_partitions")
    if not os.path.exists(folder_path):
        flash(f"folder path {folder_path} does not exist", category='danger')
        return redirect(redirect_url())
    if not os.path.isdir(folder_path):
        flash(f"folder path {folder_path} is not a folder", category='danger')
        return redirect(redirect_url())
    partitions = []
    for path in os.scandir(folder_path):
        if path.is_dir() and os.listdir(path):
            partitions.append(path)
    partitions.sort(key=lambda partition: partition.name)
    if part_idx < 0 or part_idx >= len(partitions):
        flash(f"partition index {part_idx} out of bounds", category='danger')
        return redirect(redirect_url())
    partition_path = partitions[part_idx];
    if not os.path.exists(partition_path):
        flash(f"partition path {partition_path} does not exist", category='danger')
        return redirect(redirect_url())
    if not os.path.isdir(partition_path):
        flash(f"partition path {partition_path} is not a folder", category='danger')
        return redirect(redirect_url())
    samples = []
    for path in os.scandir(partition_path):
        if path.is_dir() and os.listdir(path):
            samples.append(path)
    if sample_idx < 0 or sample_idx >= len(samples):
        flash(f"sample index {sample_idx} out of bounds", category='danger')
        return redirect(redirect_url())
    sample_path = samples[sample_idx]
    if not os.path.exists(sample_path):
        flash(f"sample path {sample_path} does not exist", category='danger')
        return redirect(redirect_url())
    if not os.path.isdir(sample_path):
        flash(f"sample path {sample_path} is not a folder", category='danger')
        return redirect(redirect_url())
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
        flash(f"no unique sample file {names} found", category='danger')
        return redirect(redirect_url())
    try:
        with open(file_path.path, 'r') as file:
            _ = file.read()
    except FileNotFoundError:
        flash(f"file {file_path.path} is unreadable", category='danger')
        return redirect(redirect_url())
    vul_folder_path = os.path.join(sample_path, "injections")
    missing = False
    if not os.path.exists(vul_folder_path):
        missing = True
        flash(f"vulnerability path {vul_folder_path} does not exist", category='warning')
    if missing:
        Path(vul_folder_path).mkdir(exist_ok=True)
        flash(f"vulnerability path {vul_folder_path} created", category='success')
    if not os.path.isdir(vul_folder_path):
        flash(f"vulnerability path {vul_folder_path} is not a folder", category='danger')
        return redirect(redirect_url())
    injection_count = 0
    for path in os.scandir(vul_folder_path):
        if not path.is_dir() and '_vul_' in path.name:
            injection_count += 1
    vuln_type = request.form.get('vuln_type')
    indication_path = os.path.join(vul_folder_path, f"no_vul_injectable.txt")
    injection_path = os.path.join(vul_folder_path, f"{vuln_type}_vul_{injection_count}.c")
    if os.path.exists(injection_path):
        flash(f"injection path {injection_path} already exists", category='warning')
        return redirect(redirect_url())
    try:
        if vuln_type == 'None':
            with open(indication_path, 'w') as file:
                print('No vulnerability found', file=file, end='')
                flash(f'recorded "No vulnerability" for sample', category='success')
        else:
            with open(injection_path, 'w') as file:
                print(f'{vuln_type}', file=file)
                vuln_program = request.form.get('vuln_program')
                print(f"{vuln_program}", file=file)
                flash(f'submitted vulnerable program to {vul_folder_path}', category='success')
    except FileNotFoundError:
        flash(f'file {injection_path} not found', category='warning')
        flash(f'directory {vul_folder_path} exists: {os.path.exists(vul_folder_path)}', category='info')
        return redirect(redirect_url())
    return redirect(redirect_url())

@app.route('/partition/<int(signed=True):part_idx>/sample/<int(signed=True):sample_idx>', methods=['GET'])
def partition(part_idx=None, sample_idx=None):
    folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], "data_partitions")
    if not os.path.exists(folder_path):
        flash(f"folder path {folder_path} does not exist", category='danger')
        return redirect(redirect_url())
    if not os.path.isdir(folder_path):
        flash(f"folder path {folder_path} is not a folder", category='danger')
        return redirect(redirect_url())
    partitions = []
    for path in os.scandir(folder_path):
        if path.is_dir() and os.listdir(path):
            partitions.append(path)
    partitions.sort(key=lambda partition: partition.name)
    if part_idx < 0 or part_idx >= len(partitions):
        flash(f"partition index {part_idx} out of bounds", category='danger')
        return redirect(redirect_url())
    partition_path = partitions[part_idx];
    if not os.path.exists(partition_path):
        flash(f"partition path {partition_path} does not exist", category='danger')
        return redirect(redirect_url())
    if not os.path.isdir(partition_path):
        flash(f"partition path {partition_path} is not a folder", category='danger')
        return redirect(redirect_url())
    samples = []
    for path in os.scandir(partition_path):
        if path.is_dir() and os.listdir(path):
            samples.append(path)
    if sample_idx < 0 or sample_idx >= len(samples):
        flash(f"sample index {sample_idx} out of bounds", category='danger')
        return redirect(redirect_url())
    sample_path = samples[sample_idx]
    if not os.path.exists(sample_path):
        flash(f"sample path {sample_path} does not exist", category='danger')
        return redirect(redirect_url())
    if not os.path.isdir(sample_path):
        flash(f"sample path {sample_path} is not a folder", category='danger')
        return redirect(redirect_url())
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
    try:
        with open(file_path.path, 'r') as file:
            file_content = file.read()
            enabled=True
    except FileNotFoundError:
        file_content = "File read failed. Vulnerability analysis skipped."
        enabled=False
    prev_partition = part_idx - 1
    next_partition = part_idx + 1
    prev_sample = sample_idx - 1
    next_sample = sample_idx + 1
    return render_template('label.html', sample_text=file_content, prev_partition=prev_partition,
        next_partition=next_partition, prev_sample=prev_sample, next_sample=next_sample,
        curr_partition=part_idx, curr_sample=sample_idx, enabled=enabled, path=file_path.path)

if __name__ == '__main__':
    app.run(debug=True)