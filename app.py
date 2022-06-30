
from datetime import datetime, timedelta
from enum import unique
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Date, String, Integer, Boolean, DateTime, Float, ForeignKey, true
from flask_restful import Api, Resource
from flask_cors import CORS
from sqlalchemy.orm import backref
import os
import socket
import json
from functools import wraps
import uuid

app = Flask(__name__)
CORS(app)

cors = CORS(app, resource={
    r"/*" : {
        "origins" : "*"
    }
})

config = json.load(open('config.json'))
api = Api(app)

app.config['SECRET_KEY'] = 'pv_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.curdir , 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + config['DBuser'] +':'+ config['DBpass'] +'@database/pn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Note(db.Model):
    __tablename__ = 'Note'
    id = Column(Integer, primary_key=True)
    noteBody = Column(String(1000))
    link = Column(String(100), nullable=False, unique=True)
    expire = Column(DateTime, nullable=False)
    isExpired = Column(Boolean, nullable=False)



@app.route('/create', methods=['POST'])
def createNote():
    data = request.get_json()
    note = Note(noteBody=data['noteBody'], link=str(uuid.uuid4().hex), expire=datetime.now() + timedelta(hours=int(config['expireTime'])) , isExpired=False)
    db.session.add(note)
    db.session.commit()
    return jsonify({"link": "http://localhost:4200/requestRead/" + note.link})

@app.route('/requestRead/<note_link>', methods=['GET'])
def requestRead(note_link):
    linkId = note_link
    note = Note.query.filter_by(link=linkId).first()
    try:
        note = db.session.query(Note).filter(Note.link == linkId).first()
        if note == None:
            resp = make_response(jsonify({'message': 'Bad request.', 'status': 0}), 200)
            return resp
        if note.isExpired:
            resp = make_response(jsonify({'message': 'Note is expired.', 'status':1}), 200)
            return resp
        else:
            resp = make_response(jsonify({'message': 'Note is available.', 'status':2}), 200)
            return resp
            
    except:
        resp = make_response(jsonify({'message': 'Bad request.'}), 400)
        return resp
    

@app.route('/read/<note_link>', methods=['PUT'])
def readNote(note_link):
    linkId = note_link
    try:
        note = db.session.query(Note).filter(Note.link == linkId).first()
        if note == None:
            resp = make_response(jsonify({'message': 'Bad request.'}), 400)
            return resp
        else:
            if note.isExpired:
                resp = make_response(jsonify({'message': 'Note is expired.' ,'status':1}), 400)
                return resp
            else:
                resp = make_response(jsonify({'noteBody': note.noteBody, 'status':2}), 200)
                note.isExpired = True
                db.session.commit()
                return resp
    except Exception as _:
        resp = make_response(jsonify({'message': 'There is an internal issue.'}), 500)
        return resp



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=config['port'])


