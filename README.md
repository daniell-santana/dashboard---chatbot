Dicas de melhorias:
- Transforme o arquivo .csv em .parquet
- Particione os arquivos "faq_", com as seguintes ressalvas:
    - Se o FAQ for particionado de forma inadequada (por exemplo, com base em critérios que não refletem
      a semelhança semântica entre as perguntas), perguntas semelhantes podem acabar em partes diferentes.
    - Isso pode fazer com que o sistema não encontre a pergunta mais similar no FAQ, resultando em respostas incorretas.
- Hospedar o projeto em um imagem no Docker (caso queira usar diretamente a imagem desenvolvida, acesse: docker pull daniellsantanaa/dashboard-chatbot

  ![Uploading workprocess-chatbot.png…]()

