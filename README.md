# Detector de Rostos em Imagens

Este projeto usa a biblioteca **OpenCV** para detectar rostos em uma imagem que você fornecer. O código carrega a imagem, converte para preto e branco, encontra os rostos e coloca retângulos ao redor de cada um deles. Por fim, a imagem com os rostos destacados é exibida. É uma maneira simples e divertida de fazer detecção facial em imagens!

## Funcionalidades

- **Carregar Imagem**: Você pode carregar qualquer imagem de um arquivo no seu computador.
- **Detectar Rostos**: Usamos uma ferramenta chamada **Haar Cascade** para encontrar rostos na imagem.
- **Exibir a Imagem com os Rostos Marcados**: Após detectar os rostos, o programa desenha retângulos ao redor deles e exibe a imagem com as marcações.

## Tecnologias Utilizadas

Este projeto usa algumas bibliotecas poderosas do Python:

- **Python 3.x**: A linguagem de programação que você vai usar.
- **OpenCV**: A principal biblioteca que usamos para detectar os rostos e manipular a imagem.
- **Matplotlib**: Usada para exibir a imagem com os rostos detectados.

Para instalar as dependências do projeto, basta rodar o seguinte comando:

```bash
pip install opencv-python matplotlib
