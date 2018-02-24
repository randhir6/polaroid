from polaroid import app
from flask import Flask, render_template, request, send_file, session, flash
import os
from wand.image import Image
import ctypes
from wand.api import library
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(APP_ROOT, 'images/')
app.config['SECRET_KEY'] = "lundbc"

library.MagickPolaroidImage.argtypes = (ctypes.c_void_p,  # MagickWand *
                                        ctypes.c_void_p,  # DrawingWand *
                                        ctypes.c_double)  # Double

library.MagickSetImageBorderColor.argtypes = (ctypes.c_void_p,  # MagickWand *
                                              ctypes.c_void_p)  # PixelWand *


def polaroid(wand, context, angle=0.0):
    if not isinstance(wand, Image):
        raise TypeError('wand must be instance of Image, not ' + repr(wand))
    if not isinstance(context, Drawing):
        raise TypeError('context must be instance of Drawing, not ' +
                        repr(context))
    library.MagickPolaroidImage(wand.wand,
                                context.resource,
                                angle)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/samples')
def samples():
    return render_template('samples.html')


@app.route('/upload', methods=['POST'])
def upload():

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist('file'):
        name = file.filename
        destination = '/'.join([target, name])
        file.save(destination)
        with Image(filename=destination) as image:
            with Color('white') as white:
                library.MagickSetImageBorderColor(image.wand, white.resource)
            with Drawing() as annotation:
                polaroid(image, annotation)
            image.save(filename='pika.jpg')
            session['file_name'] = 'pika.jpg'
    return render_template('download.html')


@app.route('/download', methods=['GET'])
def download():
    file_name = session.get('file_name', None)
    file_data = '/'.join([APP_ROOT, file_name])
    return send_file(file_data, attachment_filename='editedfile.jpg',
                     as_attachment=True)
