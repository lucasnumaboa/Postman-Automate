# Instruções de Uso - Postman Automatizado

## Configuração Inicial

1. Instale as dependências necessárias:
   ```
   pip install -r requirements.txt
   ```

2. Execute o aplicativo:
   ```
   python postman_automatizado.py
   ```

## Configurando o Aplicativo

### Aba de Configurações

1. Preencha a URL base do serviço que receberá as requisições
2. Configure as credenciais de autenticação (se necessário):
   - Username e Password para autenticação básica
   - Token para autenticação via Bearer token
   - Client ID e Client Secret para OAuth
3. Defina o timeout das requisições em segundos
4. Se necessário, configure a fila de processamento (será adicionada à URL base)
5. Clique em "Salvar Configurações"

### Aba de Cadastro de Caminhos

1. Selecione o diretório de entrada (onde os arquivos JSON serão colocados)
2. Selecione o diretório de saída (onde os arquivos processados serão movidos)
3. Configure o tempo de execução (em segundos) para verificação automática
4. Configure as flags:
   - **Ativar Gatilho**: Se marcado, o processamento só iniciará quando um arquivo `gatilho_ini.json` for detectado
   - **Requisições em Lote**: Se marcado, as requisições serão enviadas simultaneamente de acordo com o valor da "Fila de processamento"
   - **Execução Automática**: Se marcado, o sistema verificará a pasta de entrada a cada X segundos (definido no campo "Tempo de execução")
5. Clique em "Salvar Caminhos"

## Utilizando o Aplicativo

### Modo de Monitoramento Automático com Gatilho

1. Configure os caminhos de entrada e saída
2. Marque a opção "Ativar Gatilho"
3. Clique em "Iniciar Monitoramento"
4. Coloque os arquivos no diretório de entrada:
   - `gatilho_ini.json` (para iniciar o processamento)
   - Arquivos JSON a serem processados
   - `gatilho_fim.json` (será enviado ao final)

### Modo de Execução Automática Periódica

1. Configure os caminhos de entrada e saída
2. Defina o tempo de execução em segundos (intervalo entre verificações)
3. Marque a opção "Execução Automática"
4. Clique em "Iniciar Monitoramento"
5. O sistema verificará a pasta de entrada no intervalo definido e processará automaticamente os arquivos encontrados

### Modo de Processamento em Lote

1. Configure os caminhos de entrada e saída
2. Defina um valor numérico no campo "Fila de processamento" (na aba Configurações)
3. Marque a opção "Requisições em Lote"
4. Ao processar, o sistema enviará múltiplas requisições simultaneamente de acordo com o valor definido

### Modo de Execução Manual

1. Configure os caminhos de entrada e saída
2. Coloque os arquivos JSON a serem processados no diretório de entrada
3. Clique em "Executar Agora"

Observação: Todos os arquivos processados, incluindo os arquivos de gatilho (`gatilho_ini.json` e `gatilho_fim.json`), serão movidos para a pasta de saída com um timestamp no nome após o processamento.

## Estrutura dos Arquivos JSON

### Arquivos de Gatilho

Exemplos de arquivos de gatilho estão disponíveis na pasta `exemplos`:

- `gatilho_ini.json`: Enviado no início do processamento
- `gatilho_fim.json`: Enviado ao final do processamento

### Arquivos de Requisição

Qualquer arquivo JSON válido pode ser usado como corpo da requisição. Um exemplo está disponível em `exemplos/exemplo_requisicao.json`.

## Monitorando o Processamento

A aba de Logs exibe informações detalhadas sobre o processamento:

- Status de cada requisição enviada
- Erros que possam ocorrer
- Confirmação de arquivos processados

## Dicas e Solução de Problemas

### Configuração
- Certifique-se de que os diretórios de entrada e saída existam antes de iniciar o monitoramento
- Verifique se a URL base está correta e acessível
- Se estiver usando autenticação, confirme se as credenciais estão corretas

### Processamento em Lote
- Para o processamento em lote funcionar corretamente, o valor da "Fila de processamento" deve ser um número inteiro
- Quanto maior o número de requisições simultâneas, maior será o consumo de recursos do sistema
- Recomenda-se ajustar o valor de acordo com a capacidade do seu sistema e da API de destino

### Execução Automática
- O tempo de execução define o intervalo em segundos entre as verificações da pasta de entrada
- Valores muito baixos podem sobrecarregar o sistema e a API de destino
- Valores recomendados: entre 30 e 300 segundos (0,5 a 5 minutos)

### Geral
- Os arquivos são processados em ordem alfabética pelo nome
- Após o processamento, os arquivos são movidos para o diretório de saída com um timestamp no nome
- Se ocorrerem erros nas requisições, verifique os logs para mais detalhes
- Para interromper o monitoramento, clique em "Parar Monitoramento"