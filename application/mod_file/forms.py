from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField

class FileForm(FlaskForm):
    file = FileField('file')
    submit = SubmitField('submit')