from flask import Flask

app = Flask(__name__)

import polaroid.edit
import polaroid.forms
import polaroid.register
    