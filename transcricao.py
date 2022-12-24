import whisper
import os
import time
import re

#
# Carrega amostras em uma lista
def retorna_amostras(path_amostras: str, formatos: list):
    arquivos = []
    for arq in os.listdir(path_amostras):
        for formato in formatos:
            if arq.endswith("." + formato):
                arquivos.append(arq)
    arquivos.sort()
    return arquivos

def executa_transcricao(modelos: list, arquivos: list, path_amostras: str, nome_resultados="resultados.txt") ->  list:

    arq_resultados = open(path_amostras + nome_resultados, "w")

    for i in range(len(arquivos)):

        print(f"Amostra {i+1} de {len(arquivos)}\n")

        #
        # Header do arquivo de resultados
        arq_resultados.write("=" * 50)
        arq_resultados.write("\n")
        arq_resultados.write(f"Amostra {i+1}:\n")
        arq_resultados.write(f"Tamanho: {os.stat(path_amostras + f'amostra0{i+1}.mp3' if (i<9) else path_amostras + f'amostra{i+1}.mp3').st_size / (1024 * 1024):.2f}mb\n")

        arq_oficial = open(path_amostras + f"amostra0{i+1}.txt" if (i<9) else path_amostras + f"amostra{i+1}.txt", "r")

        transc_oficial = arq_oficial.readlines()

        qtd_palavras = len(transc_oficial[0].split())
        arq_resultados.write(f"Qtd. de palavras: {qtd_palavras}\n")
        arq_resultados.write(transc_oficial[1])
        arq_resultados.write(transc_oficial[2] + "\n\n")
        arq_resultados.write(transc_oficial[0])

        arq_oficial.close()

        #
        # Separa as palavras da transcrição original, remove caracteres especiais, salva em um arquivo temportário e libera a memória
        palavras_oficial = []
        for word in transc_oficial[0].split():
            word = re.sub("[,.?!;\s\"()-]", "", word)
            palavras_oficial.append(word.lower())

        with open("tmp.txt", "w") as arq_temp:
            for palavra in palavras_oficial:
                arq_temp.write(palavra + "\n")

        del palavras_oficial


        #
        # Executa cada modelo sobre a amostra 
        for modelo in modelos:

            #
            #Transcreve a amostra e armazena o tempo
            print(f"Executando modelo {modelo}\n")

            modelo_carregado = whisper.load_model(modelo)
            
            inicio = time.time()
            transc_whisper = modelo_carregado.transcribe(path_amostras + arquivos[i])
            final = time.time()
            tempo = final-inicio

            arq_resultados.write("-" * 50)
            arq_resultados.write(f"\nModelo: {modelo}")
            for k, v in transc_whisper.items():
                arq_resultados.write("\n")
                if(k not in "segments"):
                    arq_resultados.write(f"{k}:\n")
                    arq_resultados.write(f"{v}\n")
            arq_resultados.write(f"\ntempo: {tempo:.3f}s\n")

            #
            # Lê as palavras da transcrição original
            palavras_oficial = []
            with open("tmp.txt", "r") as arq_temp:
                for palavra in arq_temp.readlines():
                    palavras_oficial.append(palavra.replace("\n", ""))

            #
            # Separa palavras da transcrição do whisper
            palavras_modelo = []
            for word in transc_whisper["text"].split():
                word = re.sub("[,.?!;\s\"()-]+", "", word)
                palavras_modelo.append(word.lower())

            #
            # Compara as palavras das duas listas e conta as corretas
            corretas = 0
            for j in range(len(palavras_oficial)):
                for k in range(len(palavras_modelo)):
                    if (palavras_oficial[j] == palavras_modelo[k]):
                        corretas += 1
                        del palavras_modelo[k]
                        break

            #
            # Salva resultados no arquivo
            arq_resultados.write(f"Palavras erradas: {qtd_palavras - corretas} de {qtd_palavras}\n")
            arq_resultados.write(f"Taxa de erro: {100 - (corretas / qtd_palavras * 100):.3f}%\n")
            arq_resultados.write("-" * 50)
            arq_resultados.write("\n" * 3)

        os.remove("tmp.txt")

    arq_resultados.close()
    return
