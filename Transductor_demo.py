from flask import Flask, request, send_file, jsonify, Response
import os
import openai as ai
from werkzeug.utils import secure_filename
import json
import time

key = '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'
lista_archivos = os.listdir('Grabaciones')

soportado = ['mp3', 'flac', 'wav', 'm4a']
ruta_archivos = os.path.abspath('Grabaciones')
def limpieza():
    try:
        if (len(lista_archivos) >=1):    
            for col in lista_archivos:
                remove_file(f'Grabaciones/{col}')
        else:
            print('Carpeta Limpia !')
            
            
    except Exception as e:
        return print(f'Error : {e}')
        
def remove_file(path):
    try:
        
        time.sleep(2)
        os.remove(path)
        print('Se eliminó satisfactoriamente')
        return jsonify({'message': 'Se ha eliminado el archivo original satisfactoriamente'})
    except Exception as e:
        print(f'No se logró eliminar porque: {e}')
        return jsonify({'error': f'No se logró eliminar el archivo: {e}'})

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Grabaciones'

@app.route('/api/upload', methods=['POST'])
def upload_file():
    limpieza()
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó ningún archivo'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se proporcionó un nombre de archivo válido'})
        filename = secure_filename(file.filename)
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_filepath)
        return jsonify({'temp_filepath': temp_filepath})

    
        
    except Exception as e:
        return jsonify({f'error': '{e}'})
    
@app.route('/api/text', methods=['GET'])
def get_text():
    largo = len(os.listdir('Grabaciones'))
    if largo >= 1:
        for col in lista_archivos:
            tipo = str(col.split(sep='.')[1])
            if tipo in soportado:
                try:
                    ai.api_key = key
                    with open(f'Grabaciones/{col}', "rb") as audio_file:
                        transcript = ai.Audio.transcribe("whisper-1", audio_file)
                    transcript_text = transcript['text'].encode('UTF-7').decode('unicode_escape')
                    text = str(transcript_text).replace('+APM-n', 'ón')
                    l=len(os.listdir('Textos'))+1
                    text_file=open(f'Textos/archivo{l}.txt', 'w',encoding='UTF-8')
                    t=str(text).replace('Ã³','ó').encode('UTF-8').decode('unicode_escape')
                    text_file.write(t.replace('Ã³','ó'))
                    text_file.close()                   
                    
                    data = {"texto": text}
                    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
                    response = Response(json_data, content_type='application/json; charset=utf-8')

                    remove_file(f'Grabaciones/{col}')

                    return response

                except Exception as e:
                    return jsonify({'error': e})
            else:
                return jsonify({'error': 'Formato de archivo no soportado por whisper'})
    else:
        return jsonify({'error': 'No hay audios para transcribir!'})

if __name__ == '__main__':
    app.run()
