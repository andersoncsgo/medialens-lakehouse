# Decisões técnicas

| Decisão | Razão | Quando rever |
| --- | --- | --- |
| Começar por uma página da TMDB | É suficiente para demonstrar o fluxo da API ao painel e observar a mudança de composição da amostra. | Aumentar a cobertura se a pergunta analítica exigir e após revisar limites e termos. |
| Preservar a resposta na Bronze | Permite rastrear os registros e reprocessar sem consultar a API novamente. | Revisar política de retenção à medida que o histórico crescer. |
| Uma identidade de lote por execução do job | Separa reparo de uma execução da coleta de um novo snapshot. | Se houver múltiplos escritores, revisar concorrência e integridade do contrato de chaves. |
| Reconstruir Silver e Gold em batch | Com o volume atual, a abordagem é pequena, fácil de reproduzir e mantém o histórico na Bronze. | Medir duração e custo para decidir quando migrar para cargas incrementais e backfill explícito. |
| Comparar as duas últimas coletas disponíveis | A métrica tem uma definição simples e rastreável. | Se for preciso comparar filmes em janelas equivalentes, definir coortes e janelas fixas. |
| Validar a Gold antes de substituir a tabela | Evita publicar chaves duplicadas, diferenças inconsistentes ou perda de cobertura. | Evoluir para alertas de atraso e anomalia quando houver uma frequência operacional acordada. |

A próxima prioridade é acompanhar os mesmos filmes TMDB em dias diferentes, medir a cobertura do vínculo com MovieLens e demonstrar um reparo no Databricks. O [fluxo MovieLens](movielens.md) trata a edição histórica como um snapshot de arquivos e usa materialized views batch.
