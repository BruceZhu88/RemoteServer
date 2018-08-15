#!/usr/bin/env python
# @Time
# @Author   : Bruce.Zhu(Jialin)

# -------------------------------------------------------------------------
import subprocess
import app_config
import simplejson
import traceback
import PIL
from flask import Flask, render_template, request, redirect, jsonify, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
from src.common.Logger import Logger
from src.common.upload_file import uploadfile
from src.common.util import *

logger = Logger("main").logger()
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "eventlet"

app = Flask(__name__)
app.config.from_object(app_config)
bootstrap = Bootstrap(app)
socketio = SocketIO(app, async_mode=async_mode)
# socketio.async_mode
ALLOWED_EXTENSIONS = set(['txt', 'ini', 'gif', 'png', 'jpg', 'jpeg',
                          'bmp', 'rar', 'zip', '7zip', 'doc', 'docx',
                          'pdf', 'ppt'])
IGNORED_FILES = set(['.gitignore'])

PAGE_INFO = {"page": ""}

"""
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello1.html', name=name)
"""


# *********************************************************************************
#                        *Index*
# *********************************************************************************


@app.route('/')
def index():
    PAGE_INFO['page'] = 'home'
    global app_version
    return render_template('index.html', app_version=app_version)


@app.route('/remote_server')
def remote_server():
    PAGE_INFO['page'] = 'home'
    global app_version
    return render_template('RemoteServer.html', app_version=app_version)


@app.route('/remote_server/send_content', methods=['POST'])
def send_content():
    txt = request.form.to_dict().get("txt")
    print(format(str(datetime.today()), '*^60s'))
    print(txt)
    return jsonify({})

# *********************************************************************************
#                        *File server*
# *********************************************************************************


@app.route('/file_server')
def file_server():
    PAGE_INFO['page'] = 'file_server'
    return render_template('FileServer.html')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """
    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1
    return filename


def create_thumbnail(image):
    try:
        base_width = 80
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))
        return True
    except:
        print(traceback.format_exc())
        return False


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']
        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type
            if not allowed_file(files.filename):
                result = uploadfile(
                    name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
            else:
                # save file to disk
                uploaded_file_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)
                files.save(uploaded_file_path)
                # create thumbnail after saving
                if mime_type.startswith('image'):
                    create_thumbnail(filename)
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)
                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data/uploads/ directory
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(
            os.path.join(app.config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]
        file_display = []
        for f in files:
            size = os.path.getsize(os.path.join(
                app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())
        return simplejson.dumps({"files": file_display})
    return redirect(url_for('index'))


@app.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


# serve static files
@app.route("/thumbnail/<string:filename>", methods=['GET'])
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename=filename)


@app.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)


# *********************************************************************************
#                        *Android*
# *********************************************************************************


@app.route('/android')
def android():
    PAGE_INFO['page'] = 'android'
    return render_template('android.html')


@app.route('/android/adb', methods=['POST'])
def adb():
    cmd_id = request.form.to_dict().get("cmd")
    if cmd_id == 'screencap':
        cmd = '&&'.join([get_adb('shell', cmd_id).format('test.png'),
                         get_adb('system', 'file_pull').format('test.png', '1.png')])
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    try:
        code = p.stdout.read().decode("GB2312")
    except:
        code = p.stdout.read().decode("utf-8")
    print(code)
    return jsonify({})


if __name__ == '__main__':
    app_setting = load("./config/app.json")
    app_version = app_setting["version"]
    if not app.config["DEBUG"]:
        go_web_page("http://localhost:{}".format(app_setting["port"]))
        print(
            "Server started: http://localhost:{}".format(app_setting["port"]))
    socketio.run(app, host=app_setting["host"], port=app_setting["port"])
    # app.run(host='0.0.0.0', port=5000)
