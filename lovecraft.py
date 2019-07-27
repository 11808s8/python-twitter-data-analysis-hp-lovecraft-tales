
from pymongo import MongoClient
import base64
import hashlib
import json
from Crypto import Random
from Crypto.Cipher import AES

# GLOBALS

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-s[-1]]
client = MongoClient('localhost', 27017)
db = client.trabalho

posts = db.posts

numeroTotalIndices = 4
numeroTotalDeRegistrosQueDeveriaTer = 50000

# ===================

'''
    Classe responsável pelos métodos de criptografia (AES 256)
    Código modificado de: https://gist.github.com/maxpowel/c5fdac919528e36f553732b507420408
'''
class AESCipher:

    def __init__( self, key ):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))


'''
    Classe responsável pelas buscas no banco NoSQL MongoDB
'''
class Buscas:

    def __init__( self, key ): # seta a chave padrão para lidar com a criptografia do campo ANO
        self.cipher = key

    def tweets(self, dicionarioBusca):
        global posts
        return self.buscaTextual(dicionarioBusca)

    def tweetsCount(self, dicionarioBusca): # busca os tweets textualmente e retorna o texto
        #print(dicionarioBusca)
        return self.buscaTextual(dicionarioBusca,True)

    def ano(self,anoBusca): #busca os tweets por ano (traz todos e descriptografa 1 por 1)
        global posts
        listaRetorno = []
        for entrada in posts.find():
            anoDecrypt = str(self.cipher.decrypt(entrada["ano"]).decode("utf-8"))
            if(anoDecrypt==anoBusca):
                objeto = { 'ano': anoDecrypt, 'tweet':entrada["tweet"], 'mes':entrada["mes"]}
                listaRetorno.append(objeto)

        return listaRetorno

    def mes(self, mesBusca): # busca tweets pelo mês
        global posts
        return self.busca({'mes' : mesBusca})

    def busca(self, termoBusca):    #encapsulamento genérico para buscas
        global posts
        listaRetorno = []
        for entrada in posts.find(termoBusca):
            anoDecrypt = str(self.cipher.decrypt(entrada["ano"]).decode("utf-8"))
            objeto = { 'ano': anoDecrypt, 'tweet':entrada["tweet"], 'mes':entrada["mes"]}
            listaRetorno.append(objeto)
        return listaRetorno

    def buscaTextual(self, textoBusca, conta=False): # busca textual nos TWEETS
        global posts
        if(conta==False):
            listaRetorno = []
            for entrada in posts.find({"$text": {"$search":"\""+textoBusca+"\""}}):
                anoDecrypt = str(self.cipher.decrypt(entrada["ano"]).decode("utf-8"))
                objeto = { 'ano': anoDecrypt, 'tweet':entrada["tweet"], 'mes':entrada["mes"]}
                listaRetorno.append(objeto);
            return listaRetorno
        else:
            return (posts.find({"$text": {"$search":"\""+textoBusca+ "\""}})).count();

buscas = Buscas(AESCipher('minhasenha123456')) # nunca façam isso em casa, crianças

def erroPadrao():
    print("Nenhum registro foi encontrado! Retornando ao menu")



'''
    Classe responsável por 3 testes: sobre a quantidade de indices, a quantidade de registros e a criptografia feita sobre a chave ano
'''
def testes(qualTeste):
    global posts, numeroTotalIndices, numeroTotalDeRegistrosQueDeveriaTer

    def erroPadraoTestes(teste, mensagem):
        print("Ocorreu um erro no teste: " + teste)
        print(mensagem)

    if(qualTeste=='testar indices'):
        result = posts.index_information()
        i = 0
        for a in result:
            i+=1

        restoMensagem = "Esperava " + str(numeroTotalIndices) + " e obteve " + str(i) + "!"
        if(i==numeroTotalIndices): # 4 pois o MONGODB cria um índice único chamado ID
            print("Número de índices correto! " + restoMensagem)
        else:
            erroPadraoTestes(qualTeste, "Número de índices incorreto! " + restoMensagem)
        print("\n")
    elif(qualTeste=='quantidade registros'):
        contador = posts.find().count()
        restoMensagem = "Esperava " +str(numeroTotalDeRegistrosQueDeveriaTer) + " e obteve " + str(contador) + "!"
        if(contador==numeroTotalDeRegistrosQueDeveriaTer):
            print("Numero de registros correto!" + restoMensagem)
        else:
            erroPadraoTestes(qualTeste, "Número de registros incorreto! " + restoMensagem)
        print("\n")
    elif(qualTeste=='criptografia campo ano'):
        cipher = AESCipher('minhasenha123456')
        anosTeste = [2015,2016,2017]
        encontrou = [0,0,0]
        erro = 0

        for entrada in posts.find(): #busca todos os posts
            anoDecrypt = cipher.decrypt(entrada["ano"]).decode("utf-8") #descriptografa o ano somente, usando a chave indicada
            for i in range(0,len(anosTeste)):
                if(int(anoDecrypt)==int(anosTeste[i])): # se bater, funcionou
                    encontrou[i] += encontrou[i] + 1

        for i in range (0, len(encontrou)):
            if(encontrou[i] == 0):
                print("Erro ao descriptografar o ano "+ anosTeste[i])
                erro+=1
        if(erro==0):
            print("AES 256 funcionando bonitinho!")
        else:
            print("Parabéns, você não conseguiu usar uma biblioteca pronta para criptografar corretamente :)")
        print("\n")



def menu():
    global buscas

    def exibeRegistros(tamRetorno, listaRetorno):
        print("Total de registros encontrados: " + str(tamRetorno))
        simNao = input("Desejas ver os registros encontrados?(sim/nao)")
        if(simNao== ('sim' or 'Sim' or 's')):
            for entrada in listaRetorno:
                print(entrada)
        print("Retornando ao menu!")

    # Função que devolve a quantidade total
    # das buscas efetuadas sobre um array com texto
    # a ser pesquisado no db nosql, como busca textual
    def iteradorTweetCount(arrayIterar):
        valorRetorno = 0
        global buscas
        for entrada in arrayIterar:
            valorRetorno += buscas.tweetsCount(entrada)
        return valorRetorno

    while(1==1):
        print("  ------------------------------------------------ ")
        print("# -              Menu Principal                  - ")
        print("  ------------------------------------------------ ")
        print("1 - Buscar Tweets                                - ")
        print("2 - Efetuar as buscas pertinentes a hipótese     - ")
        print("3 - Testes pertinentes aos registros/banco       - ")
        print("  ------------------------------------------------ ")
        print("0 - Sair                                         - ")
        print("  ------------------------------------------------ ")
        escolha = input("Digite o número da opção escolhida")

        if(escolha=='1'): # BUSCAR NOS TWEETS

            opcao=-1
            while(opcao!=0):
                print("  -------------------- ")
                print("# - Menu de Buscas   - ")
                print("  -------------------- ")
                print("1 - Tweet            - ")
                print("2 - Ano              - ")
                print("3 - Mes              - ")
                print("  -------------------- ")
                print("0 - Retornar ao menu - ")
                print("  -------------------- ")
                opcao = input("Digite o número da opção escolhida ")

                if(opcao=='1'): #busca de tweet
                    texto = input("Digite o conteúdo o qual deseja buscar ")
                    i=0
                    if(texto!='' ):
                        listaRetorno = buscas.buscaTextual(texto)
                        tamListaRetorno = len(listaRetorno)
                        if(tamListaRetorno==0):
                            erroPadrao()
                        else:
                            exibeRegistros(tamListaRetorno, listaRetorno)

                elif(opcao=='2'): # busca do ano
                    ano = input("Digite o ano o qual deseja buscar:")
                    listaRetorno = buscas.ano(ano)
                    tamListaRetorno = len(listaRetorno)
                    if(tamListaRetorno==0):
                        erroPadrao()
                    else:
                        exibeRegistros(tamListaRetorno, listaRetorno)

                elif(opcao=='3'): #busca do mês
                    mes = input("Digite o mês o qual deseja buscar ")
                    listaRetorno = buscas.mes(mes)
                    tamListaRetorno = len(listaRetorno)
                    if(tamListaRetorno==0):
                        erroPadrao()
                    else:
                        exibeRegistros(tamListaRetorno, listaRetorno)
                elif(opcao=='0'):
                    print("Retornando ao menu!")
                    break
                else:
                    print("Digite uma escolha válida!")

        elif(escolha=='2'): # buscas pertinentes a hipótese

            buscaPickmanModel = {"Pickman's Model","Pickmans Model","pickman's Model","pickmans model"}
            buscaShadowOut = ["The Shadow Out of Time","the shadow out of time","Shadow Out of Time","shadow out of time"]
            buscaHaunter = ["The Haunter of the Dark","the haunter of the dark","Haunter of the Dark","haunter of the dark"]
            buscaDunwich = ["The Dunwich Horror","Dunwich Horror","the dunwich horror","dunwich horror"]
            buscaCthulhu = ["The Call of Cthulhu","Call of Cthulhu","the call of cthulhu","call of cthulhu"]

            qtdRetornos = [iteradorTweetCount(buscaPickmanModel),
                           iteradorTweetCount(buscaShadowOut),
                           iteradorTweetCount(buscaHaunter),
                           iteradorTweetCount(buscaDunwich),
                           iteradorTweetCount(buscaCthulhu)]

            print("\n\nConto:   | Quantidades: ")
            contos = ["Pickman’s Model","The Shadow Out of Time","The Haunter of the Dark","The Dunwich Horror","The Call of Cthulhu"]
            melhorConto=-1
            melhorContoQtd = -1
            for i in range(0,5):
                print(contos[i] + ":  " + str(qtdRetornos[i]))
                if(qtdRetornos[i] > melhorContoQtd):
                    melhorContoQtd = qtdRetornos[i]
                    melhorConto    = i

            print("\n")
            print("O conto mais mencionado em 50k tweets foi : " + contos[melhorConto] + "\n  Com " +str(qtdRetornos[melhorConto]) + " tweets sobre!" )
            print("\n")

        elif(escolha=='3'):
            print("---------------- TEST AREA 51----------------")
            tituloTestes = ['testar indices', 'quantidade registros', 'criptografia campo ano']
            for i in range(0,3):
                print("Efetuando teste "+str(i)+": "+tituloTestes[i])
                testes(tituloTestes[i])
        elif(escolha=='0'): # Sair do programinha
            print("Adios")
            return
        else:
            print("Escolha uma opcao valida!")




# chamada ao menuzinho
menu()
