import cv2
import socket
import random

# Configurações da câmera (webcam padrão do computador)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao acessar a câmera")
    exit()

# Carrega o classificador em cascata para detecção de rosto
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Configurações do socket
HOST = '127.0.0.1'  # Endereço IP do servidor (Unity)
PORT = 65432        # Porta para comunicação

# Inicialize o socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, PORT))
    print("Conectado ao Unity")
except Exception as e:
    print(f"Erro ao conectar ao Unity: {e}")
    exit()

# Função para enviar comandos para Unity
def send_command(command):
    try:
        sock.sendall(command.encode())  # Envia o comando como string
    except Exception as e:
        print(f"Erro ao enviar comando: {e}")

# Dimensões da área de captura
WIDTH, HEIGHT = 640, 480
last_x_center = WIDTH // 2
last_y_center = HEIGHT // 2
move_threshold = 10  # Sensibilidade para detectar movimentos

try:
    while True:
        # Captura um frame da webcam
        ret, frame = cap.read()
        if not ret:
            continue

        # Redimensiona e converte para tons de cinza
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecção de rostos
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        # Inicializa o centro do rosto
        x_center = WIDTH // 2
        y_center = HEIGHT // 2

        # Verifica se um rosto foi detectado
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            x_center = x + w // 2
            y_center = y + h // 2

            # Desenha o rosto detectado
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.circle(frame, (x_center, y_center), 5, (0, 255, 0), -1)

        # Controle de movimento baseado no rosto
        if abs(x_center - last_x_center) > move_threshold or abs(y_center - last_y_center) > move_threshold:
            if x_center < WIDTH // 3:  # Lado esquerdo
                send_command("LEFT")
            elif x_center > 2 * WIDTH // 3:  # Lado direito
                send_command("RIGHT")
            elif y_center < HEIGHT // 3:  # Parte superior
                send_command("UP")
            elif y_center > 2 * HEIGHT // 3:  # Parte inferior
                send_command("DOWN")

        # Atualiza a última posição
        last_x_center = x_center
        last_y_center = y_center

        # Exibe o frame capturado com as marcações
        cv2.imshow("Detecção Facial", frame)

        # Sai do loop ao pressionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrompido pelo usuário")

finally:
    # Libera recursos
    cap.release()
    sock.close()
    cv2.destroyAllWindows()
