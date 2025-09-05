from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
from pytubefix.helpers import safe_filename
import io

# यह WSGI एप्लिकेशन के लिए आवश्यक है
# PythonAnywhere इस 'app' ऑब्जेक्ट को ढूंढेगा
app = Flask(__name__)

@app.route('/')
def index():
    """मुख्य पेज को रेंडर करता है।"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """यूट्यूब URL से प्रोग्रेसिव वीडियो/ऑडियो डाउनलोड को संभालता है।"""
    try:
        url = request.form['url']
        quality = request.form['quality']
        
        yt = YouTube(url)
        
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

        safe_title = safe_filename(yt.title)
        filename = f"{safe_title}.mp3" if quality == 'audio' else f"{safe_title}.mp4"
        mime_type = 'audio/mpeg' if quality == 'audio' else 'video/mp4'

        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_type
        )

    except Exception as e:
        return f"एक त्रुटि हुई: {str(e)}", 500

# यह सुनिश्चित करने के लिए कि यह स्थानीय रूप से भी चलता है
if __name__ == '__main__':
    app.run(debug=True)

