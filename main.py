import transcricao
import os

modelos = ["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en"]

formatos = ["mp3"]

path_amostras = os.path.abspath(os.curdir) + "/amostras/"

arquivos = transcricao.retorna_amostras(path_amostras, formatos)

transcricao.executa_transcricao(modelos, arquivos, path_amostras, nome_resultados="resultados.txt")

