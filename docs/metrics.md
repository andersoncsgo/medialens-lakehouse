# Métricas do MovieLens

- **Nota mensal.** Soma das estrelas dividida pela quantidade de avaliações válidas do filme naquele mês UTC.
- **Nota acumulada.** Soma das estrelas até o mês dividida pela quantidade de avaliações até o mesmo mês. Cada avaliação tem o mesmo peso.
- **Volume mensal.** Quantidade de eventos válidos registrados no mês. A edição termina em 20/07/2023, por isso julho de 2023 é parcial.
- **Nota por gênero.** Soma das estrelas dos filmes do gênero dividida pela quantidade de avaliações desses filmes. Filmes com vários gêneros contribuem para cada gênero.
- **Reconciliação.** As linhas Bronze correspondem às linhas de origem válidas mais as rejeitadas. A contagem de eventos válidos corresponde à soma das avaliações tanto na Gold por filme quanto na Gold mensal.

O painel usa a escala original de 0,5 a 5 estrelas. A nota reflete os usuários e o período representados nesta edição.
