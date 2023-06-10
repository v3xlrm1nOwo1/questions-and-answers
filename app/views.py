import os
from app import app
from app.models import *
from sqlalchemy import text, orm, func
from flask import render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app.config['SECRET_KEY'] = os.urandom(24)


def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        user = Users.query.filter(Users.username==user).first()
        return user


@app.route('/')
def home():
    user = get_current_user()
    
    askers = orm.aliased(Users)
    experts = orm.aliased(Users)
    questions = db.session.query(Questions, askers, experts).join(askers, Questions.question_by_id==askers.id).join(experts, Questions.answer_by_id==experts.id).filter(Questions.answer.isnot(None)).all()

    # sql = f'''SELECT Questions.id, Questions.question, askers.name, experts.name
    #             FROM Questions
    #             JOIN Users as askers ON Questions.question_by_id = askers.id
    #             JOIN Users as experts ON Questions.answer_by_id = experts.id
    #             WHERE Questions.answer IS NOT NULL'''
                
    # with db.engine.begin() as conn:
    #     for question in conn.execute(text(sql)):
    #         questions.append({'question_id': int(question[0]), 'question': question[1], 'askers': question[2], 'experts': question[3]})
        
    data = {
        'user': user,
        'questions': questions
        }
    
    return render_template('home.html', data=data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    data = {
        'user': user,
        }
    
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        
        check_user = Users.query.filter(Users.username==username).first()
        
        if check_user:
            data['error'] = 'There was an issue on your register ): username alryead exists'
            return render_template('register.html', data=data)
        
        hash_password = generate_password_hash(password, method='sha256') 
        
        new_user = Users(username=username, name=name, password=hash_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user'] = username
            return redirect(url_for('home'))
        except:
            return "There was an issue on your register ):, check the username"
    
    elif request.method == 'GET':
        return render_template('register.html', data=data)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = error = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
                
        user = Users.query.filter(Users.username==username).first()
        
        if user:
            check_password = check_password_hash(user.password, password)
            if check_password:
                session['user'] = user.username
                return redirect(url_for('home'))
            else:
                error =  "There was an issue on your login ): password the incorrect"
                user = None
        
        elif not user:
            error = "There was an issue on your login ): username the incorrect"       
    data = {
    'user': user,
    'error': error
    }
    return  render_template('login.html', data=data)


@app.route('/logout')
def logout():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/users')
def users():
    user = get_current_user()
    users = Users.query.all()
    if not user:
        return redirect(url_for('login'))
    elif not user.admin:
        return redirect(url_for('home'))
    
    data = {
        'user': user,
        'users': users
    }
    return render_template('users.html', data=data)


@app.route('/promote/<int:user_id>')
def promote(user_id):
    user = get_current_user()
    
    if not user:
        return redirect(url_for('login'))
    elif not user.admin:
        return redirect(url_for('home'))
    
    user = Users.query.get_or_404(user_id)
    
    if not user.expert:
        value = True
    else:
        value = False
        
    user.expert = value
    try:
        db.session.commit()
        return redirect(url_for('users'))
    except:
        return "There was an issue ):"


@app.route('/answer/<int:question_id>', methods=['GET', 'POST'])
def answer(question_id):
    user = get_current_user()
    
    if not user:
        return redirect(url_for('login'))
    
    elif not user.expert:
        return redirect(url_for('home'))
    
    question = Questions.query.get_or_404(question_id)
    
    if request.method == 'POST':

        question.answer = request.form['answer']
        try:
            db.session.commit()
            return redirect(url_for('unanswered'))
        except:
            return "There was an issue on your answer ):"
    
    elif request.method == 'GET':
        user = get_current_user()
        data = {
            'question': question,
            'user': user
        }
        return render_template('answer.html', data=data)
    

@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    elif not user.expert:
        return redirect(url_for('home'))
    
    questions = db.session.query(Questions, Users).join(Users, Questions.question_by_id==Users.id).filter(Questions.answer_by_id==user.id, Questions.answer.is_(None)).all()
    
    data = {
        'user': user,
        'questions': questions
    }
    return  render_template('unanswered.html', data=data)


@app.route('/question/<int:question_id>')
def question(question_id):
    user = get_current_user()
    
    askers = orm.aliased(Users)
    experts = orm.aliased(Users)
    sengle_question = db.session.query(Questions, askers, experts).join(askers, Questions.question_by_id==askers.id).join(experts, Questions.answer_by_id==experts.id).filter(Questions.id==question_id).first()

    data = {
        'user': user,
        'sengle_question': sengle_question
    }
    return render_template('question.html', data=data)


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        question = request.form['question']
        expert_id = request.form['expert']

        new_question = Questions(question=question, answer=None, question_by_id=user.id, answer_by_id=expert_id)
    
        try:
            db.session.add(new_question)
            db.session.commit()        
            return redirect(url_for('ask'))
        except:
            return "There was an issue on your Question ):"
    
    elif request.method == 'GET':
        experts = Users.query.filter(Users.expert==True).all()
        
        data = {
            'user': user,
            'experts': experts
        }
        return render_template('ask.html', data=data)

