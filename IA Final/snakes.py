import cv2
import numpy as np
import pygame
import random

# Inicializa o Pygame
pygame.init()

# Dimensões da tela
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo da Cobra")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)  # Cor azul claro

# Configurações da cobra
snake_block = 10
snake_speed = 15  # Velocidade da cobra

# Configurações da maçã
foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0

# Inicializa o clock do pygame
clock = pygame.time.Clock()

# Configurações da câmera (webcam padrão do computador)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao acessar a câmera")
    exit()

# Carrega o classificador em cascata para detecção de rosto
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Função para desenhar a cobra
def draw_snake(snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])

# Função para desenhar a pontuação
def your_score(score):
    font_style = pygame.font.SysFont(None, 25)
    value = font_style.render("Sua Pontuação: " + str(score), True, WHITE)
    screen.blit(value, [0, 0])

# Função principal do jogo
def gameLoop():
    global foodx, foody

    game_over = False
    game_close = False
    score = 0

    x1 = int(WIDTH / 2)
    y1 = int(HEIGHT / 2)
    x_change = 0
    y_change = 0
    snake_list = []
    length_of_snake = 1

    last_x_center = WIDTH // 2
    last_y_center = HEIGHT // 2

    # Reduzindo o limiar para capturar movimentos menores
    move_threshold = 10  # Aumenta o limiar para movimentos maiores

    while not game_over:
        while game_close:
            screen.fill(LIGHT_BLUE)  # Usando azul claro como fundo
            font_style = pygame.font.SysFont(None, 50)
            message = font_style.render("Você Perdeu! Q-Sair ou C-Jogar", True, WHITE)
            screen.blit(message, [WIDTH / 6, HEIGHT / 3])
            your_score(score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()  # Reinicia o jogo

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # Captura um frame da webcam
        ret, frame = cap.read()
        if not ret:
            continue

        # Converte a imagem para tons de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Melhorar o contraste da imagem (Equalização de histograma)
        gray = cv2.equalizeHist(gray)

        # Detecção de rostos
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        # Inicializa variáveis do centro do rosto
        x_center = WIDTH // 2
        y_center = HEIGHT // 2

        # Verifica se um rosto foi detectado
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            x_center = x + w // 2  # Calcula o centro do rosto
            y_center = y + h // 2  # Calcula o centro do rosto

            # Desenha um retângulo ao redor do rosto
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Desenha um ponto no centro do rosto (nariz)
            cv2.circle(frame, (x_center, y_center), 3, (0, 255, 0), -1)

        # Controle de movimento da cobra com base no centro do rosto
        if abs(x_center - last_x_center) > move_threshold or abs(y_center - last_y_center) > move_threshold:
            # Definindo movimento baseado nas coordenadas de x_center e y_center
            if x_center < WIDTH // 3:  # Lado esquerdo da tela
                  # Só muda para a esquerda se não estiver indo para a direita
                    x_change = -snake_block
                    y_change = 0
            elif x_center > 2 * WIDTH // 3:  # Lado direito da tela
                  # Só muda para a direita se não estiver indo para a esquerda
                    x_change = snake_block
                    y_change = 0
            elif y_center < HEIGHT // 3:  # Parte superior da tela
                  # Só muda para cima se não estiver indo para baixo
                    x_change = 0
                    y_change = -snake_block
            elif y_center > 2 * HEIGHT // 3:  # Parte inferior da tela
                  # Só muda para baixo se não estiver indo para cima
                    x_change = 0
                    y_change = snake_block

        # Atualiza a posição da cabeça da cobra
        x1 += x_change
        y1 += y_change
        snake_head = [x1, y1]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0
            length_of_snake += 1
            score += 1

        # Verifica colisão com o próprio corpo
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # Traz a cobra para o lado oposto da tela caso ela ultrapasse as bordas
        if x1 >= WIDTH:
            x1 = 0  # Vai para o lado esquerdo
        elif x1 < 0:
            x1 = WIDTH - snake_block  # Vai para o lado direito

        if y1 >= HEIGHT:
            y1 = 0  # Vai para a parte superior
        elif y1 < 0:
            y1 = HEIGHT - snake_block  # Vai para a parte inferior

        # Desenha os elementos na tela
        screen.fill(LIGHT_BLUE)  # Usando azul claro como fundo
        draw_snake(snake_list)
        pygame.draw.rect(screen, RED, [foodx, foody, snake_block, snake_block])
        your_score(score)

        pygame.display.update()

        clock.tick(snake_speed)  # Aqui é onde a velocidade da cobra é controlada

        # Atualiza as últimas posições do rosto
        last_x_center = x_center
        last_y_center = y_center

        # Exibe a janela do OpenCV para visualizar a detecção
        cv2.imshow("Frame", frame)

        # Se pressionar 'q', sai da janela do OpenCV
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

gameLoop()