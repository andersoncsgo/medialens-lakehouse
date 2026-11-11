# Decisões do projeto

| Decisão | Motivo |
| --- | --- |
| Usar o MovieLens como fonte de avaliações | Cada evento tem seu próprio horário, o que permite reconstruir a trajetória observada do mesmo filme. |
| Fixar a edição de 20/07/2023 | Mantém entrada, resultados e testes reproduzíveis. |
| Identificar filmes pelo ID MovieLens | Preserva títulos homônimos e permite registrar a incerteza dos vínculos IMDb. |
| Materializar o histórico por mês | Mantém as consultas do painel sobre uma agregação com contagens reconciliáveis. |
| Mostrar volume ao lado da nota | Permite interpretar mudanças de nota com a quantidade de avaliações do período. |
