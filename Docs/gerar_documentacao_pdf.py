import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from PIL import Image as PILImage

# Configurações do documento
PDF_FILE = "Documentacao_Postman_Automatizado.pdf"
TITULO = "Documentação - Postman Automatizado"
SUBTITULO = "Guia Completo de Uso e Configuração"
AUTOR = "Equipe de Desenvolvimento"
VERSAO = "1.0"

# Função para verificar se o arquivo existe
def verificar_arquivo(caminho):
    return os.path.exists(caminho)

# Função para ler conteúdo de arquivo
def ler_arquivo(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except Exception as e:
        print(f"Erro ao ler arquivo {caminho}: {e}")
        return ""

# Função principal para gerar o PDF
def gerar_pdf():
    # Verificar se a biblioteca ReportLab está instalada
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        print("A biblioteca ReportLab não está instalada. Instalando...")
        os.system("pip install reportlab")
        print("ReportLab instalada com sucesso!")
        from reportlab.pdfgen import canvas
    
    # Criar o documento PDF
    doc = SimpleDocTemplate(
        PDF_FILE,
        pagesize=A4,
        title=TITULO,
        author=AUTOR
    )
    
    # Estilos de texto
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Titulo',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='Subtitulo',
        parent=styles['Heading2'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Secao',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Subsecao',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='TextoNormal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='Lista',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=5
    ))
    
    # Elementos do documento
    elementos = []
    
    # Adicionar logo/ícone se existir
    if verificar_arquivo("icon.png"):
        try:
            img = PILImage.open("icon.png")
            width, height = img.size
            aspect = height / float(width)
            img_width = 2 * inch
            img_height = img_width * aspect
            elementos.append(Image("icon.png", width=img_width, height=img_height))
            elementos.append(Spacer(1, 0.5 * inch))
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
    
    # Título e subtítulo
    elementos.append(Paragraph(TITULO, styles["Titulo"]))
    elementos.append(Paragraph(SUBTITULO, styles["Subtitulo"]))
    elementos.append(Paragraph(f"Versão {VERSAO}", styles["Subtitulo"]))
    elementos.append(Spacer(1, 1 * inch))
    
    # Índice (será preenchido automaticamente)
    elementos.append(Paragraph("Índice", styles["Secao"]))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 1. Objetivo do Programa
    elementos.append(PageBreak())
    elementos.append(Paragraph("1. Objetivo do Programa", styles["Secao"]))
    elementos.append(Paragraph(
        "O Postman Automatizado é uma aplicação desktop desenvolvida em Python que automatiza o envio de requisições HTTP para APIs. "
        "O programa monitora diretórios específicos, processa arquivos JSON e os envia como requisições POST para um endpoint configurado, "
        "facilitando a integração entre sistemas através de uma interface gráfica moderna e intuitiva.",
        styles["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 2. Bibliotecas Utilizadas
    elementos.append(Paragraph("2. Bibliotecas Utilizadas", styles["Secao"]))
    
    # Tabela de bibliotecas
    dados_bibliotecas = [
        ["Biblioteca", "Função"],
        ["ttkbootstrap", "Framework para criação de interfaces gráficas modernas com tema escuro"],
        ["requests", "Biblioteca para envio de requisições HTTP"],
        ["watchdog", "Monitoramento de diretórios e detecção de eventos de criação de arquivos"],
        ["pystray", "Criação de ícones na bandeja do sistema (system tray)"],
        ["pillow", "Manipulação de imagens para o ícone da aplicação"],
        ["pyinstaller", "Criação de executáveis standalone"],
        ["pywin32", "Integração com o sistema Windows para verificação de instâncias múltiplas"]
    ]
    
    tabela = Table(dados_bibliotecas, colWidths=[2.5*cm, 12*cm])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elementos.append(tabela)
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 3. Consumo de Recursos
    elementos.append(Paragraph("3. Consumo de Recursos", styles["Secao"]))
    elementos.append(Paragraph(
        "O consumo de recursos do Postman Automatizado varia de acordo com a configuração utilizada:",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("• <b>Processamento em Lote:</b> Quanto maior o número de requisições simultâneas (definido na \"Fila de processamento\"), maior será o consumo de memória e CPU", styles["Lista"]))
    elementos.append(Paragraph("• <b>Execução Automática:</b> Intervalos muito curtos de verificação podem aumentar o consumo de CPU", styles["Lista"]))
    elementos.append(Paragraph("• <b>Monitoramento Contínuo:</b> Mantém um processo ativo em segundo plano, com consumo mínimo de recursos quando ocioso", styles["Lista"]))
    elementos.append(Paragraph("• <b>Requisitos Mínimos:</b> Python 3.6+, 100MB de RAM livre, conexão com internet para envio das requisições", styles["Lista"]))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 4. Aba de Configurações
    elementos.append(PageBreak())
    elementos.append(Paragraph("4. Aba de Configurações", styles["Secao"]))
    elementos.append(Paragraph("4.1. Campos de Configuração", styles["Subsecao"]))
    elementos.append(Paragraph("• <b>URL Base:</b> Endereço principal da API que receberá as requisições POST", styles["Lista"]))
    elementos.append(Paragraph("• <b>Autenticação:</b>", styles["Lista"]))
    elementos.append(Paragraph("  - <b>Username/Password:</b> Credenciais para autenticação básica HTTP", styles["Lista"]))
    elementos.append(Paragraph("  - <b>Token/Access Token:</b> Token para autenticação via Bearer token", styles["Lista"]))
    elementos.append(Paragraph("  - <b>Client ID/Secret:</b> Credenciais para autenticação OAuth", styles["Lista"]))
    elementos.append(Paragraph("• <b>Timeout:</b> Tempo máximo (em segundos) que o sistema aguardará por uma resposta da API antes de considerar a requisição como falha. Valores recomendados entre 30 e 300 segundos, dependendo da complexidade da API.", styles["Lista"]))
    elementos.append(Paragraph("• <b>Fila de processamento:</b> Número que define:", styles["Lista"]))
    elementos.append(Paragraph("  1. Quantas requisições serão enviadas simultaneamente quando o modo \"Requisições em Lote\" estiver ativado", styles["Lista"]))
    elementos.append(Paragraph("  2. Complemento que será adicionado à URL base (ex: se URL base é \"https://api.exemplo.com/\" e fila é \"10\", a URL final será \"https://api.exemplo.com/10\")", styles["Lista"]))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 5. Aba de Cadastro de Caminhos
    elementos.append(Paragraph("5. Aba de Cadastro de Caminhos", styles["Secao"]))
    elementos.append(Paragraph("5.1. Como Cadastrar Caminhos", styles["Subsecao"]))
    elementos.append(Paragraph("1. Defina um nome para identificar o caminho", styles["Lista"]))
    elementos.append(Paragraph("2. Selecione o diretório de entrada onde os arquivos JSON serão colocados", styles["Lista"]))
    elementos.append(Paragraph("3. Selecione o diretório de saída onde os arquivos processados serão movidos", styles["Lista"]))
    elementos.append(Paragraph("4. Configure o tempo de execução (em segundos) para verificação automática", styles["Lista"]))
    elementos.append(Paragraph("5. Configure as flags conforme necessário", styles["Lista"]))
    elementos.append(Paragraph("6. Clique em \"Salvar Caminhos\"", styles["Lista"]))
    elementos.append(Spacer(1, 0.3 * inch))
    
    elementos.append(Paragraph("5.2. Funcionalidade da Flag Gatilho", styles["Subsecao"]))
    elementos.append(Paragraph(
        "Quando ativada, o processamento só iniciará quando um arquivo específico chamado <b>gatilho_ini.json</b> for detectado no diretório de entrada. "
        "Este arquivo funciona como um \"sinal verde\" para iniciar o processamento dos demais arquivos.",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("• <b>gatilho_ini.json:</b> Enviado no início do processamento. Após ser processado, o sistema processa todos os outros arquivos JSON no diretório.", styles["Lista"]))
    elementos.append(Paragraph("• <b>gatilho_fim.json:</b> Enviado ao final do processamento, após todos os outros arquivos terem sido processados. Serve como confirmação de que o lote foi completamente processado.", styles["Lista"]))
    elementos.append(Paragraph(
        "Esta funcionalidade é útil para garantir que todos os arquivos necessários já estejam no diretório antes de iniciar o processamento, evitando processamento parcial de lotes.",
        styles["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.3 * inch))
    
    elementos.append(Paragraph("5.3. Requisições em Lote", styles["Subsecao"]))
    elementos.append(Paragraph(
        "Quando ativada, esta opção permite o envio simultâneo de múltiplas requisições, aumentando significativamente a velocidade de processamento. "
        "O número de requisições simultâneas é determinado pelo valor configurado no campo \"Fila de processamento\" na aba Configurações.",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("Considerações importantes:", styles["TextoNormal"]))
    elementos.append(Paragraph("• Maior paralelismo = maior velocidade, mas também maior consumo de recursos", styles["Lista"]))
    elementos.append(Paragraph("• Recomenda-se ajustar o valor de acordo com a capacidade do seu sistema e da API de destino", styles["Lista"]))
    elementos.append(Paragraph("• Valores muito altos podem sobrecarregar a API ou causar erros de timeout", styles["Lista"]))
    elementos.append(Spacer(1, 0.3 * inch))
    
    elementos.append(Paragraph("5.4. Execução Automática", styles["Subsecao"]))
    elementos.append(Paragraph(
        "Quando ativada, o sistema verificará periodicamente o diretório de entrada em busca de novos arquivos para processar. "
        "O intervalo entre verificações é definido pelo campo \"Tempo de execução\" em segundos.",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("Recomendações:", styles["TextoNormal"]))
    elementos.append(Paragraph("• Valores muito baixos podem sobrecarregar o sistema e a API", styles["Lista"]))
    elementos.append(Paragraph("• Valores recomendados: entre 30 e 300 segundos (0,5 a 5 minutos)", styles["Lista"]))
    elementos.append(Paragraph("• Para processamento em tempo real, considere usar valores menores com a flag de gatilho ativada", styles["Lista"]))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 6. Aba de Logs
    elementos.append(PageBreak())
    elementos.append(Paragraph("6. Aba de Logs", styles["Secao"]))
    elementos.append(Paragraph(
        "A aba de Logs exibe informações detalhadas sobre o processamento, incluindo:",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("• Início e fim do monitoramento", styles["Lista"]))
    elementos.append(Paragraph("• Detalhes de cada requisição enviada (URL, tempo de resposta, status)", styles["Lista"]))
    elementos.append(Paragraph("• Erros que possam ocorrer durante o processamento", styles["Lista"]))
    elementos.append(Paragraph("• Confirmação de arquivos processados e movidos", styles["Lista"]))
    elementos.append(Paragraph("• Tempo de execução de cada requisição", styles["Lista"]))
    elementos.append(Paragraph(
        "Os logs são salvos diariamente em arquivos na pasta \"log\" com o formato \"log_DDMMYY.txt\" para referência futura e diagnóstico de problemas.",
        styles["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 7. Criação de Executável
    elementos.append(Paragraph("7. Criação de Executável", styles["Secao"]))
    elementos.append(Paragraph(
        "O aplicativo pode ser distribuído como um arquivo executável (.exe) para Windows, facilitando a instalação e uso sem necessidade de configurar o ambiente Python. Para criar o executável:",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("1. Execute o arquivo <b>criar_executavel.bat</b> com um duplo clique", styles["Lista"]))
    elementos.append(Paragraph("2. Aguarde o processo ser concluído (pode demorar alguns minutos)", styles["Lista"]))
    elementos.append(Paragraph("3. O executável será criado na pasta <b>dist</b> dentro do diretório do projeto", styles["Lista"]))
    elementos.append(Paragraph(
        "O executável gerado inclui todas as dependências necessárias e pode ser distribuído para outros computadores Windows sem necessidade de instalação adicional.",
        styles["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 8. Exemplos de Uso
    elementos.append(Paragraph("8. Exemplos de Uso", styles["Secao"]))
    elementos.append(Paragraph(
        "Na pasta <b>exemplos</b> estão disponíveis modelos de arquivos que podem ser utilizados como referência:",
        styles["TextoNormal"]
    ))
    elementos.append(Paragraph("• <b>exemplo_requisicao.json:</b> Exemplo de corpo de requisição", styles["Lista"]))
    elementos.append(Paragraph("• <b>gatilho_ini.json:</b> Modelo de arquivo para iniciar o processamento", styles["Lista"]))
    elementos.append(Paragraph("• <b>gatilho_fim.json:</b> Modelo de arquivo para finalizar o processamento", styles["Lista"]))
    elementos.append(Spacer(1, 0.5 * inch))
    
    # 9. Dicas e Solução de Problemas
    elementos.append(Paragraph("9. Dicas e Solução de Problemas", styles["Secao"]))
    elementos.append(Paragraph("• Certifique-se de que os diretórios de entrada e saída existam antes de iniciar o monitoramento", styles["Lista"]))
    elementos.append(Paragraph("• Os arquivos são processados em ordem alfabética pelo nome", styles["Lista"]))
    elementos.append(Paragraph("• Após o processamento, os arquivos são movidos para o diretório de saída com um timestamp no nome", styles["Lista"]))
    elementos.append(Paragraph("• Se ocorrerem erros nas requisições, verifique os logs para mais detalhes", styles["Lista"]))
    elementos.append(Paragraph("• A aplicação pode ser minimizada para a bandeja do sistema (system tray) para continuar o monitoramento em segundo plano", styles["Lista"]))
    
    # Construir o documento
    doc.build(elementos)
    print(f"Documentação PDF gerada com sucesso: {PDF_FILE}")
    return True

# Executar a função principal
if __name__ == "__main__":
    gerar_pdf()