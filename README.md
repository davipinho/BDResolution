# BDResolution

Este script em Python foi desenvolvido para alterar automaticamente a resolução e a taxa de atualização do sistema quando o jogo BloodStrike for iniciado. Quando o aplicativo for fechado, o script reverterá as configurações para os valores anteriores.

## Funcionalidades

- **Monitoramento de Aplicativo**: Monitora o jogo `BloodStrike.exe` localizado em `C:\Program Files (x86)\bloodstrike\BloodStrike.exe`.
- **Alteração de Resolução e Taxa de Atualização**: Modifica a resolução e a taxa de atualização do monitor quando o aplicativo é iniciado.
- **Retorno à Configuração Padrão**: Restaura a resolução padrão do monitor quando o aplicativo é fechado.
- **Interface Gráfica**: Interface de usuário com campos de entrada para configurar a resolução e a taxa de atualização, um terminal embutido e um botão para executar as ações.
- **Salvamento de Configurações**: As configurações de resolução e taxa de atualização são salvas em um arquivo XML, permitindo que sejam carregadas na próxima execução.
- **Troca de Caminho do Aplicativo**: Possibilidade de alterar o caminho do aplicativo monitorado, mantendo as configurações anteriores.
- **Parada Automática do Monitoramento**: Opção de parar automaticamente o monitoramento quando o aplicativo é fechado.

## Requisitos

- Python 3.x
- Bibliotecas Python: `tkinter`, `subprocess`, `xml.etree.ElementTree`, `psutil`, `time`

## Observações

- O `BloodStrike.exe` tem que estar instalado no `C:\Program Files (x86)`

