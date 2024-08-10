import pandas as pd

# ---------------------------------------- #
# 1. TRATAMENTO INICIAL DOS DADOS;

# Criação dos DataFrames a partir dos arquivos
ratings = pd.read_csv('minirating.csv')
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
# 2.2. E2 - ÁRVORE DE PREFIXOS DE NOMES DE JOGADORES;
# 2.3. E3 - (para guardar avaliações);
# 2.4. E4 - (para guardar tags e jogadores relacionados);

# ---------------------------------------- #
# 3. FUNÇÕES DE BUSCA;

# 3.1. PREFIXOS DE NOMES DE JOGADORES;
# 3.2. REVISÕES DE JOGADORES;
# 3.3. MELHORES JOGADORES POR POSIÇÃO;
# 3.4. TAGS E JOGADORES RELACIONADOS;