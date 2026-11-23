# Demonstração: classificar anúncios de vaga com um modelo de linguagem

Esta pasta mostra, do começo ao fim, como usamos um modelo de linguagem (LLM) para classificar anúncios de emprego do InfoJobs. Traz uma amostra de 1.000 anúncios, as instruções dadas ao modelo, o formato da resposta e a planilha com o resultado. O script que chama o modelo é escrito durante o workshop, a partir destes arquivos.

## O que o modelo faz

Para cada anúncio, fazemos uma chamada ao modelo. Ele lê o anúncio e responde duas coisas:

1. **A função principal da vaga é de TI?** Responde `ti`, `telecom_operacional` ou `nao`, com uma justificativa curta.
2. **Que habilidades técnicas o anúncio cita?** Devolve duas listas: `skills`, com as ferramentas e métodos que têm nome (Excel, SAP, Python), e `temas`, com exigências técnicas sem nome de ferramenta ("suporte a usuários").

O modelo só lê e extrai. O agrupamento das habilidades em categorias é feito depois, por regras fixas, sem modelo.

## Como as peças se ligam

```
1_banco_de_dados/vagas_amostra_1000.csv ──┐
   (uma linha = um anúncio)               │  cada {coluna} do molde é uma coluna do banco
2_prompt/modelo_mensagem_usuario.txt ─────┴─► mensagem do usuário ──┐
2_prompt/prompt_sistema.txt ────────────────► mensagem de sistema ──┼─► modelo ─► JSON
configuracao_api.json ──────────────────────► modelo e parâmetros ──┘             │
3_schema_json/schema_saida.json ────────────► confere o JSON ◄────────────────────┘
                                                    │
                                                    ▼
4_saida/minha_saida.csv   (uma linha = um anúncio; campos do JSON viram colunas)
```

- O **prompt de sistema** pede um JSON com quatro campos: `vaga_ti`, `justificativa_ti`, `skills` e `temas`.
- O **schema** descreve esses mesmos quatro campos, com os tipos e as três opções de `vaga_ti`.
- A **planilha de saída** tem uma coluna para cada campo, mais o código do anúncio, que é o mesmo do banco.

## O que há na pasta

| Pasta ou arquivo | Conteúdo |
|---|---|
| `1_banco_de_dados/vagas_amostra_1000` (.csv e .xlsx) | Os 1.000 anúncios |
| `1_banco_de_dados/dicionario_de_dados.md` | O que é cada coluna e quais vão para o modelo |
| `2_prompt/prompt_sistema.txt` | As instruções dadas ao modelo, iguais para todos os anúncios |
| `2_prompt/modelo_mensagem_usuario.txt` | O molde da mensagem com o anúncio; cada `{coluna}` é uma coluna do banco |
| `2_prompt/mensagem_do_usuario_exemplo.txt` | O molde preenchido com um anúncio |
| `3_schema_json/schema_saida.json` | O formato obrigatório da resposta, com a descrição de cada campo |
| `3_schema_json/exemplo_de_resposta.json` | A resposta do modelo para o anúncio de exemplo |
| `configuracao_api.json` | Modelo, endereço do serviço, parâmetros da chamada e preço |
| `.env.example` | Modelo do arquivo onde se guarda a chave de acesso |
| `4_saida/saida_classificacao_1000` (.csv e .xlsx) | O resultado de referência: uma linha por anúncio, com a resposta ao lado do texto |
| `4_saida/respostas_do_modelo_1000.jsonl` | As mesmas respostas em JSON, uma por linha, como o modelo as devolve |
| `PEDIDO_PARA_O_CLAUDE.md` | O texto a colar no Claude para ele escrever o script, e os comandos para rodar |
| `conferir_saida.py` | Confere a planilha gerada e compara com a de referência; não chama o modelo |
| `referencia/` | Um script pronto, para o caso de algo falhar na hora, e o prompt original de agosto |

## Roteiro do workshop

1. Abrir o banco no Excel e ler dois ou três anúncios.
2. Ler o prompt de sistema e o exemplo de mensagem do usuário.
3. Ler o schema e o exemplo de resposta.
4. Abrir o Claude nesta pasta e colar o texto de `PEDIDO_PARA_O_CLAUDE.md`.
5. Rodar o script gerado com `--simular`, depois com `--limite 5`, depois inteiro.
6. Rodar `python conferir_saida.py` e abrir a planilha.

## Como ler a planilha de saída

| Coluna | Conteúdo |
|---|---|
| `vacancy_id` | Código do anúncio, o mesmo do banco |
| `vaga_ti` | `ti`, `telecom_operacional` ou `nao` |
| `justificativa_ti` | O motivo dado pelo modelo; serve para conferência humana |
| `skills` | Habilidades com nome, separadas por ponto e vírgula |
| `temas` | Exigências técnicas sem nome de ferramenta, separadas por ponto e vírgula |
| `tokens_in`, `tokens_out` | Tamanho do que foi enviado e do que voltou; é o que define o custo |
| `erro` | Vazio quando deu certo; se não, o motivo da falha |

A planilha de referência traz também o título, a empresa e a descrição, para comparar a resposta com o texto. Um bom exercício é filtrar `vaga_ti = nao` com `skills` preenchido: são as vagas que usam ferramentas digitais sem serem de TI (vendedor com CRM, professor de musculação com Excel).

## Sobre a amostra

- Os 1.000 anúncios foram sorteados da base nacional já classificada: 200 de TI, 50 de telecomunicações operacionais e 750 das demais.
- **A amostra não é representativa.** Na base inteira, as vagas de TI são 1,7% e as de telecomunicações 0,5%. Aumentamos essas duas para que apareçam exemplos suficientes de cada resposta. Não use a amostra para calcular proporções.
- As respostas de referência são as que o modelo deu na classificação da base nacional, em agosto de 2026. Não foram revisadas por pessoas e contêm erros.
- Nenhum anúncio desta amostra faz parte das amostras de anotação humana do projeto.

## Preparação antes de rodar

É preciso ter Python 3.10 ou mais novo e uma chave de acesso do OpenRouter (openrouter.ai), o serviço que dá acesso ao modelo.

```bash
pip install pandas openai openpyxl
```

A chave fica fora do código. Há duas formas:

- copiar `.env.example` para um arquivo chamado `.env` e colar a chave nele; ou
- definir a variável de ambiente `OPENROUTER_API_KEY` no terminal.

A chave nunca deve ser escrita no código, enviada por e-mail ou colocada em pasta compartilhada. Ao compartilhar esta pasta, não inclua o arquivo `.env`.

**Custo:** os 1.000 anúncios somaram 1,29 milhão de tokens de entrada e 0,23 milhão de saída, cerca de US$ 0,14 pelo preço usado no projeto (US$ 0,08 e US$ 0,16 por milhão). Confira o preço atual antes de rodar bases grandes.

## Configuração usada

| Item | Valor | Por quê |
|---|---|---|
| Modelo | `deepseek/deepseek-v4-flash`, via OpenRouter | Barato e suficiente para a tarefa |
| Temperatura | 0 | Reduz a variação entre rodadas |
| Saída em JSON | `response_format = json_object` | O provedor garante que a resposta é um JSON |
| Tamanho máximo da resposta | 1.500 tokens | A resposta é curta |
| Tentativas | 3 | Cobre falhas de rede e respostas fora do formato |

## Cuidados

- **A resposta pode mudar.** Mesmo com temperatura 0, rodar de novo pode dar respostas um pouco diferentes, e o modelo muda quando o fornecedor o atualiza. Guarde sempre a saída junto com a data, o modelo e o prompt usados.
- **O modelo erra.** Antes de usar o resultado, compare uma amostra com a leitura de pessoas.
- **O prompt é a definição.** Mudar uma frase das instruções muda o que está sendo medido. Toda mudança deve ser registrada, e a base, classificada de novo.
- **A referência não é gabarito.** `conferir_saida.py` compara a sua rodada com a de agosto, que é só outra rodada do mesmo modelo. Diferenças pequenas são esperadas.
- **Não envie dados pessoais.** Os anúncios são públicos. Para outros tipos de texto, verifique antes se podem ser enviados a um serviço externo.

## Diferenças em relação à rodada de agosto

- **Uma frase do prompt foi corrigida.** O original dizia "extraia SEMPRE, mesmo se vaga_ti=false", mas as respostas válidas são `ti`, `telecom_operacional` e `nao`. Na rodada de agosto, parte das respostas veio como `true` ou `false` e foi convertida pelo script. O prompt desta pasta diz `mesmo se "vaga_ti" for "nao"`. O texto original está em `referencia/prompt_sistema_original_agosto.txt`.
- **A conferência do formato é mais rígida.** Aqui, resposta fora das três opções é erro e a chamada é repetida.
- **A mensagem do usuário foi simplificada.** A área do InfoJobs já vem numa coluna do banco, em vez de ser extraída da descrição pelo script.
- **Nada foi rodado de novo.** As respostas de referência vêm da rodada de agosto. O script de referência foi testado até a montagem das mensagens, e o conferidor, com as respostas de referência.
