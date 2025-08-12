# Arquitetura do Backend - Sistema de Toldos

## Visão Geral
O backend será desenvolvido em Flask com SQLite para prototipagem (facilmente migrável para PostgreSQL em produção). O sistema incluirá autenticação robusta, APIs RESTful, visualização 3D, dashboard administrativo e geração de PDFs protegidos.

## Estrutura do Projeto

```
toldos_backend/
├── src/
│   ├── models/          # Modelos de dados
│   │   ├── user.py      # Usuários e autenticação
│   │   ├── client.py    # Clientes
│   │   ├── seller.py    # Vendedores
│   │   ├── quote.py     # Orçamentos
│   │   └── product.py   # Produtos/Toldos
│   ├── routes/          # Rotas da API
│   │   ├── auth.py      # Autenticação
│   │   ├── client.py    # Gestão de clientes
│   │   ├── seller.py    # Gestão de vendedores
│   │   ├── quote.py     # Gestão de orçamentos
│   │   ├── dashboard.py # Dashboard e relatórios
│   │   └── pdf.py       # Geração de PDFs
│   ├── services/        # Lógica de negócio
│   │   ├── auth_service.py
│   │   ├── email_service.py
│   │   ├── pdf_service.py
│   │   └── visualization_service.py
│   ├── utils/           # Utilitários
│   │   ├── decorators.py
│   │   └── validators.py
│   ├── static/          # Frontend integrado
│   └── main.py          # Ponto de entrada
└── requirements.txt
```

## Modelos de Dados

### User (Usuário)
- id (Primary Key)
- email (Unique)
- password_hash
- name
- role (admin, seller, client)
- is_verified (Boolean)
- verification_token
- created_at
- updated_at

### Client (Cliente)
- id (Primary Key)
- user_id (Foreign Key)
- company_name
- phone
- address
- city
- state
- zip_code
- created_at
- updated_at

### Seller (Vendedor)
- id (Primary Key)
- user_id (Foreign Key)
- commission_rate
- territory
- created_at
- updated_at

### Quote (Orçamento)
- id (Primary Key)
- client_id (Foreign Key)
- seller_id (Foreign Key)
- product_type
- dimensions (JSON)
- materials (JSON)
- total_price
- status (pending, approved, rejected)
- pdf_password
- created_at
- updated_at

### Product (Produto)
- id (Primary Key)
- name
- category
- base_price
- materials (JSON)
- dimensions_config (JSON)
- created_at
- updated_at

## APIs Principais

### Autenticação
- POST /api/auth/register - Registro de usuário
- POST /api/auth/login - Login
- POST /api/auth/logout - Logout
- POST /api/auth/verify-email - Verificação de email
- POST /api/auth/forgot-password - Recuperação de senha
- GET /api/auth/profile - Perfil do usuário

### Clientes
- GET /api/clients - Listar clientes
- POST /api/clients - Criar cliente
- GET /api/clients/{id} - Obter cliente
- PUT /api/clients/{id} - Atualizar cliente
- DELETE /api/clients/{id} - Deletar cliente

### Vendedores
- GET /api/sellers - Listar vendedores
- POST /api/sellers - Criar vendedor
- GET /api/sellers/{id} - Obter vendedor
- PUT /api/sellers/{id} - Atualizar vendedor
- DELETE /api/sellers/{id} - Deletar vendedor

### Orçamentos
- GET /api/quotes - Listar orçamentos
- POST /api/quotes - Criar orçamento
- GET /api/quotes/{id} - Obter orçamento
- PUT /api/quotes/{id} - Atualizar orçamento
- DELETE /api/quotes/{id} - Deletar orçamento
- POST /api/quotes/{id}/calculate - Calcular preço
- GET /api/quotes/{id}/3d-data - Dados para visualização 3D

### Dashboard
- GET /api/dashboard/stats - Estatísticas gerais
- GET /api/dashboard/reports - Relatórios
- GET /api/dashboard/charts - Dados para gráficos

### PDF
- GET /api/pdf/quote/{id} - Gerar PDF do orçamento
- POST /api/pdf/unlock - Desbloquear PDF com senha

## Funcionalidades Especiais

### Visualização 3D
- Integração com Three.js no frontend
- Backend fornece dados de geometria e materiais
- Cálculo de cotas e medidas em tempo real

### Sistema de Autenticação
- JWT tokens para sessões
- Verificação de email obrigatória
- Sistema de roles (admin, seller, client)
- Recuperação de senha por email

### Dashboard Administrativo
- Estatísticas em tempo real
- Relatórios de vendas por vendedor
- Análise de orçamentos por cliente
- Gráficos interativos

### Geração de PDF
- PDFs protegidos por senha única
- Layout profissional com logo e dados da empresa
- Visualização 3D integrada no PDF
- Assinatura digital opcional

## Tecnologias Utilizadas

### Backend
- Flask (Framework web)
- SQLAlchemy (ORM)
- Flask-JWT-Extended (Autenticação)
- Flask-Mail (Envio de emails)
- ReportLab (Geração de PDFs)
- PyPDF2 (Proteção de PDFs)
- Flask-CORS (CORS)

### Banco de Dados
- SQLite (Desenvolvimento)
- PostgreSQL (Produção - opcional)

### Segurança
- Bcrypt (Hash de senhas)
- JWT (Tokens de autenticação)
- CORS configurado
- Validação de entrada
- Rate limiting

## Próximos Passos
1. Implementar modelos de dados
2. Configurar autenticação e autorização
3. Desenvolver APIs CRUD
4. Integrar visualização 3D
5. Criar dashboard e relatórios
6. Implementar geração de PDFs
7. Testes e integração

