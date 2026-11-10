# Fontes e condições de uso

A integração **TMDB** consulta [filmes populares](https://developer.themoviedb.org/reference/movie-popular-list) e usa o ID TMDB como chave do filme. Mantém a nota na escala original, a contagem de votos e o instante da coleta. Popularidade e contagem de votos representam coisas diferentes.

O job usa uma página por execução e trata HTTP 429 com tentativas limitadas e espera. Antes de ampliar a coleta, revise [limites da API](https://developer.themoviedb.org/docs/rate-limiting). As respostas brutas ficam na Bronze. Arquivos brutos e credenciais ficam fora do Git.

## Atribuição

O painel usa dados da [TMDB](https://www.themoviedb.org/). Para publicar um painel com esses dados, confira a [FAQ de uso e atribuição](https://developer.themoviedb.org/docs/faq) e aplique os requisitos da TMDB ao material publicado, incluindo logo aprovado e o aviso abaixo.

> This product uses the TMDB API but is not endorsed or certified by TMDB.

## MovieLens

O fluxo [MovieLens Latest Full](movielens.md) usa a edição de 2023-07-20 fornecida pelo GroupLens, com avaliações históricas de 0,5 a 5 estrelas. O vínculo usa o `tmdbId` documentado pelo GroupLens e preserva candidatos ambíguos. Confira os [termos e a citação oficial](https://files.grouplens.org/datasets/movielens/ml-latest-README.html) antes de publicar dados ou resultados derivados.
