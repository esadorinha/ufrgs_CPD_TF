import pandas as pd
from tabulate import tabulate
from os import system
import re


# ---------------------------------------- #
# 0. FUNÇÕES DE USO GERAL;

# 0.1 RADIX SORT LSD: tamanho fixo de 7 dígitos, sendo 6 decimais; decrescente;
def radix_sort(list):

    for i in range(7):
        exp = 10**(i-6)
        esc = [[], [], [], [], [], [], [], [], [], []]

        for j in range(len(list)):
            buf = list[j]   # a lista é de tuplas (id, rating)
            d = int(buf[1]/exp) % 10
            esc[d].append(buf)
        
        list = sum(esc[::-1], [])
    
    return list

# 0.2 CRIAÇÃO DA HASH TABLE 
class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(size)]

    def hash_function(self, key):
        return key % self.size

    def insert(self, key, value):
        hash_key = int(self.hash_function(key)) 
        bucket = self.table[hash_key]

        for i, kv in enumerate(bucket):
            k, _ = kv
            if key == k:
                bucket[i] = (key, value)  # Update existing key
                return
        bucket.append((key, value))  # Insert new key

    def search(self, key):
        hash_key = self.hash_function(key)
        bucket = self.table[hash_key]
        for k, v in bucket:
            if key == k:
                return v
        return None

# 0.3 CRIAÇÃO DA ÁRVORE TRIE:
class TrieNode:
    def __init__(self, c):
        self.char = c
        self.children = []
        self.ID = []

class Trie:
    def __init__(self):
        self.raiz = TrieNode("")

    def find_node(self, node, c):
        for son in node.children:
            if son.char == c:
                return son
        
        return None

    def insert(self, word, ID):
        node_cur = self.raiz

        for c in word:
            if not node_cur.children:
                node_cur.children.append(TrieNode(c))
                node_cur = node_cur.children[0]
            else:
                node_buf = self.find_node(node_cur, c)
                if node_buf == None:
                    # insere nodo 'c' na árvore na posição correta
                    i = 0
                    while i < len(node_cur.children) and c >= node_cur.children[i].char:
                        i += 1
                    node_cur.children.insert(i, TrieNode(c))
                    node_cur = node_cur.children[i]
                else:
                    node_cur = node_buf

        node_cur.ID.append(ID)
                    
    def search_word(self, word):
        node_cur = self.raiz

        for c in word:
            node_buf = self.find_node(node_cur, c)
            if node_buf == None:
                return None
            else:
                node_cur = node_buf
        
        if not node_cur.ID:
            return None
        else:
            return node_cur.ID
        
    def list_words(self, node, semiword):
        semiword = semiword + node.char

        word_list = node.ID
        if node.children:
            for son in node.children:
                word_list = word_list + self.list_words(son, semiword)

        return word_list

    def search_prefix(self, word):
        node_cur = self.raiz

        for c in word:
            node_buf = self.find_node(node_cur, c)
            if node_buf == None:
                return None
            else:
                node_cur = node_buf

        prefix_list = []
        for son in node_cur.children:
            prefix_list = prefix_list + self.list_words(son, "")
        
        return prefix_list
    


# ---------------------------------------- #
# 1. TRATAMENTO INICIAL DOS DADOS;

#HASH_RATINGS_SIZE = 13001 # lembrar de alterar esse valor caso trocar de Miniratings para Ratings
HASH_RATINGS_SIZE = 180043 # substituir quando for trabalhar com rating.csv
#MIN_RATING_COUNT = 0
MIN_RATING_COUNT = 1000 # substituir quando for trabalhar com rating.csv

# Criação dos DataFrames a partir dos arquivos
#ratings = pd.read_csv('ufrgs_CPD_TF\minirating.csv')
ratings = pd.read_csv('ufrgs_CPD_TF\\rating.csv')
players = pd.read_csv('ufrgs_CPD_TF\players.csv')
nonfiltered_tags = pd.read_csv('ufrgs_CPD_TF\\tags.csv')
tags = nonfiltered_tags.dropna(subset=['tag']) # exlui tags vazias

# Adição das colunas de média e quantidade de avaliações por jogador ao DataFrame 'players'
mean_ratings = ratings.groupby('sofifa_id').mean().round(6)
count = ratings.groupby('sofifa_id').size() 
count.name = 'count'
del mean_ratings['user_id']
new_columns = pd.merge(mean_ratings, count, on='sofifa_id', how='left')
# (A média dos jogadores não avaliados foi considerada como 0)
players = pd.merge(players, new_columns, on='sofifa_id', how='left').fillna(0)
players['count'] = players['count'].astype(int)

# Adição da coluna de médias ao Dataframe 'tags'
del new_columns['count']
tags = pd.merge(tags, new_columns, on='sofifa_id', how='left').fillna(0)



# ---------------------------------------- #
# 2. ESTRUTURAS DE DADOS;

# 2.1. E1 - TABELA HASH DE JOGADORES;

hash_players = HashTable(24697) # 24697 numero primo mais prox de 25000, valor arbitrário para guardar quase 19 mil jogadores na hash
for row in players.itertuples(index=False): # Usa itertuples para iterar sobre todas linhas do Dataframe
    pl_id = row.sofifa_id # Guarda o Id do jogador para ser usado como Chave
    pl_info = list(row)  # Guarda todas informações do jogador como uma lista
    hash_players.insert(pl_id, pl_info) # Insere cada jogador na HashTable


# 2.2. E2 - ÁRVORE TRIE DE PREFIXOS DE NOMES DE JOGADORES;

player_names = Trie()
for row in players.itertuples(index=False): # Itera sobre todas linhas do Dataframe 'players'
    pl_id = row.sofifa_id
    pl_name = row.long_name
    player_names.insert(pl_name, pl_id)
# print(player_names.search_prefix('Fer'))


# 2.3. E3 - TABELA HASH DE AVALIAÇÕES POR USUÁRIO;

# Agrupa as avaliações de cada usuário em uma lista de listas:
user_ratings = ratings.groupby('user_id').apply(lambda x: [x.name, x.iloc[:, 1:].values.tolist()]).tolist()
hash_ratings = HashTable(HASH_RATINGS_SIZE)
for user in user_ratings: 
    user_id = user[0]
    user_info = user[1] # Lista de listas '[sofifa_id, avaliação do user]'
    hash_ratings.insert(user_id, user_info) # Insere a lista de avaliações de cada usuário na HashTable


# 2.4. E4 - ÁRVORE TRIE DE JOGADORES POR TAG;

player_tags = Trie()
for row in tags.itertuples(index=False): # Itera sobre todas linhas do Dataframe 'tags'
    pl_id = row.sofifa_id
    pl_tag = row.tag
    pl_rate = row.rating
    player_tags.insert(pl_tag, (pl_id, pl_rate))


# 2.5. E5 - TABELA DE JOGADORES POR POSIÇÃO; 

positions = ['GK', 'RB', 'CB', 'LB', 'CDM', 'CM', 'CAM', 'RM', 'LM', 'RW', 'LW', 'CF', 'ST']
position_listed = []

# Split na coluna de posições do Dataframe 'players'
players['player_positions'] = players['player_positions'].str.split(r',\s*')

# Filtragem de jogadores por posição e número de avaliações
for pos in positions:
    # Detecta jogadores que possuem a posição e foram avaliados
    condition = (players['player_positions'].apply(lambda x: pos in x)) & (players['count'] > MIN_RATING_COUNT)
    # Cria e ordena uma lista de tuplas com os IDs e médias dos jogadores detectados
    new_list = players[condition].apply(lambda r: (r['sofifa_id'], r['rating']), axis=1).tolist()
    new_list = radix_sort(new_list)
    # Adiciona à lista de posições uma tupla com a posição e a lista de jogadores
    position_listed.append((pos, new_list))

# A estrutura atual é uma lista de tuplas, onde cada tupla contém uma sigla e outra lista de tuplas :)



# ---------------------------------------- #
# 3. FUNÇÕES DE BUSCA E EXIBIÇÃO;

# 3.1. PREFIXOS DE NOMES DE JOGADORES;  - Pedro
#      => sofifa_id,short_name,long_name,player_positions,rating,count
def player_prefix_query1(prefix, filename):
    ids = player_names.search_prefix(prefix)
    if not ids:
        print('=> Busca sem resultados;')
        return 0
    
    ordered_pl_list = []    # cria lista de tuplas onde cada tupla é
                            # 1. Informações do jogador
                            # 2. Rating Global
    for pl_id in ids:
        pl_info = hash_players.search(pl_id)
        ordered_pl_list.append((pl_info[:4] + pl_info[7:], pl_info[7]))
    
    ordered_pl_list = radix_sort(ordered_pl_list)

    # Cria .html com a tabela de resultados:
    headers = ['sofifa_id','short_name','long_name','player_positions','rating','count']
    data = []

    for player in ordered_pl_list:
        data.append(player[0])

    player_prefix = pd.DataFrame(data, columns=headers)
    player_prefix.to_html(filename+'.html', index=False)

    print('=> Arquivo HTML criado!')

    



# 3.2. REVISÕES DE JOGADORES;

def user_reviews_query2(user_id, filename):
    rating_list = hash_ratings.search(user_id)
    if not rating_list:
        print('=> Usuário não encontrado;')
        return 0
    
    rating_ordered = []
    for rating in rating_list:
        pl_id = int(rating[0])
        gb_rating = hash_players.search(pl_id)[7]
        rating_ordered.append((int(rating[0]), gb_rating, rating[1]))

    # Ordena em função do rating global
    rating_ordered = radix_sort(rating_ordered)

    # Ordena em função da avaliação do usuário, mantendo estável
    esc = [[], [], [], [], [], []]
    for rating in rating_ordered:
        d = int((rating[2] % 1)*10)
        esc[d].append(rating) 
    rating_ordered = sum(esc[::-1], [])

    esc = [[], [], [], [], [], []]
    for rating in rating_ordered:
        esc[int(rating[2])].append(rating)
    rating_ordered = sum(esc[::-1], [])
    rating_ordered = rating_ordered[:20]

     # Se a busca não obtiver resultado, finaliza
    if not rating_ordered:
        print('=> Busca sem resultados;')
        return 0

    # Cria .html com a tabela de resultados:
    headers = ['sofifa_id','short_name','long_name','global_rating','count','user_rating']
    data =[]
    for rating in rating_ordered:
        pl_id = int(rating[0])
        pl_info = hash_players.search(pl_id)
        data.append(pl_info[:3] + pl_info[7:9] + [rating[2]])
    user_reviews = pd.DataFrame(data, columns=headers)
    user_reviews.to_html(filename+'.html', index=False)

    print('=> Arquivo HTML criado!')


# 3.3. MELHORES JOGADORES POR POSIÇÃO;

def top_players_query3(N, pos, filename):
    i = 0;
    searching = 1;
    while searching and i<len(positions):
        if pos == position_listed[i][0]:
            player_list = [tuple[0] for tuple in position_listed[i][1]]
            searching = 0
        i += 1
    
    if searching == 1:
        print('=> Posição inválida!')
        return 0
    elif len(player_list) <= N:
        ids = player_list
    else:
        ids = player_list[0:N]

     # Se a busca não obtiver resultado, finaliza
    if not ids:
        print('=> Busca sem resultados;')
        return 0

    # Cria .html com a tabela de resultados:
    headers = ['sofifa_id','short_name','long_name','player_positions','nationality','club_name','league_name','rating','count']
    data = []
    for pl_id in ids:
        pl_info = hash_players.search(pl_id)
        data.append(pl_info)
    top_players = pd.DataFrame(data, columns=headers)
    top_players.to_html(filename+'.html', index=False)

    print('=> Arquivo HTML criado!')


# 3.4. TAGS E JOGADORES RELACIONADOS;

def tagged_players_query4(tag_list, filename):
    cj = set(player_tags.search_word(tag_list[0]))
    for tag in tag_list[1:]:
        buf = set(player_tags.search_word(tag))
        cj = cj & buf
    ids = radix_sort(list(cj))
    ids = [tuple[0] for tuple in ids]
    
    # Se a busca não obtiver resultado, finaliza
    if not ids:
        print('=> Busca sem resultados;')
        return 0

    # Cria .html com a tabela de resultados:
    headers = ['sofifa_id','short_name','long_name','player_positions','nationality','club_name','league_name','rating','count']
    data = []
    for pl_id in ids:
        pl_info = hash_players.search(pl_id)
        data.append(pl_info)
    tagged_players = pd.DataFrame(data, columns=headers)
    tagged_players.to_html(filename+'.html', index=False)

    print('=> Arquivo HTML criado!')
    


# ---------------------------------------- #
# 4. INTERFACE DE USO;

system('cls')
query = '1'

while query != '0':  
    print('# ---------------------------------------- #\n\t\t    MENU\n# ---------------------------------------- #')
    print('Consulta por nome: digite \"player<nome/prefixo buscado>\";')
    print('Consulta por usuário: digite \"user<ID do usuário buscado>\";')
    print('Consulta por posição: digite \"top<número><posição entre apóstrofes>\";')
    print('Consulta por tag: digite \"tags<tags entre apóstrofes>\";')
    print('Para sair, digite \'0\';\n')

    query = input()
    if query == '0':
        print('=> Sair selecionado')
    elif query[:3] == 'top':        # Lê, por exemplo "top10'GK'";
        query_data = query[3:].split('\'', 1)
        if str.isdigit(query_data[0]):
            query_num = int(query_data[0])
            query_pos = query_data[1][:-1]
            top_players_query3(query_num, query_pos, query)
        else:
            print('=> Número inválido;')
    elif query[:4] == 'tags':       # Lê, por exemplo "tags 'Brazil' 'Dribbler'"; a falta das apóstrofes ocasiona ERRO;
        query_data = re.findall(r"'(.*?)'", query[4:])
        tagged_players_query4(query_data, query)
    elif query[:4] == 'user':       # Lê, por exemplo, "user213908";
        query_data = query[4:]
        if str.isdigit(query_data):
            user_reviews_query2(int(query_data), query)
        else:
            print('=> ID inválido;')
    elif query[:6] == 'player':     # Lê, por exemplo, ____;
        query_data = query[6] + query[7:].lower()
        print('player') 
        player_prefix_query1(query_data, query)

    else:
        print('=> Busca inválida;')

    print('\nPressione ENTER para continuar...')
    buf = input()
    system('cls')
system('cls')
