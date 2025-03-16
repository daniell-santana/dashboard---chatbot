⚠️Dicas de melhorias⚠️:
- 🔃Transforme o arquivo .csv em .parquet
- 🔪Particione os arquivos "faq_", com as seguintes ressalvas:
    - Se o FAQ for particionado de forma inadequada (por exemplo, com base em critérios que não refletem
      a semelhança semântica entre as perguntas), perguntas semelhantes podem acabar em partes diferentes.
    - Isso pode fazer com que o sistema não encontre a pergunta mais similar no FAQ, resultando em respostas incorretas.
- 🏠Hospedar o projeto em um imagem no Docker (caso queira usar diretamente a imagem desenvolvida, acesse: docker pull daniellsantanaa/dashboard-chatbot
- ⏳Tornar a resposta do chatbot mais rápida (abaixo de 30 segundos)

#=========== 🤖Fluxo Operacional do Chatbot ===================#
1. Entrada do Usuário
Componente: Interface do Chatbot (Streamlit).

Descrição: O usuário digita uma pergunta no campo de entrada do chatbot.

Fluxo:
- O texto da pergunta é enviado para o backend do chatbot.
#=================================================

2. Processamento da Pergunta
Componente: Backend do Chatbot (Python + Streamlit).

Descrição: A pergunta do usuário é processada para determinar a melhor resposta.

Fluxo:
- A pergunta é convertida em um embedding usando um modelo da OpenAI (text-embedding-3-small).
- O embedding é normalizado para garantir consistência na busca de similaridade.
#=================================================

3. Busca no FAQ (Resposta Baseada em Dados)
Componente: FAQ Particionado + FAISS.

Descrição: O chatbot tenta encontrar uma resposta no FAQ usando similaridade de embeddings.

Fluxo:
- O embedding da pergunta é comparado com os embeddings das perguntas do FAQ usando o índice FAISS.
- Se a distância entre os embeddings for menor que um limiar pré-definido (ex: 0.3), a resposta correspondente é retornada.
- Caso contrário, o chatbot prossegue para gerar uma resposta híbrida.
#=================================================

4. Resposta Híbrida (FAQ + GPT-3.5)
Componente: OpenAI GPT-3.5

Descrição: Se a pergunta não for encontrada no FAQ, o chatbot usa o GPT-3.5 para gerar uma resposta criativa.

Fluxo:
- O chatbot envia a pergunta do usuário para o GPT-3.5, junto com um contexto personalizado (ex: "Você é um assistente educacional...").
- O GPT-3.5 gera uma resposta, que é então limitada a um número máximo de palavras e retornada ao usuário.
#=================================================

5. Resposta Final
Componente: Interface do Chatbot (Streamlit).

Descrição: A resposta (seja do FAQ ou do GPT-3.5) é exibida para o usuário.

Fluxo:
- A resposta é formatada e exibida na interface do chatbot.
- A conversa é armazenada no histórico (chat_history) para referência futura.
#=================================================

6. Infraestrutura (Docker + Google Cloud Run)
Componente: Docker + Google Cloud Run.

Descrição: O chatbot é empacotado em um contêiner Docker e implantado no Google Cloud Run para escalabilidade e disponibilidade.

Fluxo:
- O código do chatbot é empacotado em uma imagem Docker.
- A imagem é enviada para o Google Container Registry.
- O Google Cloud Run implanta a imagem e gerencia a execução do chatbot em um ambiente escalável.




