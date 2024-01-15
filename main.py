from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from wtforms.validators import DataRequired, URL
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FLASK_KEY'
# app.config['SECRET_KEY']=  os.environ.get('FLASK_KEY')
Bootstrap5(app)

# CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///cafes.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'

db = SQLAlchemy()
db.init_app(app)

TODAY = datetime.today().strftime("%Y-%m-%d")



class ToDo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(250), nullable=False)
    duedate = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(250), nullable=False)
    create_date = db.Column(db.String(250),  nullable=False)


class TaskForm(FlaskForm):
    task = StringField('Cafe name', validators=[DataRequired()])
    duedate = DateField('Due date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField("Status", choices=["Completed", "Active", "Has Due Date"], validators=[DataRequired()])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()

FILTER = "Active"

@app.route("/", methods=["GET", "POST"])
def home():
    # result = db.session.execute(db.select(ToDo).where(ToDo.status == "Active"))
    if request.method == 'POST':
        print(request.form.get('todo_status'))
    result = db.session.execute(db.select(ToDo))
    todos = result.scalars().all()
    return render_template("index.html",  all_todos=todos, today=TODAY)


@app.route('/add', methods=["GET", "POST"])
def add_task():
    # form = CafeForm()
    if request.method == 'POST':
        if request.form.get('add_task_button'):
            result = db.session.execute(db.select(ToDo).where(ToDo.task == request.form["task"]))
            task_result = result.scalar()
            if task_result:
                # User already exists
                flash("You've already added this task before, add a new one instead!")
                return redirect(url_for('add_task'))
            # try:
            #     new_task = ToDo(
            #         task=request.form["task"],
            #         duedate=datetime.strptime(request.form["duedate"],"%Y-%m-%d"),
            #         status="Active",
            #         create_date = datetime.strptime(TODAY,"%Y-%m-%d"),)
            # except ValueError as ve:
            new_task = ToDo(
                    task=request.form["task"],
                    duedate=request.form["duedate"],
                    status="Active",
                    create_date=datetime.strptime(TODAY, "%Y-%m-%d"),)


            db.session.add(new_task)
            db.session.commit()

    return redirect(url_for('home'))
    # return render_template('index.html')


@app.route('/todos')
def todos(filter, sort):
    # result = db.session.execute(db.select(ToDo))
    # todos = result.scalars().all()
    # print(cafe_result)
    if filter == "all":
        result = db.session.execute(db.select(ToDo))
        todos = result.scalars().all()
        if sort =="Added date":
            result = db.session.execute(db.select(ToDo).order_by(ToDo.create_date))
            todos = result.scalars().all()
        else:
            result = db.session.execute(db.select(ToDo).order_by(ToDo.duedate))
            todos = result.scalars().all()
    if filter == "Active":
        result = db.session.execute(db.select(ToDo).where(ToDo.status == "Active"))
        todos = result.scalars().all()
        if sort =="Added date":
            result = db.session.execute(db.select(ToDo).where(ToDo.status == "Active").order_by(ToDo.create_date))
            todos = result.scalars().all()
        else:
            result = db.session.execute(db.select(ToDo).where(ToDo.status == "Active").order_by(ToDo.duedate))
            todos = result.scalars().all()
    if filter == "Complete":
        result = db.session.execute(db.select(ToDo).where(ToDo.status == "Complete"))
        todos = result.scalars().all()
        if sort =="Added date":
            result = db.session.execute(db.select(ToDo).where(ToDo.status == "Complete").order_by(ToDo.create_date))
            todos = result.scalars().all()
        else:
            result = db.session.execute(db.select(ToDo).where(ToDo.status == "Complete").order_by(ToDo.duedate))
            todos = result.scalars().all()
    if filter == "Has no due date":
        result = db.session.execute(db.select(ToDo).where(ToDo.duedate == ''))
        todos = result.scalars().all()

    return render_template('index.html', all_todos=todos)




@app.route('/checked',methods=["GET", "POST"])
def checked():
    if request.method == 'POST':
        completed_todos = request.form.getlist('task_check_input')
        # uncpleted_todos = request.form.getlist('task_check_input')
    for com_todo in completed_todos:
        todo = db.get_or_404(ToDo, com_todo)
        todo.status = "Complete"
        db.session.commit()
    # result = db.session.execute(db.select(ToDo))
    # todos = result.scalars().all()
    # print(cafe_result)
    return redirect(url_for("home"))

@app.route('/filter',methods=["GET", "POST"])
def filtered():
    if request.method == 'POST':
        filter = request.form.get('todo_filter')
        sort = request.form.get('todo_sort')
    return todos(filter,sort)




@app.route("/delete/<int:todo_id>")
def delete_todo(todo_id):
    todo_to_delete = db.get_or_404(ToDo, todo_id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/edit-todo/<int:todo_id>", methods=["GET", "POST"])
def edit_todo(todo_id):
    todo_to_update = db.get_or_404(ToDo, todo_id)
    # if request.method == 'POST':
    print(todo_id)
    if request.method == 'POST':
        new_to_update = ToDo(
            task=request.form["task"],
            duedate=request.form["duedate"],
            status="Active",
            create_date=TODAY,)
        print(request.form.get('update_task_button'))
        if request.form.get('update_task_button'):
            todo_to_update.task = new_to_update.task
            todo_to_update.duedate = new_to_update.duedate
            todo_to_update.status = new_to_update.status
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html")





if __name__ == '__main__':
    app.run(debug=True, port=5002)
