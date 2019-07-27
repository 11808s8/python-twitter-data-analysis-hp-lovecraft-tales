# Aplicação de Validação de Hipótese sobre contos do autor H.P. Lovecraft com base em Tweets

Esta aplicação fora desenvolvida para a disciplina de Organização de Arquivos, da Universidade de Caxias do Sul.

Autor: [Adriano Gomes da Silva](https://github.com/11808s8) (adrianogsss@gmail.com)

Colaboradores: Marçal Nunes de Oliveira e [Venicius Bregalda](https://github.com/venicius12).

Acesse [esta apresentação](./extracao-dados-twitter.pdf) para saber mais sobre o projeto.


## Requerimentos
 Python >= 3.6
 
 MongoDB >= 2.6.10

## Como Rodar
Instale os pacotes necessários por meio do arquivo requirements.txt através do comando
```console
pip3 install -r requirements.txt
```

Após isto, levante o banco com o seguinte comando:
```console
mongorestore --drop -d trabalho <Diretório onde está a pasta dump>
```
Por fim, só executar o projeto através do comando:
```console
python3 lovecraft.py
```
### Bônus:
Há um script no repositório, chamado, createvirtualenv.sh, o qual, executado em máquinas unix (com o virtualenv instalado), criará um ambiente virtual Python3 para instalação de pacotes sem que os mesmos sejam instalados no ambiente global da máquina.
Após executá-lo através do comando
```console
./createvirtualenv.sh
```
Você precisará ativá-lo por meio do comando
```console
source .venv/bin/activate
```
E então seguir o passo-a-passo descrito no tópico Como Rodar, acima.


Para mais informações sobre ambientes virtuais, [clique aqui](https://pt.stackoverflow.com/questions/209384/instalar-com-pip-atrav%c3%a9s-do-arquivo-requirements-txt-dentro-do-virtualenv/209511#209511).
