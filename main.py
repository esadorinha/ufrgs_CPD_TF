import pandas as pd

# ---------------------------------------- #
# 0. FUNÇÕES DE USO GERAL;

# 0.1 RADIX SORT LSD: tamanho fixo de 7 dígitos, sendo 6 decimais; decrescente;
def radix_sort(list):

    for i in range(7):
        exp = 10**(i-6)
        esc = [[], [], [], [], [], [], [], [], [], []]

        for j in range(len(list)):
            buf = list[j]
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

HASH_RATINGS_SIZE = 13001 # lembrar de alterar esse valor caso trocar de Miniratings para Ratings

# Criação dos DataFrames a partir dos arquivos
ratings = pd.read_csv('ufrgs_CPD_TF\minirating.csv')
players = pd.read_csv('ufrgs_CPD_TF\players.csv')
nonfiltered_tags = pd.read_csv('ufrgs_CPD_TF\\tags.csv')
tags = nonfiltered_tags.dropna(subset=['tag']) # exlui tags vazias

# Adição das colunas de média e quantidade de avaliações por jogador ao DataFrame 'players'
sum_ratings = ratings.groupby('sofifa_id').sum()
mean_ratings = ratings.groupby('sofifa_id').mean().round(6)
del sum_ratings['user_id']
del mean_ratings['user_id']
new_columns = pd.merge(mean_ratings, sum_ratings, on='sofifa_id', how='left')
new_columns.columns = ['rating', 'num_ratings'] # renomeando colunas
new_columns['num_ratings'] = new_columns['num_ratings']/new_columns['rating'];
new_columns = new_columns.astype({'num_ratings': 'int'}) # casting
# (A média dos jogadores não avaliados foi considerada como 0)
players = pd.merge(players, new_columns, on='sofifa_id', how='left').fillna(0)

# Adição da coluna de médias ao Dataframe 'tags'
del new_columns['num_ratings']
tags = pd.merge(tags, new_columns, on='sofifa_id', how='left').fillna(0)

# Split na coluna de posições do Dataframe 'players'
players['player_positions'] = players['player_positions'].str.split(r',\s*')

# print(players)
# print(ratings)
# print(tags)
# players.to_csv('dados.csv', index=False)


# ---------------------------------------- #
# 2. ESTRUTURAS DE DADOS;

# 2.1. E1 - TABELA HASH DE JOGADORES;

hashPlayers = HashTable(24697) # 24697 numero primo mais prox de 25000, valor arbitrário para guardar quase 19 mil jogadores na hash
for index, row in players.iterrows(): # Usa iterrows (método pandas) para iterar sobre todas linhas do Dataframe
    player_id = row['sofifa_id'] # Guarda o Id do jogador para ser usado como Chave
    player_info = row.to_dict()  # Guarda todas informações do jogador como um dicionário
    hashPlayers.insert(player_id, player_info) # Insere cada jogador na HashTable


# 2.2. E2 - ÁRVORE TRIE DE PREFIXOS DE NOMES DE JOGADORES;

player_names = Trie()
for index, row in players.iterrows(): # Itera sobre todas linhas do Dataframe 'players'
    pl_id = row['sofifa_id']
    pl_name = row['long_name']
    player_names.insert(pl_name, pl_id)
# print(player_names.search_prefix('Fer'))


# 2.3. E3 - TABELA HASH DE AVALIAÇÕES POR USUARIO;

hashRatings = HashTable(HASH_RATINGS_SIZE)
for index, row in ratings.iterrows(): 
    user_id = row['user_id']
    user_info = row.to_dict()
    hashRatings.insert(user_id, user_info)


# 2.4. E4 - ÁRVORE TRIE DE JOGADORES POR TAG;
# em caso de problema, checar essa parte!!!

player_tags = Trie()
for row in tags.itertuples(index=False): # Itera sobre todas linhas do Dataframe 'tags'
    pl_id = row.sofifa_id
    pl_tag = row.tag
    pl_rate = row.rating
    player_tags.insert(pl_tag, (pl_id, pl_rate))

# EXEMPLO DE BUSCA:
# buf1 = list(set(player_tags.search_word('Brazil'))) # 'set' remove duplicatas
# buf2 = list(set(player_tags.search_word('Dribbler')))
# intersec = [i for i in buf1 if i in buf2]
# print(radix_sort(intersec))
# print(len(intersec))


# 2.5. E5 - TABELA DE JOGADORES POR POSIÇÃO; 

positions = ['GK', 'RB', 'CB', 'LB', 'CDM', 'CM', 'CAM', 'RM', 'LM', 'RW', 'LW', 'CF', 'ST']
position_listed = []

# Filtragem de jogadores por posição e número de avaliações
for pos in positions:
    # Detecta jogadores que possuem a posição e foram avaliados
    condition = (players['player_positions'].apply(lambda x: pos in x)) & (players['num_ratings'] > 0)
    # Cria e ordena uma lista de tuplas com os IDs e médias dos jogadores detectados
    new_list = players[condition].apply(lambda r: (r['sofifa_id'], r['rating']), axis=1).tolist()
    new_list = radix_sort(new_list)
    # Adiciona à lista de posições uma tupla com a posição e a lista de jogadores
    position_listed.append((pos, new_list))

# A estrutura atual é uma lista de tuplas, onde cada tupla contém uma sigla e outra lista de tuplas :)


# ---------------------------------------- #
# 3. FUNÇÕES DE BUSCA;

# 3.1. PREFIXOS DE NOMES DE JOGADORES;
# 3.2. REVISÕES DE JOGADORES;
# 3.3. MELHORES JOGADORES POR POSIÇÃO;
# 3.4. TAGS E JOGADORES RELACIONADOS;