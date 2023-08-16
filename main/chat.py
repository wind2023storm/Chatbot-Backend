from flask import Blueprint, jsonify, request, send_file, url_for
from flask import render_template
from .models import Chat, Message
from . import db
from collections import Counter
import json
import pinecone
import openai
import os
import uuid
from dotenv import load_dotenv
import datetime
from gmplot import gmplot
import gpxpy
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import base64
from selenium import webdriver
import time

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
PINECONE_NAMESPACE = os.getenv('PINECONE_NAMESPACE')
GOOGLE_MAP_API_KEY = os.getenv('GOOGLE_MAP_API_KEY')

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
openai.openai_api_key = OPENAI_API_KEY

chat = Blueprint('chat', __name__)
coord_list = []
options = webdriver.ChromeOptions()
options.add_argument("--headless") # to run in background
driver = webdriver.Chrome(options=options)

@chat.route('/')
def hello_world():
   return 'Hello World'

@chat.route('/api/upload', methods=['POST'])
def upload_gpx():
    load_dotenv()
    file = request.files.get('file', None)
    if not file:
        return {"success": False}
    filename = secure_filename(file.filename)
    file.save(filename)
    gpx_file = open(filename, "rb")
    # # Parse the file
    gpx = gpxpy.parse(gpx_file)
    global coord_list 
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coord_list.append((point.latitude, point.longitude))
    for route in gpx.routes:
        for point in route.points:
            coord_list.append((point.latitude, point.longitude))
    x, y = zip(*coord_list)  # This will unzip the coord_list into two lists

    gmap = gmplot.GoogleMapPlotter(
        x[0], y[0], 14.1, apikey=GOOGLE_MAP_API_KEY
    )
    gmap.plot(x, y, "cornflowerblue", edge_width=2.5)
    gmap.draw('main/static/map.html') 

    driver.get('http://localhost:5000' + url_for('static', filename='map.html'))
    time.sleep(2)  
    driver.save_screenshot("main/static/map.png")

    response = {
        'success': True,
        'code': 200,
        'data': 'map.png'
    }
    return jsonify(response)

@chat.route('/api/addchat', methods=['POST'])
def add_chat():
    temp = json.loads(request.form["data"])
    label = "New Chat"
    description = "This is new chatbot"
    model = "GPT-3.5-Turbo"
    conversation = "Hello friends! How can I help you today?"
    creativity = 0.5
    rider_level = temp['level']
    age = temp['age']    
    gender = temp['gender']
    location = temp['location']
    behavior = f'''As an avid bike racer, I understand the importance of having the right equipment for optimal performance and safety. 
    
    Since the user's age is {age} years, {gender}, and {rider_level}, I would recommend the necessary products to provide more comfort for the user.

    Please take a moment to fill in the details above so I can generate personalized product recommendations tailored to your specific needs and preferences from specializedaustin website.
    Answer format is like this:
    =========
    Product 1:
        - Product Name:
        - Product Description:
        - Product Price:
        - Product Image:
    Product 2:
        - Product Name:
        - Product Description:
        - Product Price:
        - Product Image:
    Product 3:
        - Product Name:
        - Product Description:
        - Product Price:
        - Product Image:
    =========

    Outpur is html.
    '''
    print(behavior)
    behaviormodel = "If there is relevant training data available, please utilize it to generate responses using the provided information. However, if no training data exists for the specific query, you may respond with \"I don't know.\""
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
                'label': chat.label[:10],
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


@chat.route('/api/deletechat', methods=['POST'])
def delete_chat():
    id = request.form['id']
    if chat := db.session.query(Chat).filter_by(id=id).first():
        db.session.query(Message).filter_by(chat_id=id).delete()
        # delete index in the pinecone
        db.session.delete(chat)
        db.session.commit()
        response = {
            'success': True,
            'message': 'Chat has been deleted from the database.'
        }
    else:
        response = {
            'success': False,
            'message': 'Chat with label not found in the database.'
        }

    return jsonify(response)

@chat.route('/api/editchat', methods=['POST'])
def edit_chat():
    label = request.form['chat_name']
    uuid = request.form['uuid']
    chat = db.session.query(Chat).filter_by(uuid=uuid).first()
    if chat is None:
        # If no such chat exists, return an error response
        response = {
            'success': False,
            'code': 404,
            'message': 'ChatBot not found'
        }
    else:
        chat.label = label
        db.session.commit()

        # Return a success response
        response = {
            'success': True,
            'code': 200,
            'message': 'Your ChatBot was updated successfully'
        }
    return jsonify(response)