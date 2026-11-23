# Dicionário de dados: vagas_amostra_1000

Um anúncio por linha, 1.000 linhas. Arquivo CSV em UTF-8 com BOM, separado por vírgula (abre direto no Excel); a mesma tabela está em `.xlsx`. Todas as colunas são texto.

| Coluna | Conteúdo | Vazios | Vai para o modelo? |
|---|---|---|---|
| `vacancy_id` | Código do anúncio no InfoJobs. É a chave: liga o banco à planilha de saída | 0 | Não |
| `area_infojobs` | Área declarada pelo anunciante, tirada do começo da descrição | 34 | Sim |
| `title` | Título do anúncio | 0 | Sim |
| `company` | Empresa (vazio quando o anúncio é confidencial) | 84 | Sim |
| `location` | Cidade e estado | 10 | Sim |
| `work_model` | Presencial, híbrido ou remoto | 0 | Sim |
| `experience` | Experiência pedida | 457 | Sim |
| `education` | Escolaridade pedida | 0 | Sim |
| `salary` | Salário como aparece no anúncio (muitas vezes "A combinar") | 0 | Sim |
| `employment_type` | Tipo de jornada | 34 | Sim |
| `date_posted` | Data de publicação | 34 | Não |
| `description` | Texto completo do anúncio, de 301 a 4.401 caracteres | 0 | Sim |

## Como o banco entra na chamada

O arquivo `2_prompt/modelo_mensagem_usuario.txt` é o molde da mensagem enviada ao modelo. Cada `{nome}` do molde é o nome de uma coluna desta tabela. Para montar a mensagem de um anúncio, troca-se cada `{nome}` pelo valor da coluna naquela linha. **Se o valor estiver vazio, a linha inteira do molde é retirada.**

## Como a saída se liga ao banco

A planilha de saída (`4_saida/`) tem uma linha por anúncio, com o mesmo `vacancy_id`. Os campos do JSON viram colunas com o mesmo nome; as listas (`skills`, `temas`) viram texto com os itens separados por ponto e vírgula e espaço (`"; "`).
