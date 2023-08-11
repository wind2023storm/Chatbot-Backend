from flask import Blueprint, jsonify, request, send_file
from .models import Chat
from . import db
from collections import Counter
import json
import pinecone
import openai
import os
import uuid
from dotenv import load_dotenv
import datetime

PINECONE_API_KEY = ""
PINECONE_ENV = ""
OPENAI_API_KEY = ""
PINECONE_INDEX_NAME = ""
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
openai.openai_api_key = OPENAI_API_KEY

chat = Blueprint('chat', __name__)

@chat.route('/api/addchat', methods=['POST'])
def add_chat():
    temp = json.loads(request.form["data"])
    label = "New Chat"
    description = "This is new chatbot"
    model = "GPT-3.5-Turbo"
    conversation = "Hello friends! How can I help you today?"
    creativity = 0.3
    behavior = '''Hey there! I'm an AI assistant that has been trained by experts in the Specialized community to assist you in gearing up for your upcoming biking adventure. Whether you're a seasoned cyclist with countless miles under your belt or just starting out and exploring the thrilling world of cycling, I'm here to help you conquer your goals.

    You can count on me to provide personalized guidance that caters specifically to your needs and aspirations. No question is too big or too small, whether it's about route conditions, training techniques, or race preparation. I'm here to be your reliable source of valuable course insights, training tips, and unwavering support.

    Throughout our time together, I'll keep you updated with regular progress reports, suggest new workouts to keep you motivated, and celebrate every milestone you achieve. 

    Feel free to share how I can assist you today, and let's pedal our way towards success together!'''
    behaviormodel = "If there is relevant training data available, please utilize it to generate responses using the provided information. However, if no training data exists for the specific query, you may respond with \"I don't know.\""
    rider_level = temp['level']
    age = temp['age']
    gender = temp['gender']
    location = temp['location']
    print(rider_level)
    
    if chat := db.session.query(Chat).filter_by(label=label).first():
        return jsonify({
            'success': False,
            'code': 401,
            'message': 'A chart with the same name already exists. Please change the Name and description',
        })
    new_chat = Chat(label=label, description=description, model=model, 
                    conversation=conversation, creativity=creativity, behavior=behavior, behaviormodel=behaviormodel,      
                    rider_level = rider_level, age = age, gender = gender, location = location)
    db.session.add(new_chat)
    db.session.commit()

    response = {
        'success': True,
        'code': 200,
        'message': 'Your ChatBot created successfully!!!'
    }

    return jsonify(response)

@chat.route('/api/getchatbot', methods=['POST'])
def get_chatbot():
    chats = db.session.query(Chat).all()
    response = []
    if chats:
        for chat in chats:
            chat_data = {
                'id': chat.id,
                'label': chat.label,
                'description': chat.description,
                'model': chat.model,
                'conversation': chat.conversation,
                'creativity': chat.creativity,
                'behavior': chat.behavior,
                'behaviormodel': chat.behaviormodel,
                'uuid': chat.uuid,
            }
            response.append(chat_data)
    data = {
        'success': True,
        'code': 200,
        'data': response
    }

    return jsonify(data)

@chat.route('/api/getchat', methods=['POST'])
def get_chat():
    json_data = request.get_json()
    if json_data:
        uuid = request.json['id'];
        chat = db.session.query(Chat).filter_by(id=uuid).first()
        if chat is None:
            return jsonify({
                'success': False,
                'code': 404,
                'message': 'The Data not excited'
            })
        chat_data = {
          'id': chat.id,
          'label': chat.label,
          'description': chat.description,
          'model': chat.model,
          'conversation': chat.conversation,
          'creativity': chat.creativity,
          'behavior': chat.behavior,
          'behaviormodel': chat.behaviormodel,
          'uuid': chat.uuid,
        }
        data = {
          'success': True,
          'code': 200,
          'data': chat_data
        }
        return jsonify(data)
    else:
        return jsonify({"'success": False, "code": 404, "message": "No data"})
    # chats = db.session.query(Chat).all()
    # response = []
    # if chats:
    #     for chat in chats:
            
    #         response.append(chat_data)
    # return jsonify(data)