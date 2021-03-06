from flask import Flask, request, jsonify
import pickle5 as pickle
import pandas as pd 
import speech_recognition as sr
import re
import sklearn 

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def predict():
  audiofile = request.files['AudioFile']
  recognizer = sr.Recognizer()
  recognizer.energy_threshold = 300
  sample_file = sr.AudioFile(audiofile) 
  with sample_file as source:
    sample_audio = recognizer.record(source)
  transcription = recognizer.recognize_google(audio_data=sample_audio, language="en-US")
  unseen_data = pd.DataFrame([(transcription)],columns=['Transcription'])
  unseen_data['Transcription'] = unseen_data['Transcription'].apply(lambda x: " ".join(x.lower() for x in x.split())) 
  unseen_data['Transcription'] = unseen_data['Transcription'].map(lambda x: re.sub(r'\W+', ' ', x)) 
  vectorizer_word_unigram = pickle.load(open('./models/vectorizer_word_unigram.pkl', 'rb'))
  unseen_data = unseen_data['Transcription']
  transform_unseen_data = vectorizer_word_unigram.transform(unseen_data)
  transform_unseen_data = transform_unseen_data.todense()
  word_unigram_features = vectorizer_word_unigram.get_feature_names()
  unseen_data_features = pd.DataFrame(transform_unseen_data, columns = word_unigram_features)
  model = pickle.load(open('./models/trained_model.pkl', 'rb'))
  model_predictions = model.predict(unseen_data_features)
  return jsonify( 
    result = int(model_predictions[0]),
    transcription = transcription
  )