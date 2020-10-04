from flask import Blueprint, request, render_template, flash, \
    g, session, redirect, url_for, jsonify, abort, url_for, make_response
from werkzeug.security import check_password_hash
from application.mod_module.models import Module, ClassRoom
from application.mod_auth.models import User
from application.mod_auth.controllers import get_user_object, get_fullname
from application.mod_notification.controllers import set_notification, NotificationType
from application import db, app
import flask_login
from .forms import *


# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_module = Blueprint('mod_module', __name__, url_prefix='/module',\
     template_folder='templates/')



@mod_module.route('/create/', methods=['POST'])
@flask_login.login_required
def create():
    form = CreateModuleForm(meta={'csrf_token':False})
    username = str(flask_login.current_user)
    try:
        if form.validate_on_submit():
            m = Module(form.name.data,
            username,
            form.session.data,
            form.description.data,
            form.code.data)
            c = ClassRoom(m.module_id, username)
            db.session.add(c)
            db.session.add(m)
            db.session.commit()
            flash("Module Created Successfully")
            return redirect(f'/module/view/{m.module_id}/')
        else:
            flash("Submitted Form was Invalid")
            return redirect(f'/module/view/{m.module_id}/')

    except Exception as ex:
        flash("Something went wrong, please try again")
        return redirect(url_for('mod_module.index'))


@mod_module.route('/view/<module_id>/', methods=['GET'])
@flask_login.login_required
def view(module_id):
    m = Module.query.filter_by(module_id=module_id).first()

    if m is None:
        return redirect(url_for('not_found'))
    else:
        return render_template('module/index.html',
            module_id = module_id,
            module_name = m.module_name,
            module_tutor_id = m.module_tutor_id,
            session = m.session,
            description = m.description,
            module_code = m.module_code,
            created_on = m.created_on
        )


@mod_module.route('/<module_id>/add/', methods=['POST'])
@flask_login.login_required
def add_student(module_id):
    user_making_the_addition = \
        get_user_object(str(flask_login.current_user))
    user_to_be_added = \
        get_user_object(request.form['username'])

    module = get_module_object(module_id)


    if (user_to_be_added is not None):
        # module leader cannot add himself to the module
        # since he owns the module
        if module.module_tutor_id == user_to_be_added.username:
            return 'Error encountered'


        if user_making_the_addition is user_to_be_added:
            # When Students joins a class by himself
            if ClassRoom.query.filter_by(module_id=module_id, username=user_to_be_added.username).first():
                c = ClassRoom(module.module_id, user_to_be_added.username)
                db.session.add(c)
                db.session.commit()
                return jsonify(status='Success')
            else:
                return "This student is already in this class"
        elif user_making_the_addition.username == module.module_tutor_id:
            # Tutor is adding student to a classroom
            # send invite that appears in the notifcation 
            # section of the student where they can accept 

            # TODO: call Notification system function to create
            # 'Add module' notification in student's db
            if set_notification(user_making_the_addition.username, \
                user_to_be_added.username, NotificationType.JoinModule):
                return jsonify("Notification will be sent to the student")
            else:
                return jsonify("Something Went Wrong")

    else:
        return jsonify(msg='Error encountered')



@mod_module.route('/<module_id>/members/', methods=['GET'])
@flask_login.login_required
def get_members(module_id):
    m = get_module_object(module_id)
    c = get_classroom_object(module_id)
    return jsonify(
        module_tutor = m.module_tutor_id,
        others = c
    )


def get_modules():
    # get modules this user is registered in
    c = ClassRoom.query.filter_by(\
        member_username=str(flask_login.current_user))

    # get modules created by this user
    modules = []
    for i in c:
        modules.append(Module.query.filter_by(module_id=i.module_id).first())
    return modules


@mod_module.route('/join_module/', methods=['GET'])
@flask_login.login_required
def join_module():
    # Generate ajax list
    username = str(flask_login.current_user)
    if request.args['action'] == "get_mod":
        text = request.args['data'].lower()
        if text.strip() == '':
            return jsonify(data=[])
        m = Module.query.all()
        s = []
        for i in m:
            if (text in (i.module_id).lower()) or (text in (i.module_name).lower()):
                s.append((i.module_name, i.module_id, get_fullname(i.module_tutor_id)))
        return jsonify(data = s)

    if request.args['action'] == "join":
        module_id = request.args['module_id']
        try:
            if ClassRoom.query.filter_by(\
                module_id=module_id, member_username = username).first() is None:
                c = ClassRoom(module_id, username)
                db.session.add(c)
                db.session.commit()
                return jsonify(msg="Success")
            else:
                return jsonify(msg="Error Occured")
        except Exception:
            return jsonify(msg="Error Occured")

    




def get_module_object(module_id):
    return Module.query.filter_by(module_id=module_id).first()

def get_classroom_object(module_id):
    return ClassRoom.query.filter_by(module_id=module_id)

def is_student_in_classroom(module_id, username):
    c = ClassRoom.query.filter_by(\
        module_id=module_id, member_username=username).first()
    if c is None:
        return False
    else:
        return True
