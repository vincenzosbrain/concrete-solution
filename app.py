import cv2
import numpy as np
from flask import Flask, render_template, Response
import time
import os

# !!! Adresse de ta caméra DroidCam (modifie si besoin) !!!
url = "http://192.168.178.25:4747/video"
cap = cv2.VideoCapture(url)

app = Flask(__name__)

start_time = time.time()
# Fonction pour capturer les frames et générer la vidéo en temps réel
def generate_frames():
    global start_time
    while True:

        ret, frame = cap.read()
        if not ret:
            break

        # Convertir l'image en HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Plage de rouge (deux zones)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([179, 255, 255])

        # Masques
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Message par défaut
        alert_message = "Safe"
        alert_color = (0, 255, 0)  # Vert

        # Rechercher les contours
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:  # Ajuste ce seuil si nécessaire
                x, y, w, h = cv2.boundingRect(cnt)

                # Agrandir les dimensions du rectangle
                padding = 10  # Ajouter un padding pour rendre le rectangle plus visible
                x -= padding
                y -= padding
                w += 2 * padding
                h += 2 * padding

                # Tracer le rectangle agrandi
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Modifier le message d'alerte
                alert_message = "   ! WARNING : CRACK DETECTED ! "
                alert_message_printed = f"Danger ! Coordonnees : x={x}, y={y}, w={w}, h={h}"
                print(alert_message_printed)
                alert_color = (0, 0, 255)  # Rouge
                break  # On affiche seulement la première zone détectée

        # Ajouter le texte directement sur l'image de la caméra
        cv2.putText(frame, alert_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, alert_color, 2)

        # Chronomètre : calcul du temps écoulé
        elapsed_time = int(time.time() - start_time)
        hours = elapsed_time // 3600
        minutes = (elapsed_time % 3600) // 60
        seconds = elapsed_time % 60
        timer_text = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Position du texte en bas à droite
        height, width, _ = frame.shape
        text_size, _ = cv2.getTextSize(timer_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        text_x = width - text_size[0] - 10
        text_y = height - 10

        # Affichage du timer
        cv2.putText(frame, timer_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # Convertir la frame en JPEG pour l'envoyer via HTTP
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#if __name__ == '__main__':
#    app.run(debug=False, host='0.0.0.0', port=5501)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5501))
    app.run(debug=False, host='0.0.0.0', port=port)
