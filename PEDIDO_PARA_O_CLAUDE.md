# Pedido para o Claude (copiar e colar no workshop)

Abra o Claude nesta pasta (`Demonstração`) e cole o texto abaixo. Ele descreve a tarefa por inteiro; todos os arquivos citados existem na pasta.

---

Escreva um script Python chamado `classificar.py`, nesta pasta, que classifica anúncios de vaga com um modelo de linguagem. Leia antes os arquivos que cito, porque eles definem a tarefa; não copie o conteúdo deles para dentro do código, leia-os em tempo de execução.

**Entrada**
- `1_banco_de_dados/vagas_amostra_1000.csv`: um anúncio por linha, colunas descritas em `1_banco_de_dados/dicionario_de_dados.md`. Leia todas as colunas como texto, com vazios como `""`.

**Uma chamada ao modelo por anúncio, com duas mensagens**
- Mensagem de sistema: o conteúdo de `2_prompt/prompt_sistema.txt`, sem alterar.
- Mensagem do usuário: o molde `2_prompt/modelo_mensagem_usuario.txt`, trocando cada `{coluna}` pelo valor da coluna do anúncio. Se o valor estiver vazio, retire a linha inteira. O arquivo `2_prompt/mensagem_do_usuario_exemplo.txt` mostra o resultado esperado para um anúncio.

**API**
- Use os valores de `configuracao_api.json`: endereço, modelo, temperatura, máximo de tokens, formato de resposta, número de tentativas e de chamadas simultâneas. A interface é a do SDK `openai` (chat completions).
- A chave vem da variável de ambiente indicada nesse arquivo, ou de um arquivo `.env` na pasta. Nunca escreva a chave no código nem a mostre na tela. Se não houver chave, pare com uma mensagem clara.

**Resposta**
- O modelo devolve um JSON. Confira cada resposta contra `3_schema_json/schema_saida.json`: campos obrigatórios, nenhum campo a mais, tipos e opções permitidas. `3_schema_json/exemplo_de_resposta.json` é um exemplo válido.
- Resposta fora do formato ou falha de rede: repita a chamada, até o número de tentativas configurado, com espera crescente. Se continuar falhando, grave a linha com a coluna `erro` preenchida e os outros campos vazios. Não corrija nem invente valores.

**Saída**
- `4_saida/minha_saida.csv`, em UTF-8 com BOM, com exatamente estas colunas: `vacancy_id, vaga_ti, justificativa_ti, skills, temas, tokens_in, tokens_out, erro`.
- `skills` e `temas` são as listas do JSON unidas por `"; "`. `tokens_in` e `tokens_out` vêm do campo de uso da resposta da API.
- Grave cada linha assim que a resposta chegar. Ao rodar de novo, não chame o modelo para os anúncios que já têm resposta sem erro.

**Opções de linha de comando**
- `--simular`: mostra a mensagem de sistema e a mensagem do usuário do primeiro anúncio e termina, sem chamar a API.
- `--limite N`: classifica só os N primeiros anúncios pendentes.

**Ao terminar**
- Mostre quantos anúncios foram classificados, quantos erros, os tokens de entrada e de saída e o custo estimado pelo preço de `configuracao_api.json`.
- Não rode o script com a API sem eu pedir. Rode apenas `python classificar.py --simular` e compare a mensagem gerada com `2_prompt/mensagem_do_usuario_exemplo.txt` (procure o mesmo anúncio pelo título).

---

## Depois que o script existir

```bash
python classificar.py --simular     # confere as mensagens, sem custo
python classificar.py --limite 5    # 5 anúncios, menos de 1 centavo
python conferir_saida.py            # confere o formato e compara com a rodada de referência
python classificar.py               # os 1.000 anúncios, cerca de US$ 0,14
python conferir_saida.py
```

Se algo der errado na hora, há um script pronto em `referencia/classificar_referencia.py`, que faz a mesma coisa e grava no mesmo arquivo de saída.
