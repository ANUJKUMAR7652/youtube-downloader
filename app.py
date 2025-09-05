from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
from pytubefix.helpers import safe_filename
import io
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """यूट्यूब URL से प्रोग्रेसिव वीडियो/ऑडियो डाउनलोड को संभालता है।"""
    try:
        url = request.form['url']
        quality = request.form['quality']
        
        # यह लाइन 'बॉट डिटेक्शन' त्रुटि को ठीक करने का प्रयास करती है
        yt = YouTube(url, use_po_token=True, use_oauth=False, allow_oauth_cache=False)
        
        stream = None
        
        if quality == 'high':
            # उच्चतम रिज़ॉल्यूशन वाला प्रोग्रेसिव स्ट्रीम (आमतौर पर 720p)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
        elif quality == 'low':
            # सबसे कम रिज़ॉल्यूशन वाला प्रोग्रेसिव स्ट्रीम (आमतौर पर 360p)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_lowest_resolution()
        elif quality == 'audio':
            # केवल ऑडियो वाला सबसे अच्छा स्ट्रीम
            stream = yt.streams.get_audio_only()
        
        if not stream:
            return "चुनी गई क्वालिटी में कोई स्ट्रीम उपलब्ध नहीं है।", 404

        # pytubefix से एक सुरक्षित फ़ाइल नाम बनाएँ
        filename = safe_filename(yt.title)
        file_extension = ".mp3" if quality == 'audio' else ".mp4"
        full_filename = f"{filename}{file_extension}"
        mime_type = 'audio/mpeg' if quality == 'audio' else 'video/mp4'

        # मेमोरी में वीडियो डाउनलोड करें
        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        
        # फ़ाइल को उपयोगकर्ता को भेजें
        return send_file(
            buffer,
            as_attachment=True,
            download_name=full_filename,
            mimetype=mime_type
        )

    except Exception as e:
        # किसी भी त्रुटि को पकड़ें और दिखाएं
        error_details = traceback.format_exc()
        # त्रुटि को कॉपी करने में आसान बनाने के लिए उसे <pre> टैग में लौटाएं
        return f"<pre>एक विस्तृत त्रुटि हुई:\n\n{error_details}</pre>", 500

# Gunicorn इस हिस्से को नहीं चलाएगा, लेकिन यह स्थानीय परीक्षण के लिए अच्छा है
if __name__ == '__main__':
    app.run(debug=True)

