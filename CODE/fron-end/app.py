from flask import Flask,render_template, url_for, redirect, request, session,jsonify # type: ignore
import mysql.connector, joblib # type: ignore
import pandas as pd
import numpy as np
import speech_recognition as sr # type: ignore
from googletrans import Translator # type: ignore
from gtts import gTTS # type: ignore
import os
import pandas as pd
from nltk.corpus import stopwords # type: ignore
stop_words = set(stopwords.words('english'))
import bcrypt# type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer# type: ignore
from sklearn.metrics.pairwise import cosine_similarity# type: ignore

app = Flask(__name__)
app.secret_key = 'admin'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='db'
)

mycursor = mydb.cursor()


def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()
    return


def retrivequery1(query, values):
    mycursor.execute(query, values)
    data = mycursor.fetchall()
    return data


def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        c_password = request.form['c_password']

        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = [i[0] for i in email_data]

            if email.upper() not in email_data_list:
                # Hash the password before storing
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, hashed_password)
                executionquery(query, values)

                session['user_email'] = email
                session['user_name'] = name
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID already exists!")
        return render_template('register.html', message="Confirm password does not match!")
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        query = "SELECT name, email, password FROM users WHERE email = %s"
        values = (email,)
        user_data = retrivequery1(query, values)

        if user_data:
            stored_hashed_password = user_data[0][2] 
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')): 
                session['user_email'] = user_data[0][1]
                session['user_name'] = user_data[0][0]
                return redirect(url_for('home'))
        return render_template('login.html', message="Invalid Email or Password")
    return render_template('login.html')


@app.route('/adlogin', methods=["GET", "POST"])
def adlogin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        if email == "admin@gmail.com":
            if password == "admin": 
                return render_template('admin.html', message="Welcome to Admin!!")
            return render_template('adlogin.html', message="Invalid Password for Admin!!")
        return render_template('adlogin.html', message="This email ID does not exist!")
    return render_template('adlogin.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')



@app.route('/view_data')
def view_data():
    query = "SELECT name, email, disease FROM prediction1"
    predictions_data = retrivequery2(query)
    return render_template('view_data.html', data=predictions_data)

@app.route('/view_data2')
def view_data2():
    query_r = "SELECT name, email, disease FROM prediction2"
    predictions_data_r = retrivequery2(query_r)
    return render_template('view_data2.html', data=predictions_data_r)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/prediction', methods=['GET', "POST"])
def prediction():
    result = None  
    suggestionsp = ""
    user_selections = {} 

    if request.method == "POST":
        user_selections = {key: request.form.get(key, '0') for key in [
            'Nausea', 'Lumber', 'Urine', 'Micturition', 'Urethra', 'Itch', 
            'Swelling', 'Inflammation', 'Nephritis', 'Irregular', 'No_Periods', 
            'Excessive_Hair_Growth', 'Buttocks', 'Belly_Fat', 'Hair_Loss', 'Acne'
        ]}

        # Convert values to integers where necessary
        lee = [[int(user_selections[key]) for key in user_selections]]

        # Load model and predict
        model = joblib.load("random_forest_model.joblib")
        predictions = model.predict(lee)
        
        # Determine result
        if predictions == 0:
            result = 'Healthy'
        elif predictions == 1:
            result = 'PCOS'
        else:
            result = 'UTI'
        
        SUGGESTIONSP = {
                "PCOS": "Follow a balanced diet rich in whole grains, lean proteins, and healthy fats.\n"
                        "Limit refined sugars and processed foods to help manage insulin levels.\n"
                        "Aim for 30-45 minutes of moderate exercise (5 days a week).\n"
                        "Maintain a healthy weight; even a 5-10%% reduction can improve symptoms.\n"
                        "Consult a gynecologist for medications like hormonal birth control to regulate periods.",
                "UTI":"Drink plenty of water to flush out bacteria.\n"
                        "Avoid caffeine, alcohol, and spicy foods that can irritate the bladder.\n"
                        "Practice good hygiene by wiping from front to back after using the toilet.\n"
                        "Urinate frequently and don’t hold urine for long periods.\n"
                        "Consult a doctor if symptoms persist; antibiotics may be required.",
                "Healthy":"Eat a nutritious diet with fruits, vegetables, and whole grains.\n"
                        "Exercise for at least 30 minutes daily to stay active.\n"
                        "Stay hydrated by drinking at least 2-3 liters of water per day.\n"
                        "Get 7-9 hours of quality sleep every night for proper rest.\n"
                        "Manage stress through meditation, deep breathing, or hobbies.",

            }

        suggestionsp = SUGGESTIONSP.get(result, SUGGESTIONSP['Healthy'])
        print(suggestionsp)
        # Insert the values into the 'prediction1' table
        name = session.get('user_name') 
        email = session.get('user_email')
        session['result'] = result
        query = "INSERT INTO prediction1 (name, email, disease) VALUES (%s, %s, %s)"
        values = (name, email, result)
        executionquery(query, values)
    return render_template('prediction.html', result=result, suggestionsp=suggestionsp, user_selections=user_selections)

@app.route('/voice', methods=["GET", "POST"])
def voice():
    diagnosis = ""
    my_text = None
    translated_text = None
    if request.method == "POST":
        language = request.form["language"]
        indian_languages = {'hi': 'Hindi','bn': 'Bengali','ta': 'Tamil','te': 'Telugu','kn': 'Kannada','ml': 'Malayalam','gu': 'Gujarati',
                            'mr': 'Marathi','or': 'Odia','pa': 'Punjabi','as': 'Assamese','sd': 'Sindhi','ur': 'Urdu','ne': 'Nepali' }
        print("Available Indian languages:")
        for code, lang in indian_languages.items():
            print(f"{code}: {lang}")
        language_code = language.strip()
        if language_code not in indian_languages:
            print("Invalid language code.")
            exit()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print(f"Please say something in {indian_languages[language_code]}:")
            audio = r.listen(source)
        with open("input.wav", "wb") as f:
            f.write(audio.get_wav_data())
        try:
            my_text = r.recognize_google(audio, language=f"{language_code}-IN")
            print("You said: " + my_text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            exit()
        translator = Translator()
        translated_text = translator.translate(my_text, dest="en").text
        conditions = {
            "PCOS": ["irregular periods", "no periods", "hormonal imbalance", "dark patches"],
            "UTI": ["urine burning sensation", "pain while urinating", "frequent urination"],
            "Healthy": ["no symptoms", "Weakness", "mild body pains", "knee pain"]
        }
        all_texts = []
        labels = []
        for condition, symptoms in conditions.items():
            for symptom in symptoms:
                all_texts.append(symptom)
                labels.append(condition)
        all_texts.append(translated_text)
        # Using TF-IDF Vectorizer and Cosine Similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        condition_scores = {cond: 0 for cond in conditions.keys()}
        condition_counts = {cond: 0 for cond in conditions.keys()}
        for i, score in enumerate(similarities):
            condition = labels[i]
            condition_scores[condition] += score
            condition_counts[condition] += 1
        # Compute Final Similarity Scores
        final_scores = {cond: (condition_scores[cond] / condition_counts[cond]) for cond in conditions.keys()}
        # Find the Best Match
        best_match = max(final_scores, key=final_scores.get)
        best_score = final_scores[best_match]
        if best_score < 0:  
            diagnosis = "Uncertain"
        else:
            diagnosis = best_match
        print(f"Diagnosis: {diagnosis}")
        
        
        user_name = session.get('user_name')
        email_r = session.get('user_email')
        session['diagnosis'] = diagnosis
        query = "INSERT INTO prediction2 (name, email, disease) VALUES (%s, %s, %s)"
        values = (user_name, email_r, diagnosis)
        executionquery(query, values)
        
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        SUGGESTIONS = {
            "PCOS": {
                "en": "Follow a balanced diet rich in whole grains, lean proteins, and healthy fats.\n"
                    "Limit refined sugars and processed foods to help manage insulin levels.\n"
                    "Aim for 30-45 minutes of moderate exercise (5 days a week).\n"
                    "Maintain a healthy weight; even a 5-10% reduction can improve symptoms.\n"
                    "Consult a gynecologist for medications like hormonal birth control to regulate periods.",
                    
                "hi": "संपूर्ण अनाज, दुबले प्रोटीन और स्वस्थ वसा से भरपूर संतुलित आहार लें।\n"
                    "परिष्कृत शर्करा और प्रसंस्कृत खाद्य पदार्थों से बचें ताकि इंसुलिन स्तर नियंत्रित रहे।\n"
                    "सप्ताह में 5 दिन 30-45 मिनट मध्यम व्यायाम करें।\n"
                    "स्वस्थ वजन बनाए रखें; 5-10% वजन घटाने से लक्षणों में सुधार हो सकता है।\n"
                    "माहवारी को नियमित करने के लिए स्त्री रोग विशेषज्ञ से परामर्श लें।",
                
                "bn": "সম্পূর্ণ শস্য, চর্বিহীন প্রোটিন এবং স্বাস্থ্যকর ফ্যাট সমৃদ্ধ সুষম খাদ্য গ্রহণ করুন।\n"
                    "পরিশোধিত চিনি এবং প্রক্রিয়াজাত খাবার এড়িয়ে চলুন।\n"
                    "সপ্তাহে ৫ দিন ৩০-৪৫ মিনিট মাঝারি ব্যায়াম করুন।\n"
                    "৫-১০% ওজন কমালে উপসর্গগুলির উন্নতি হতে পারে।\n"
                    "গাইনোকোলজিস্টের পরামর্শ নিন।",
                    
                "ta": "முழுமையான தானியங்கள், குறைந்த கொழுப்பு உள்ள புரதம் மற்றும் ஆரோக்கியமான கொழுப்புகள் நிறைந்த சமச்சீர் உணவை உட்கொள்ளுங்கள்.\n"
                    "சுத்திகரிக்கப்பட்ட சர்க்கரை மற்றும் செயலாக்க உணவுகளை தவிர்க்கவும்.\n"
                    "வாரத்தில் 5 நாட்கள் 30-45 நிமிடங்கள் மிதமான உடற்பயிற்சி செய்யுங்கள்.\n"
                    "உங்கள் உடல் எடையை கட்டுப்படுத்துங்கள்; 5-10% எடை குறைந்தால் அறிகுறிகள் மேம்படலாம்.\n"
                    "மாதவிடாய் ஒழுங்குபடுத்த ஹார்மோன் மாத்திரைகள் குறித்து மருத்துவரை அணுகவும்.",

                "te": "పూర్తి ధాన్యాలు, లీన్ ప్రోటీన్లు మరియు ఆరోగ్యకరమైన కొవ్వులతో సమతుల ఆహారం తీసుకోండి.\n"
                    "ఇన్సులిన్ స్థాయిలను నియంత్రించడానికి రిఫైన్డ్ షుగర్స్ మరియు ప్రాసెస్డ్ ఫుడ్స్ తగ్గించండి.\n"
                    "వారానికి 5 రోజుల పాటు 30-45 నిమిషాల మధ్యస్థ వ్యాయామం చేయండి.\n"
                    "ఆరోగ్యకరమైన బరువును నిర్వహించండి; 5-10% బరువు తగ్గడం లక్షణాలను మెరుగుపరచగలదు.\n"
                    "పిరియడ్స్ ని నియంత్రించడానికి హార్మోనల్ మందుల కోసం గైనకాలజిస్ట్‌ను సంప్రదించండి.",

                "kn": "ಪೂರ್ಣ ಧಾನ್ಯಗಳು, ಕಡಿಮೆ ಕೊಬ್ಬಿನ ಪ್ರೋಟೀನುಗಳು ಮತ್ತು ಆರೋಗ್ಯಕರ ಕೊಬ್ಬುಗಳ ಸಮತೋಲನ ಆಹಾರ ಸೇವಿಸಿ.\n"
                    "ರಿಫೈನ್ಡ್ ಸಕ್ಕರೆ ಮತ್ತು ಪ್ರೊಸೆಸ್ಡ್ ಆಹಾರಗಳನ್ನು ತಗ್ಗಿಸಿ.\n"
                    "ವಾರದಲ್ಲಿ 5 ದಿನಗಳ ಕಾಲ 30-45 ನಿಮಿಷಗಳಷ್ಟು ಮಧ್ಯಮ ವ್ಯಾಯಾಮ ಮಾಡಿ.\n"
                    "ಆರೋಗ್ಯಕರ ತೂಕವನ್ನು ಕಾಪಾಡಿ; 5-10% ತೂಕ ಕಡಿಮೆ ಮಾಡುವುದು ಲಕ್ಷಣಗಳಲ್ಲಿ ಸುಧಾರಣೆ ತರಬಹುದು.\n"
                    "ಹಾರ್ಮೋನಲ್ ಜನನ ನಿಯಂತ್ರಣಕ್ಕಾಗಿ ಗೈನಕಾಲಜಿಸ್ಟ್ ಅನ್ನು ಸಂಪರ್ಕಿಸಿ.",

                "ml": "മുഴുവൻ ധാന്യങ്ങൾ, കുറഞ്ഞ കൊഴുപ്പ് പ്രോട്ടീനുകൾ, ആരോഗ്യകരമായ കൊഴുപ്പുകൾ അടങ്ങിയ സമതുലിതമായ ആഹാരം സ്വീകരിക്കുക.\n"
                    "ശുദ്ധീകരിച്ച പഞ്ചസാരയും പ്രോസസ്ഡ് ഫുഡുകളും ഒഴിവാക്കുക.\n"
                    "ആഴ്ചയിൽ 5 ദിവസം 30-45 മിനിറ്റ് മിതമായ വ്യായാമം ചെയ്യുക.\n"
                    "ആരോഗ്യകരമായ ഭാരം നിലനിർത്തുക; 5-10% ഭാരം കുറയ്ക്കുന്നത് ലക്ഷണങ്ങൾ മെച്ചപ്പെടുത്തും.\n"
                    "മാസിക ചക്രം ക്രമീകരിക്കാൻ ഹോർമോൺ മരുന്നുകൾക്കായി ഗൈനക്കോളജിസ്റ്റുമായി കൺസൾട്ട് ചെയ്യുക.",

                "gu": "સમગ્ર અનાજ, દૂધ, પ્રોટીન અને આરોગ્યપ્રદ ચરબીથી સમતુલ્ય આહાર લો.\n"
                    "શુદ્ધ ખાંડ અને પ્રોસેસ્ડ ખોરાક ઓછા કરો.\n"
                    "અઠવાડિયામાં 5 દિવસ 30-45 મિનિટ માધ્યમ કસરત કરો.\n"
                    "સ્વસ્થ વજન જાળવી રાખો; 5-10% વજન ઘટાડવાથી લક્ષણોમાં સુધારો થાય છે.\n"
                    "માસિક ચક્ર નિયંત્રિત કરવા માટે ગાયનેકોલોજિસ્ટનો સંપર્ક કરો.",

                "mr": "पूर्ण धान्य, कमी चरबीयुक्त प्रथिने आणि आरोग्यदायी चरबीयुक्त संतुलित आहार घ्या.\n"
                    "शुद्ध साखर आणि प्रक्रिया केलेले अन्न टाळा.\n"
                    "आठवड्यात 5 दिवस 30-45 मिनिटे मध्यम व्यायाम करा.\n"
                    "नियमित वजन ठेवा; 5-10% वजन कमी केल्यास लक्षणे सुधारू शकतात.\n"
                    "मासिक पाळी नियंत्रित करण्यासाठी स्त्रीरोग तज्ञाचा सल्ला घ्या.",

                "or": "ସମ୍ପୂର୍ଣ୍ଣ ଧାନ୍ୟ, ଲୀନ୍ ପ୍ରୋଟିନ୍ ଏବଂ ସୁସ୍ଥ ଚର୍ବି ଯୋଗୁଁ ସମତୁଳିତ ଆହାର ଗ୍ରହଣ କରନ୍ତୁ।\n"
                    "ସଫା ଚିନି ଏବଂ ପ୍ରସଏସ୍ ଖାଦ୍ୟର ସେବନ କମ କରନ୍ତୁ।\n"
                    "ପ୍ରତି ସପ୍ତାହରେ 5 ଦିନ 30-45 ମିନିଟ୍ ମଧ୍ୟମ ଅଭ୍ୟାସ କରନ୍ତୁ।\n"
                    "ନିୟମିତ ଓଜନ ରଖନ୍ତୁ; 5-10% ଓଜନ କମିଲେ ଲକ୍ଷଣର ସୁଧାର ହୋଇପାରେ।\n"
                    "ମାସିକ ଚକ୍ର ନିୟନ୍ତ୍ରଣ ପାଇଁ ଗାଇନକୋଲୋଜିଷ୍ଟଙ୍କ ସହ ଆଲୋଚନା କରନ୍ତୁ।",

                "pa": "ਪੂਰੇ ਅਨਾਜ, ਚਿੱਟੇ ਪ੍ਰੋਟੀਨ ਅਤੇ ਸਿਹਤਮੰਦ ਚਰਬੀਆਂ ਨਾਲ ਸੰਤੁਲਿਤ ਆਹਾਰ ਲਓ।\n"
                    "ਸੁਧ ਚੀਨੀ ਅਤੇ ਪ੍ਰੋਸੈੱਸ ਕੀਤੇ ਭੋਜਨ ਤੋਂ ਪਰਹੇਜ਼ ਕਰੋ।\n"
                    "ਹਫ਼ਤੇ ਵਿੱਚ 5 ਦਿਨ 30-45 ਮਿੰਟ ਦਰਮਿਆਨੀ ਵਿਆਯਾਮ ਕਰੋ।\n"
                    "ਸਿਹਤਮੰਦ ਭਾਰ ਬਣਾਈ ਰੱਖੋ; 5-10% ਭਾਰ ਘਟਾਉਣ ਨਾਲ ਲੱਛਣਾਂ ਵਿੱਚ ਸੁਧਾਰ ਹੋ ਸਕਦਾ ਹੈ।\n"
                    "ਮਹੀਨਾਵਾਰੀ ਨੂੰ ਨਿਯੰਤਰਿਤ ਕਰਨ ਲਈ ਗਾਇਨਕੋਲੋਜਿਸਟ ਦੀ ਸਲਾਹ ਲਓ।"
            },
            "UTI": {
                "en": "Drink plenty of water to flush out bacteria.\n"
                    "Avoid caffeine, alcohol, and spicy foods that can irritate the bladder.\n"
                    "Practice good hygiene by wiping from front to back after using the toilet.\n"
                    "Urinate frequently and don’t hold urine for long periods.\n"
                    "Consult a doctor if symptoms persist; antibiotics may be required.",

                "hi": "बैक्टीरिया को बाहर निकालने के लिए खूब पानी पिएं।\n"
                    "कैफीन, शराब और मसालेदार भोजन से बचें, जो मूत्राशय को परेशान कर सकते हैं।\n"
                    "शौचालय का उपयोग करने के बाद आगे से पीछे की ओर पोंछने की आदत डालें।\n"
                    "बार-बार पेशाब करें और पेशाब को ज्यादा देर तक न रोकें।\n"
                    "यदि लक्षण बने रहें, तो डॉक्टर से परामर्श लें; एंटीबायोटिक्स की आवश्यकता हो सकती है।",

                "bn": "ব্যাকটেরিয়া দূর করতে প্রচুর পানি পান করুন।\n"
                    "ক্যাফেইন, অ্যালকোহল এবং মশলাদার খাবার এড়িয়ে চলুন।\n"
                    "টয়লেট ব্যবহারের পরে সামনের দিক থেকে পিছনের দিকে মুছুন।\n"
                    "প্রস্রাব ধরে রাখবেন না এবং নিয়মিত প্রস্রাব করুন।\n"
                    "লক্ষণ স্থায়ী হলে ডাক্তারের পরামর্শ নিন; অ্যান্টিবায়োটিক লাগতে পারে।",

                "ta": "பாக்டீரியாக்களை வெளியேற்ற தண்ணீர் அதிகம் குடிக்கவும்.\n"
                    "மூத்திரப்பையில் பிரச்சனை ஏற்படுத்தக்கூடிய காபி, மதுபானம் மற்றும் காரமான உணவுகளை தவிர்க்கவும்.\n"
                    "கழிப்பறையைப் பயன்படுத்திய பிறகு முன்புறத்திலிருந்து பின்னாக துடைக்கவும்.\n"
                    "வழக்கமாக சிறுநீர் கழிக்கவும் மற்றும் சிறுநீரை அதிக நேரம் தடுக்காதீர்கள்.\n"
                    "லட்சணங்கள் நீடித்தால், மருத்துவரை அணுகவும்; ஆன்டிபயாட்டிக்ஸ் தேவைப்படலாம்.",

                "te": "బాక్టీరియాను బయటకు పంపించడానికి ఎక్కువగా నీరు తాగండి.\n"
                    "కాఫీ, మద్యం మరియు మసాలా ఆహారాన్ని తగ్గించండి, ఇవి మూత్రపిండాలను ప్రభావితం చేయవచ్చు.\n"
                    "మలమూత్ర విసర్జన తర్వాత ముందుకు నుంచి వెనుకకు తుడవండి.\n"
                    "నిజమైన తరచుగా మూత్ర విసర్జన చేయండి మరియు దీర్ఘకాలం పాటు ఆపుకోవద్దు.\n"
                    "లక్షణాలు కొనసాగితే, డాక్టర్‌ను సంప్రదించండి; యాంటీబయోటిక్స్ అవసరమవచ్చు."
            },

            "Healthy": {
                "en": "Eat a nutritious diet with fruits, vegetables, and whole grains.\n"
                    "Exercise for at least 30 minutes daily to stay active.\n"
                    "Stay hydrated by drinking at least 2-3 liters of water per day.\n"
                    "Get 7-9 hours of quality sleep every night for proper rest.\n"
                    "Manage stress through meditation, deep breathing, or hobbies.",

                "hi": "फल, सब्जियां और संपूर्ण अनाज से भरपूर पौष्टिक आहार लें।\n"
                    "प्रतिदिन कम से कम 30 मिनट व्यायाम करें।\n"
                    "रोजाना 2-3 लीटर पानी पीकर हाइड्रेटेड रहें।\n"
                    "रात में 7-9 घंटे की अच्छी नींद लें।\n"
                    "तनाव को कम करने के लिए ध्यान, गहरी सांस लेना या शौक अपनाएं।",

                "bn": "ফল, সবজি এবং সম্পূর্ণ শস্য সমৃদ্ধ পুষ্টিকর খাদ্য গ্রহণ করুন।\n"
                    "প্রতিদিন কমপক্ষে ৩০ মিনিট ব্যায়াম করুন।\n"
                    "প্রতিদিন ২-৩ লিটার পানি পান করুন।\n"
                    "প্রতি রাতে ৭-৯ ঘণ্টা ভালো ঘুম নিশ্চিত করুন।\n"
                    "ধ্যান, গভীর শ্বাস বা শখের মাধ্যমে মানসিক চাপ নিয়ন্ত্রণ করুন।",

                "ta": "பழங்கள், காய்கறிகள் மற்றும் முழு தானியங்கள் அடங்கிய ஆரோக்கியமான உணவு உட்கொள்ளுங்கள்.\n"
                    "தினமும் குறைந்தது 30 நிமிடங்கள் உடற்பயிற்சி செய்யுங்கள்.\n"
                    "ஒரு நாளைக்கு 2-3 லிட்டர் தண்ணீர் குடிக்கவும்.\n"
                    "தினமும் 7-9 மணிநேரம் தரமான உறக்கம் பெறுங்கள்.\n"
                    "மன அழுத்தத்தைக் குறைக்க தியானம், ஆழ்ந்த மூச்சு அல்லது பொழுதுபோக்கு செயல் பாருங்கள்.",

                "te": "పండ్లు, కూరగాయలు, మరియు పూర్తి ధాన్యాలతో సమతుల ఆహారం తీసుకోండి.\n"
                    "రోజుకు కనీసం 30 నిమిషాలు వ్యాయామం చేయండి.\n"
                    "రోజుకు 2-3 లీటర్ల నీరు తాగి హైడ్రేటెడ్ గా ఉండండి.\n"
                    "ప్రతిరోజూ 7-9 గంటలు నాణ్యమైన నిద్ర పొందండి.\n"
                    "ధ్యానం, లోతైన శ్వాస లేదా అభిరుచుల ద్వారా ఒత్తిడిని నిర్వహించండి."
            },
            "Uncertain":{
                "en": "Eat a nutritious diet with fruits, vegetables, and whole grains.\n"
                    "Exercise for at least 30 minutes daily to stay active.\n"
                    "Stay hydrated by drinking at least 2-3 liters of water per day.\n"
                    "Get 7-9 hours of quality sleep every night for proper rest.\n"
                    "Manage stress through meditation, deep breathing, or hobbies.",

                "hi": "फल, सब्जियां और संपूर्ण अनाज से भरपूर पौष्टिक आहार लें।\n"
                    "प्रतिदिन कम से कम 30 मिनट व्यायाम करें।\n"
                    "रोजाना 2-3 लीटर पानी पीकर हाइड्रेटेड रहें।\n"
                    "रात में 7-9 घंटे की अच्छी नींद लें।\n"
                    "तनाव को कम करने के लिए ध्यान, गहरी सांस लेना या शौक अपनाएं।",

                "bn": "ফল, সবজি এবং সম্পূর্ণ শস্য সমৃদ্ধ পুষ্টিকর খাদ্য গ্রহণ করুন।\n"
                    "প্রতিদিন কমপক্ষে ৩০ মিনিট ব্যায়াম করুন।\n"
                    "প্রতিদিন ২-৩ লিটার পানি পান করুন।\n"
                    "প্রতি রাতে ৭-৯ ঘণ্টা ভালো ঘুম নিশ্চিত করুন।\n"
                    "ধ্যান, গভীর শ্বাস বা শখের মাধ্যমে মানসিক চাপ নিয়ন্ত্রণ করুন।",

                "ta": "பழங்கள், காய்கறிகள் மற்றும் முழு தானியங்கள் அடங்கிய ஆரோக்கியமான உணவு உட்கொள்ளுங்கள்.\n"
                    "தினமும் குறைந்தது 30 நிமிடங்கள் உடற்பயிற்சி செய்யுங்கள்.\n"
                    "ஒரு நாளைக்கு 2-3 லிட்டர் தண்ணீர் குடிக்கவும்.\n"
                    "தினமும் 7-9 மணிநேரம் தரமான உறக்கம் பெறுங்கள்.\n"
                    "மன அழுத்தத்தைக் குறைக்க தியானம், ஆழ்ந்த மூச்சு அல்லது பொழுதுபோக்கு செயல் பாருங்கள்.",

                "te": "పండ్లు, కూరగాయలు, మరియు పూర్తి ధాన్యాలతో సమతుల ఆహారం తీసుకోండి.\n"
                    "రోజుకు కనీసం 30 నిమిషాలు వ్యాయామం చేయండి.\n"
                    "రోజుకు 2-3 లీటర్ల నీరు తాగి హైడ్రేటెడ్ గా ఉండండి.\n"
                    "ప్రతిరోజూ 7-9 గంటలు నాణ్యమైన నిద్ర పొందండి.\n"
                    "ధ్యానం, లోతైన శ్వాస లేదా అభిరుచుల ద్వారా ఒత్తిడిని నిర్వహించండి."
            }
        }

        suggestion_text = SUGGESTIONS.get(diagnosis, SUGGESTIONS['Healthy']).get(language, SUGGESTIONS['Healthy']['en'])
        messages = {
            "PCOS": f"{user_name}, you may have Polycystic Ovary Syndrome. I suggest you to follow a balanced diet rich in whole grains, lean proteins, and healthy fats.Limit refined sugars and processed foods to help manage insulin levels. Aim for 30-45 minutes of moderate exercise (5 days a week).Even a 5-10% reduction can improve symptoms.Please consult a gynecologist.",
            "UTI": f"{user_name}, you may have a Urinary Tract Infection. Please consult a doctor.",
            "Healthy": f"{user_name}, you are healthy. Keep it up!",
            "Uncertain":f"{user_name}, this may require further checkups, please consult a doctor"
        }
        translated_message = translator.translate(messages[diagnosis], dest=language_code.split('-')[0]).text
        tts = gTTS(text=translated_message, lang=language_code.split('-')[0])
        
        audio_path = os.path.join(audio_dir, f"{user_name}_diagnosis_audio.mp3")
        tts.save(audio_path)
        return render_template("voice.html", suggestion_text=suggestion_text, audio_feedback=audio_path)                
    return render_template("voice.html")

@app.route('/pie_chart')
def pie_chart():
    # Fetching data
    query_urban = "SELECT name, email, disease FROM prediction1"
    query_rural = "SELECT name, email, disease FROM prediction2"
    
    urban_data = retrivequery2(query_urban)
    rural_data = retrivequery2(query_rural)

    # Convert to DataFrame
    df_urban = pd.DataFrame(urban_data, columns=['name', 'email', 'disease'])
    df_rural = pd.DataFrame(rural_data, columns=['name', 'email', 'disease'])

    # Create unique ID to remove duplicates (prefer urban)
    df_urban["id"] = df_urban["name"] + df_urban["email"]
    df_rural["id"] = df_rural["name"] + df_rural["email"]

    df_combined = pd.concat([df_urban, df_rural]).drop_duplicates(subset=['id'], keep='first')

    categories = ["PCOS", "UTI", "Healthy"]
    urban_counts = df_urban['disease'].value_counts().to_dict()
    rural_counts = df_rural['disease'].value_counts().to_dict()

    data = {
        "categories": categories,
        "total": [urban_counts.get(c, 0) + rural_counts.get(c, 0) for c in categories],
        "urban": [urban_counts.get(c, 0) for c in categories],
        "rural": [rural_counts.get(c, 0) for c in categories]
    }

    return render_template('pie_chart.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)