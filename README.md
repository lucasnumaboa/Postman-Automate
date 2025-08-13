# Postman Automatizado

Aplicativo para envio automatizado de requisições HTTP para APIs, com suporte a monitoramento de diretórios, processamento em lote e execução automática.

## Funcionalidades

- Monitoramento de múltiplos diretórios
- Processamento em lote de arquivos
- Execução automática com intervalo configurável
- Sistema de fila para controle de requisições simultâneas
- Log detalhado de tempos de execução e transferência
- Interface gráfica com suporte a minimização para a bandeja do sistema

## Sistema de Fila

O sistema de fila permite controlar o número máximo de requisições simultâneas que serão enviadas para a API. Isso é especialmente útil para evitar sobrecarga no servidor e garantir que todas as requisições sejam processadas corretamente.

### Como funciona

1. O número máximo de requisições simultâneas é configurado no arquivo `config.json` através do parâmetro `fila`
2. Quando o processamento em lote está ativado, o sistema envia até o número máximo de requisições configurado simultaneamente
3. À medida que as requisições são concluídas, novas requisições são iniciadas, mantendo sempre o número máximo de requisições ativas
4. Se uma requisição falhar, o sistema tentará novamente até o número máximo de tentativas configurado

### Benefícios

- Evita sobrecarga no servidor de destino
- Melhora a taxa de sucesso das requisições
- Permite processamento eficiente de grandes volumes de arquivos
- Fornece controle granular sobre o uso de recursos

## Log de Tempos

O sistema registra diversos tempos relacionados ao processamento das requisições, permitindo análise detalhada do desempenho e identificação de possíveis gargalos.

### Tempos Registrados

#### Tempo de Conexão
Tempo necessário para estabelecer a conexão com o servidor. É registrado como "Tempo de conexão: X ms" e indica quanto tempo levou para estabelecer a conexão TCP com o servidor de destino.

#### Tempo até o Primeiro Byte (TTFB)
Tempo entre o envio da requisição e o recebimento do primeiro byte da resposta. É registrado como "Tempo até o primeiro byte (TTFB): X ms" e indica a latência do servidor para processar a requisição e começar a enviar a resposta.

#### Taxa de Transferência
Velocidade com que os dados foram transferidos, calculada em MB/s. É registrada como "Arquivo processado - Taxa de transferência: X MB/s (Tamanho: Y MB)" e indica a eficiência da transferência de dados entre o cliente e o servidor.

#### Tempo Total de Execução
Tempo total desde o início até o fim da requisição. É registrado como "Tempo de execução: X s" e indica o tempo total que a requisição levou para ser processada, incluindo conexão, envio, processamento no servidor e recebimento da resposta.

### Interpretação dos Logs

- **Tempo de conexão alto**: Pode indicar problemas de rede ou sobrecarga no servidor
- **TTFB alto**: Pode indicar lentidão no processamento da requisição pelo servidor
- **Taxa de transferência baixa**: Pode indicar problemas de largura de banda ou limitações na rede
- **Tempo total de execução alto**: Pode ser resultado de qualquer um dos problemas acima ou de processamento complexo no servidor

## Configuração

As configurações do aplicativo são armazenadas nos arquivos:

- `config.json`: Configurações gerais como URL, credenciais e timeout
- `caminhos.json`: Configurações dos diretórios monitorados

## Execução

Para iniciar o aplicativo, execute o arquivo `Postman_Automatizado.exe` ou use o script `iniciar_postman.bat`.
