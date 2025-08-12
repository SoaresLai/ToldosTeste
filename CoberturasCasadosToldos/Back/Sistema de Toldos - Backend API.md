# Sistema de Toldos - Backend API

Um sistema completo para gestão de orçamentos, clientes e vendedores de produtos de cobertura, com visualização 3D e dashboard administrativo.

## 🚀 Funcionalidades

### ✅ Implementadas

- **Sistema de Autenticação Completo**
  - Registro de usuários com verificação de email
  - Login com JWT tokens
  - Recuperação de senha
  - Diferentes níveis de acesso (Admin, Vendedor, Cliente)

- **Gestão de Usuários**
  - CRUD completo para clientes e vendedores
  - Perfis personalizados por tipo de usuário
  - Sistema de permissões baseado em roles

- **Gestão de Orçamentos**
  - Criação e edição de orçamentos
  - Cálculo automático de preços
  - Diferentes status (pendente, aprovado, rejeitado)
  - Associação com clientes e vendedores

- **Visualização 3D**
  - Geração de dados para renderização 3D
  - Configuração de materiais e cores
  - Cálculo de dimensões e cotas
  - Suporte a diferentes tipos de produtos

- **Dashboard Administrativo**
  - Estatísticas de vendas e performance
  - Gráficos de receita e produtos
  - Relatórios de vendedores e clientes
  - Análise financeira detalhada

- **Geração de PDFs**
  - PDFs profissionais de orçamentos
  - Proteção por senha única
  - Relatórios em PDF
  - Layout responsivo e personalizado

### 🎯 Recursos Adicionais

- **Modal de Perfil de Usuário**
  - Visualização e edição de dados pessoais
  - Histórico de atividades
  - Configurações de conta

- **Sistema de Login Seguro**
  - Validação de email obrigatória
  - Senhas criptografadas
  - Tokens JWT com expiração

- **Dashboard com Visualizações**
  - Métricas em tempo real
  - Gráficos interativos
  - Filtros por período
  - Exportação de dados

- **Proteção de PDFs**
  - Senhas únicas por orçamento
  - Regeneração de senhas
  - Validação de acesso

## 🏗️ Arquitetura

### Tecnologias Utilizadas

- **Backend:** Flask (Python 3.11)
- **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Autenticação:** JWT (Flask-JWT-Extended)
- **PDFs:** ReportLab + PyPDF2
- **Email:** Flask-Mail
- **Validação:** Email-validator
- **CORS:** Flask-CORS

### Estrutura do Projeto

```
toldos_backend/
├── src/
│   ├── main.py                 # Aplicação principal
│   ├── models/                 # Modelos de dados
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── seller.py
│   │   ├── quote.py
│   │   └── product.py
│   ├── routes/                 # Rotas da API
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── seller.py
│   │   ├── quote.py
│   │   ├── visualization.py
│   │   ├── dashboard.py
│   │   └── pdf.py
│   ├── services/               # Serviços de negócio
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   ├── pdf_service.py
│   │   └── visualization_service.py
│   └── utils/                  # Utilitários
│       ├── decorators.py
│       └── validators.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- pip
- Git

### Instalação

1. **Clone o repositório:**
```bash
git clone <url_do_repositorio>
cd toldos_backend
```

2. **Crie e ative o ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Inicialize o banco de dados:**
```bash
python -c "from src.main import app; app.app_context().push(); from src.models.user import db; db.create_all()"
```

6. **Execute a aplicação:**
```bash
python src/main.py
```

A API estará disponível em `http://localhost:5000`

### Configuração de Email

Para funcionalidade completa de email, configure no arquivo `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
MAIL_DEFAULT_SENDER=noreply@toldos.com
```

## 📚 Documentação da API

A documentação completa da API está disponível em `documentacao_api.md`, incluindo:

- Todos os endpoints disponíveis
- Parâmetros e respostas
- Exemplos de uso
- Códigos de erro
- Guias de integração

### Endpoints Principais

- **Autenticação:** `/api/auth/*`
- **Clientes:** `/api/clients/*`
- **Vendedores:** `/api/sellers/*`
- **Orçamentos:** `/api/quotes/*`
- **Visualização 3D:** `/api/visualization/*`
- **Dashboard:** `/api/dashboard/*`
- **PDFs:** `/api/pdf/*`

## 🧪 Testes

### Testes Básicos Realizados

- ✅ Registro e login de usuários
- ✅ Verificação de email
- ✅ Criação de orçamentos
- ✅ Cálculo de preços
- ✅ Geração de dados 3D
- ✅ Estatísticas do dashboard
- ✅ Geração de PDFs

### Executar Testes

```bash
# Teste de endpoints básicos
python -c "
from src.main import app
with app.test_client() as client:
    # Teste de materiais
    response = client.get('/api/visualization/materials')
    print('Materials:', response.status_code)
    
    # Teste de produtos
    response = client.get('/api/visualization/products')
    print('Products:', response.status_code)
"
```

## 🔧 Integração com Frontend

### Configuração CORS

A API está configurada para aceitar requisições de qualquer origem durante o desenvolvimento. Para produção, configure origens específicas no arquivo `.env`:

```env
CORS_ORIGINS=http://localhost:3000,https://seudominio.com
```

### Exemplo de Integração

```javascript
// Configuração base
const API_BASE = 'http://localhost:5000/api';

// Função para fazer requisições autenticadas
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Erro na requisição');
  }
  
  return response.json();
}

// Exemplo de uso
const materials = await apiRequest('/visualization/materials');
const quotes = await apiRequest('/quotes?page=1&per_page=10');
```

## 🚀 Deploy

### Desenvolvimento

```bash
python src/main.py
```

### Produção com Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:app"]
```

## 📊 Funcionalidades do Dashboard

### Para Administradores

- **Visão Geral:**
  - Total de clientes, vendedores e orçamentos
  - Receita total e taxa de conversão
  - Ticket médio

- **Gráficos:**
  - Receita ao longo do tempo
  - Produtos mais vendidos
  - Performance por vendedor

- **Relatórios:**
  - Relatório de vendedores com comissões
  - Relatório de clientes e gastos
  - Análise financeira detalhada

### Para Vendedores

- **Estatísticas Pessoais:**
  - Orçamentos criados e aprovados
  - Vendas e comissões ganhas
  - Taxa de conversão pessoal

- **Clientes:**
  - Lista de clientes atendidos
  - Histórico de orçamentos

## 🎨 Visualização 3D

### Tipos de Produtos Suportados

- **Toldo Fixo:** Estrutura fixa com suportes laterais
- **Toldo Retrátil:** Mecanismo de abertura/fechamento
- **Cobertura de Policarbonato:** Painéis transparentes
- **Pergolado:** Estrutura decorativa com vigas
- **Tenda:** Estrutura temporária

### Materiais Disponíveis

- **Estrutura:** Alumínio, Aço, Madeira
- **Cobertura:** Lona Comum, Lona Premium, Policarbonato, Vidro
- **Cores:** 7 opções padrão
- **Acessórios:** LED, Sensores, Controle Remoto

### Dados Gerados

- Geometria 3D (vértices, faces, normais)
- Propriedades de materiais (cor, rugosidade, metalicidade)
- Dimensões e cotas
- Estimativa de preço

## 📄 Sistema de PDFs

### Características

- **Layout Profissional:** Cabeçalho, rodapé e formatação consistente
- **Proteção por Senha:** Cada PDF possui senha única
- **Informações Completas:** Dados do cliente, especificações, preços
- **Condições Comerciais:** Prazo, pagamento, garantia

### Tipos de PDF

- **Orçamentos:** PDF detalhado com proteção por senha
- **Relatórios:** PDFs de vendedores, clientes e financeiro
- **Preview:** Visualização sem proteção para usuários autenticados

## 🔐 Segurança

### Autenticação

- **JWT Tokens:** Access token (1h) + Refresh token (30 dias)
- **Verificação de Email:** Obrigatória para ativação
- **Senhas Seguras:** Validação de complexidade

### Autorização

- **Roles:** Admin, Seller, Client com permissões específicas
- **Proteção de Recursos:** Cada endpoint verifica permissões
- **Isolamento de Dados:** Usuários só acessam próprios dados

### Proteção de Dados

- **Senhas Criptografadas:** Hash bcrypt
- **PDFs Protegidos:** Senhas únicas por documento
- **CORS Configurável:** Controle de origens permitidas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:

- **Documentação:** `documentacao_api.md`
- **Issues:** Use o sistema de issues do GitHub
- **Email:** contato@toldos.com

---

**Desenvolvido por Manus AI**  
**Versão:** 1.0  
**Data:** 12 de agosto de 2025

