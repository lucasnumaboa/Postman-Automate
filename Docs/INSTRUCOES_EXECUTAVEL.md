# Instruções para Criar o Executável do Postman Automatizado

Este documento contém instruções sobre como criar um arquivo executável (.exe) do aplicativo Postman Automatizado.

## Requisitos

- Python 3.6 ou superior instalado
- Conexão com a internet (para baixar dependências)

## Como Criar o Executável

1. Abra a pasta do projeto Postman Automatizado
2. Execute o arquivo `criar_executavel.bat` com um duplo clique
3. Aguarde o processo ser concluído (pode demorar alguns minutos)
4. O executável será criado na pasta `dist` dentro do diretório do projeto

## O que o Script Faz

O script `criar_executavel.bat` realiza as seguintes operações:

1. Verifica se o Python está instalado no sistema
2. Instala todas as dependências necessárias listadas no arquivo `requirements.txt`
3. Cria um executável usando o PyInstaller
4. Copia os arquivos de configuração necessários para a pasta do executável
5. Cria a estrutura de pastas necessária para o funcionamento do aplicativo

## Estrutura de Arquivos Gerada

Após a execução do script, a seguinte estrutura será criada na pasta `dist`:

```
dist/
├── Postman_Automatizado.exe
├── config.json
├── caminhos.json
├── icon.png
├── arquivos/
│   ├── input/
│   └── output/
└── log/
```

## Executando o Aplicativo

Para executar o aplicativo, basta dar um duplo clique no arquivo `Postman_Automatizado.exe` dentro da pasta `dist`.

## Solução de Problemas

Se ocorrer algum erro durante a criação do executável:

1. Verifique se o Python está instalado corretamente
2. Certifique-se de que tem permissões de administrador no sistema
3. Verifique sua conexão com a internet
4. Tente executar o script novamente

Se o problema persistir, entre em contato com o suporte técnico.