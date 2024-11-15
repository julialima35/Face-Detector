# Detecção de Rostos em Imagens

Este projeto utiliza a biblioteca **OpenCV** para realizar a detecção de rostos em imagens. O código carrega uma imagem, converte para escala de cinza, aplica a detecção de rostos usando o classificador Haar Cascade e exibe a imagem com os rostos destacados.

## Funcionalidades

- **Carregar Imagem**: Lê uma imagem a partir de um caminho especificado.
- **Converter para Escala de Cinza**: Converte a imagem para escala de cinza para facilitar a detecção.
- **Detecção de Rostos**: Utiliza o classificador Haar Cascade da OpenCV para identificar rostos na imagem.
- **Exibição da Imagem**: Exibe a imagem original com retângulos desenhados ao redor dos rostos detectados.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação utilizada para o projeto.
- **OpenCV**: Biblioteca para processamento de imagens e visão computacional.
- **Matplotlib**: Biblioteca para exibição de imagens.

## Dependências

Este projeto depende das seguintes bibliotecas Python:

- `opencv-python` para manipulação e processamento de imagens.
- `matplotlib` para visualização das imagens.

Para instalar as dependências, utilize o comando:

```bash
pip install opencv-python matplotlib