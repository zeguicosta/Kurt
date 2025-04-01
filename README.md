# Jogo de Plataforma 2D com Pygame

Um jogo de plataforma 2D simples criado com Pygame onde você coleta moedas e evita inimigos.

## Requisitos

- Python 3.6 ou superior
- Pygame 2.5.2

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Jogar

Execute o jogo com o comando:

```bash
python main.py
```

### Controles

- **Setas Esquerda/Direita**: Mover o personagem
- **Barra de Espaço**: Pular
- **R**: Reiniciar o jogo após o game over

### Objetivo

- Colete as moedas amarelas para ganhar pontos
- Evite os inimigos vermelhos
- Sobreviva o máximo possível com suas 3 vidas

## Recursos do Jogo

- Sistema de física com gravidade e colisões
- Sistema de pontuação
- Sistema de vidas
- Inimigos que patrulham as plataformas
- Moedas para coletar
- Estado de invencibilidade temporária após sofrer dano
- Tela de game over com opção de reinício

## Personalização

Você pode personalizar o jogo editando o arquivo `main.py`:

- Alterar cores, tamanho da tela ou velocidade do jogo
- Adicionar mais plataformas, inimigos ou moedas
- Modificar a física do jogo (gravidade, velocidade de movimento, etc.)
- Adicionar novos tipos de inimigos ou obstáculos 