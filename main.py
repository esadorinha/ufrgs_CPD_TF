import pandas as pd

# ---------------------------------------- #
#        HASH TABLE DE USO GERAL
# ---------------------------------------- #
class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(size)]

    def hash_function(self, key):
        return key % self.size

    def insert(self, key, value):
        hash_key = self.hash_function(key)
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

# ---------------------------------------- #
# 1. TRATAMENTO INICIAL DOS DADOS;

# Criação dos DataFrames a partir dos arquivos
ratings = pd.read_csv('minirating.csv')
HASH_RATINGS_SIZE = 13001   # lembrar de alterar esse valor caso trocar de Miniratings para Ratings
players = pd.read_csv('players.csv')
tags = pd.read_csv('tags.csv')

# Ajuste do DataFrame 'players' (acrescenta a coluna de avaliação média do jogador)
mean_ratings = ratings.groupby('sofifa_id').mean()
del mean_ratings['user_id']
# (A média dos jogadores não avaliados foi considerada como 0)
players = pd.merge(players, mean_ratings, on='sofifa_id', how='left').fillna(0)

print(players)
print(ratings)
print(tags)
# players.to_csv('dados.csv', index=False)


# ---------------------------------------- #
# 2. ESTRUTURAS DE DADOS;

# 2.1. E1 - TABELA HASH DE JOGADORES;
hashPlayers = HashTable(24697) # 24697 numero primo mais prox de 25000, valor arbitrário para guardar quase 19 mil jogadores na hash

for index, row in players.iterrows(): # Usa iterrows (método pandas) para iterar sobre todas linhas do Dataframe
    player_id = row['sofifa_id'] # Guarda o Id do jogador para ser usado como Chave
    player_info = row.to_dict()  # Guarda todas informações do jogador como um dicionário
    hashPlayers.insert(player_id, player_info) # Insere cada jogador na HashTable

# 2.2. E2 - ÁRVORE DE PREFIXOS DE NOMES DE JOGADORES;
# 2.3. E3 - TABELA HASH DE AVALIAÇÕES POR USUARIO;

hashRatings = HashTable(HASH_RATINGS_SIZE)

for index, row in ratings.iterrows(): #mesma coisa da inserção acima
    user_id = row['user_id']
    user_info = row.to_dict()
    hashRatings.insert(user_id, user_info)


# 2.4. E4 - (para guardar tags e jogadores relacionados);

# ---------------------------------------- #
# 3. FUNÇÕES DE BUSCA;

# 3.1. PREFIXOS DE NOMES DE JOGADORES;
# 3.2. REVISÕES DE JOGADORES;
# 3.3. MELHORES JOGADORES POR POSIÇÃO;
# 3.4. TAGS E JOGADORES RELACIONADOS;
