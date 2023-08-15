from flask import Blueprint, jsonify, request
from .models import Message, Chat
from bs4 import BeautifulSoup
import requests
from . import db
import datetime
from rich import print, pretty
import time
import os
import json
from .generate_response import generate_message, generate_AI_message, generate_Bubble_message
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import re

pretty.install()
message = Blueprint('message', __name__)

def correct_grammar(text):
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)

    # Correct each sentence separately
    corrected_sentences = []
    for sentence in sentences:
        # Tokenize the sentence into words and tag their parts of speech
        words = nltk.word_tokenize(sentence)
        tagged_words = nltk.pos_tag(words)

        # Perform grammar correction based on POS tags
        corrected_words = []
        for word, tag in tagged_words:
            # Perform grammar correction as needed
            # Example correction: singularize nouns, use proper verb forms, etc.
            corrected_word = word  # Placeholder for correction logic
            corrected_words.append(corrected_word)

        # Reconstruct the corrected sentence
        corrected_sentence = " ".join(corrected_words)
        corrected_sentences.append(corrected_sentence)

    # Reconstruct the entire corrected text
    corrected_text = " ".join(corrected_sentences)
    return corrected_text

@message.route('/api/createmessage', methods=['POST'])
def init_message():
    chat_id = request.json['id']
    behavior = request.json['behavior']
    creativity = request.json['creativity']
    conversation = request.json['conversation']
    messages = db.session.query(Message).all()
    for row in messages:
        _messages = json.loads(row.message)
        if len(_messages) < 2:
            db.session.delete(row)
    db.session.commit()
    if conversation == "":
        message = json.dumps([])
    else:
        message = json.dumps([{"role": "ai", "content": conversation}])
    new_message = Message(chat_id=chat_id, message=message,
                          behavior=behavior, creativity=creativity)
    db.session.add(new_message)
    db.session.commit()
    response = {'success': True, 'code': 200,
                'message': "Successfuly created", 'data': new_message.uuid}
    print(new_message.uuid)
    return jsonify(response)

@message.route('/api/sendchat', methods=['POST'])
def send_message():
    uuid = request.json['id']
    query = request.json['_message']
    current_message = db.session.query(Message).filter_by(uuid=uuid).first()
    if current_message is not None:
        chat = db.session.query(Chat).filter_by(id=current_message.chat_id).first()
        
        temp = current_message.creativity
        history = json.loads(current_message.message)
        if len(history) > 6:
            last_history = history[-6:]
        else:
            last_history = history
            behavior = current_message.behavior
            response = generate_message(query, last_history, behavior, temp, chat.uuid)
        history.append({"role": "human", "content":query})
        history.append({"role": "ai", "content":response})
        current_message.message = json.dumps(history)
        current_message.update_date = datetime.datetime.now()

        db.session.commit()
        # links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/[-\w./?=%&]+', response)
        _response = {
            'success': True,
            'code': 200,
            'message': 'Success Generate!!',
            'data': response,
            # 'image': links
        }
        
        return jsonify(_response)
    
@message.route('/api/getmessages', methods=['POST'])
def get_messages():
    chat_id = request.json['id']
    current_messages = db.session.query(
        Message).filter_by(chat_id=chat_id).all()
    response = []
    for _message in current_messages:
        message_data = {
            # 'uuid': _message.uuid,
            'message': json.loads(_message.message),
            # 'update_data': _message.update_date.strftime('%Y-%m-%d %H:%M:%S.%f')
        }
        response.append(message_data)
    text = json.dumps(response, indent=4)
    links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/[-\w./?=%&]+', text)
    print(links)

    _response = {
        'success': True,
        'code': 200,
        'message': 'Your messageBot selected successfully!!!',
        'data': response,
        # 'image': links
    }
    return jsonify(_response)
            