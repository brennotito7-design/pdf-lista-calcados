# Serviço de geração de PDF — Lista de Fornecedores

## O que é isso?
Uma API simples que recebe os dados do comprador (nome, CPF, e-mail)
e devolve o PDF personalizado com marca d'água. Integra com Make + Kirvano.

---

## Deploy no Railway (10 minutos)

### 1. Crie sua conta
Acesse railway.app e crie conta gratuita com GitHub.

### 2. Suba o projeto
- Clique em "New Project" → "Deploy from GitHub repo"
- Faça upload desta pasta como repositório (ou use GitHub Desktop)
- O Railway detecta automaticamente que é Python e instala as dependências

### 3. Pegue a URL do serviço
Após o deploy, o Railway gera uma URL pública tipo:
  https://pdf-service-production.up.railway.app

Guarde essa URL — você vai usar no Make.

---

## Como testar a API

Abra o terminal e rode:

  curl -X POST https://SUA-URL.railway.app/gerar-pdf \
    -H "Content-Type: application/json" \
    -d '{"nome":"João Silva","cpf":"123.456.789-00","email":"joao@email.com"}'

Você vai receber um JSON com o PDF em base64.

---

## Configuração no Make (passo a passo)

### Módulo 1 — Webhook (gatilho)
- Tipo: Webhooks → Custom webhook
- Copie a URL gerada e cole na Kirvano (Configurações → Integrações → Webhooks)
- Evento: Venda aprovada

### Módulo 2 — Gerar PDF
- Tipo: HTTP → Make a request
- URL: https://SUA-URL.railway.app/gerar-pdf
- Método: POST
- Body type: Raw
- Content type: application/json
- Body:
  {
    "nome": "{{1.customer.name}}",
    "cpf": "{{1.customer.document}}",
    "email": "{{1.customer.email}}"
  }

### Módulo 3 — Enviar e-mail
- Tipo: Gmail → Send an email
- To: {{1.customer.email}}
- Subject: Sua Lista de Fornecedores de Calçados está aqui!
- Body: Olá {{1.customer.name}}, seu acesso está no anexo abaixo.
- Attachment filename: Lista_Fornecedores.pdf
- Attachment data: {{2.pdf_base64}} (marcar como base64)

### Módulo 4 — Registrar na planilha (opcional)
- Tipo: Google Sheets → Add a row
- Colunas: Data, Nome, E-mail, CPF, Valor da venda

---

## Campos do webhook da Kirvano

Quando uma venda é aprovada, a Kirvano envia:
  customer.name    → nome completo do comprador
  customer.email   → e-mail do comprador
  customer.document → CPF ou CNPJ
  order.amount     → valor da venda
  order.id         → ID único do pedido

---

## Adicionando todos os seus fornecedores

Edite o arquivo app.py e substitua a lista FORNECEDORES
pelos seus dados reais. Cada item segue o formato:

  {"nome": "Nome do Contato", "whatsapp": "(XX) XXXXX-XXXX",
   "tipo": "Fabricante", "marca": "Nike"}

Após editar, faça redeploy no Railway (automático via GitHub).
