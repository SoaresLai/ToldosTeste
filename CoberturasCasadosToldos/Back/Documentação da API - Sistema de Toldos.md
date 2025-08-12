# Documentação da API - Sistema de Toldos

**Versão:** 1.0  
**Data:** 12 de agosto de 2025  
**Autor:** Manus AI  

## Sumário Executivo

Esta documentação apresenta a API completa do Sistema de Toldos, uma solução backend robusta desenvolvida em Flask para gerenciamento de orçamentos, clientes, vendedores e visualização 3D de produtos de cobertura. O sistema oferece funcionalidades avançadas incluindo autenticação JWT, dashboard administrativo, geração de PDFs protegidos por senha e APIs para visualização tridimensional de produtos.

A API foi projetada seguindo os princípios RESTful e implementa medidas de segurança modernas, incluindo autenticação baseada em tokens, verificação de email, sistema de roles e proteção CORS. O sistema suporta diferentes tipos de usuários (administradores, vendedores e clientes) com permissões específicas para cada funcionalidade.

## Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação e Autorização](#autenticação-e-autorização)
3. [Endpoints de Usuários](#endpoints-de-usuários)
4. [Gestão de Clientes](#gestão-de-clientes)
5. [Gestão de Vendedores](#gestão-de-vendedores)
6. [Gestão de Orçamentos](#gestão-de-orçamentos)
7. [Visualização 3D](#visualização-3d)
8. [Dashboard e Relatórios](#dashboard-e-relatórios)
9. [Geração de PDFs](#geração-de-pdfs)
10. [Códigos de Erro](#códigos-de-erro)
11. [Exemplos de Uso](#exemplos-de-uso)
12. [Configuração e Deploy](#configuração-e-deploy)

## Visão Geral

### Arquitetura da API

O Sistema de Toldos utiliza uma arquitetura modular baseada em Flask, com separação clara entre modelos de dados, serviços de negócio e rotas da API. A estrutura do projeto segue as melhores práticas de desenvolvimento Python, com organização em blueprints para facilitar a manutenção e escalabilidade.

### URL Base

```
http://localhost:5000/api
```

Para produção, substitua `localhost:5000` pelo domínio e porta apropriados.

### Formato de Resposta

Todas as respostas da API seguem o formato JSON padrão. Respostas de sucesso incluem os dados solicitados, enquanto respostas de erro incluem uma mensagem descritiva do problema.

**Exemplo de Resposta de Sucesso:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Exemplo"
  }
}
```

**Exemplo de Resposta de Erro:**
```json
{
  "error": "Mensagem descritiva do erro"
}
```

### Códigos de Status HTTP

A API utiliza os códigos de status HTTP padrão:

- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `400 Bad Request` - Dados inválidos na requisição
- `401 Unauthorized` - Autenticação necessária ou inválida
- `403 Forbidden` - Acesso negado (permissões insuficientes)
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro interno do servidor

### Headers Obrigatórios

Para endpoints que requerem autenticação:
```
Authorization: Bearer <token_jwt>
Content-Type: application/json
```



## Autenticação e Autorização

### Sistema de Autenticação

O sistema utiliza JSON Web Tokens (JWT) para autenticação, proporcionando uma solução stateless e segura. Cada usuário deve se registrar, verificar seu email e fazer login para obter um token de acesso válido.

### Fluxo de Autenticação

1. **Registro:** O usuário se registra fornecendo email, senha e informações básicas
2. **Verificação de Email:** Um token de verificação é enviado por email
3. **Ativação:** O usuário clica no link de verificação para ativar a conta
4. **Login:** Com a conta ativada, o usuário pode fazer login e receber tokens JWT
5. **Acesso:** Os tokens são utilizados para acessar endpoints protegidos

### Tipos de Usuário

O sistema suporta três tipos de usuário com diferentes níveis de acesso:

- **Admin:** Acesso completo a todas as funcionalidades
- **Seller (Vendedor):** Pode gerenciar seus próprios orçamentos e clientes
- **Client (Cliente):** Pode visualizar apenas seus próprios orçamentos

### Endpoints de Autenticação

#### POST /api/auth/register

Registra um novo usuário no sistema.

**Parâmetros:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "MinhaSenh@123",
  "name": "Nome do Usuário",
  "role": "client" // opcional: "admin", "seller", "client" (padrão: "client")
}
```

**Validações:**
- Email deve ter formato válido
- Senha deve ter pelo menos 8 caracteres, incluindo maiúscula, minúscula, número e caractere especial
- Nome é obrigatório
- Role deve ser um dos valores válidos

**Resposta de Sucesso (201):**
```json
{
  "message": "Usuário registrado com sucesso. Verifique seu email.",
  "user": {
    "id": 1,
    "email": "usuario@exemplo.com",
    "name": "Nome do Usuário",
    "role": "client",
    "is_verified": false,
    "created_at": "2025-08-12T01:00:00.000000"
  }
}
```

#### POST /api/auth/login

Autentica um usuário e retorna tokens de acesso.

**Parâmetros:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "MinhaSenh@123"
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Login realizado com sucesso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "usuario@exemplo.com",
    "name": "Nome do Usuário",
    "role": "client",
    "is_verified": true
  }
}
```

#### GET /api/auth/verify-email/{token}

Verifica o email do usuário através do token enviado por email.

**Parâmetros:**
- `token` (URL): Token de verificação recebido por email

**Resposta de Sucesso (200):**
Retorna uma página HTML confirmando a verificação do email.

#### POST /api/auth/forgot-password

Inicia o processo de recuperação de senha.

**Parâmetros:**
```json
{
  "email": "usuario@exemplo.com"
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Se o email existir, você receberá instruções de recuperação"
}
```

#### POST /api/auth/reset-password

Redefine a senha do usuário usando o token de recuperação.

**Parâmetros:**
```json
{
  "token": "token_de_recuperacao",
  "password": "NovaSenha@123"
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Senha redefinida com sucesso"
}
```

#### GET /api/auth/profile

Obtém o perfil do usuário autenticado.

**Headers Obrigatórios:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "email": "usuario@exemplo.com",
  "name": "Nome do Usuário",
  "role": "client",
  "is_verified": true,
  "created_at": "2025-08-12T01:00:00.000000",
  "client_data": {
    // dados específicos do cliente se role = "client"
  }
}
```

### Segurança

#### Validação de Senhas

As senhas devem atender aos seguintes critérios:
- Mínimo de 8 caracteres
- Pelo menos uma letra maiúscula
- Pelo menos uma letra minúscula
- Pelo menos um número
- Pelo menos um caractere especial (!@#$%^&*(),.?\":{}|<>)

#### Tokens JWT

- **Access Token:** Válido por 1 hora, usado para autenticação em endpoints protegidos
- **Refresh Token:** Válido por 30 dias, usado para renovar access tokens
- Tokens são assinados com chave secreta configurável via variável de ambiente

#### Proteção CORS

A API está configurada para aceitar requisições de qualquer origem durante o desenvolvimento. Em produção, deve-se configurar origens específicas para maior segurança.


## Gestão de Clientes

### Visão Geral

O módulo de gestão de clientes permite o cadastro, consulta, atualização e remoção de clientes no sistema. Cada cliente está associado a um usuário do sistema e pode ter informações adicionais como empresa, telefone e endereço.

### Permissões

- **Admin:** Acesso completo a todos os clientes
- **Seller:** Pode visualizar todos os clientes (para criação de orçamentos)
- **Client:** Pode visualizar e atualizar apenas seus próprios dados

### Endpoints de Clientes

#### GET /api/clients

Lista todos os clientes do sistema com paginação e busca.

**Permissões:** Admin, Seller

**Parâmetros de Query:**
- `page` (opcional): Número da página (padrão: 1)
- `per_page` (opcional): Itens por página (padrão: 10)
- `search` (opcional): Termo de busca (nome, email ou empresa)

**Exemplo de Requisição:**
```
GET /api/clients?page=1&per_page=5&search=empresa
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "clients": [
    {
      "id": 1,
      "user_id": 2,
      "company_name": "Empresa Exemplo Ltda",
      "phone": "11999999999",
      "address": "Rua Exemplo, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234567",
      "created_at": "2025-08-12T01:00:00.000000",
      "updated_at": "2025-08-12T01:00:00.000000",
      "user": {
        "id": 2,
        "email": "cliente@exemplo.com",
        "name": "Cliente Exemplo",
        "role": "client",
        "is_verified": true
      }
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 5
}
```

#### GET /api/clients/{id}

Obtém informações detalhadas de um cliente específico.

**Permissões:** Admin, Seller, Client (apenas próprios dados)

**Parâmetros:**
- `id` (URL): ID do cliente

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "user_id": 2,
  "company_name": "Empresa Exemplo Ltda",
  "phone": "11999999999",
  "address": "Rua Exemplo, 123",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01234567",
  "created_at": "2025-08-12T01:00:00.000000",
  "updated_at": "2025-08-12T01:00:00.000000",
  "user": {
    "id": 2,
    "email": "cliente@exemplo.com",
    "name": "Cliente Exemplo",
    "role": "client",
    "is_verified": true
  }
}
```

#### POST /api/clients

Cria um novo cliente no sistema.

**Permissões:** Admin

**Parâmetros:**
```json
{
  "email": "novocliente@exemplo.com",
  "password": "SenhaSegura@123",
  "name": "Novo Cliente",
  "company_name": "Nova Empresa Ltda", // opcional
  "phone": "11888888888", // opcional
  "address": "Nova Rua, 456", // opcional
  "city": "Rio de Janeiro", // opcional
  "state": "RJ", // opcional
  "zip_code": "20000000" // opcional
}
```

**Validações:**
- Email deve ser único e ter formato válido
- Senha deve atender aos critérios de segurança
- Telefone deve ter formato brasileiro (10 ou 11 dígitos)
- CEP deve ter 8 dígitos

**Resposta de Sucesso (201):**
```json
{
  "message": "Cliente criado com sucesso",
  "client": {
    "id": 2,
    "user_id": 3,
    "company_name": "Nova Empresa Ltda",
    "phone": "11888888888",
    "address": "Nova Rua, 456",
    "city": "Rio de Janeiro",
    "state": "RJ",
    "zip_code": "20000000",
    "user": {
      "id": 3,
      "email": "novocliente@exemplo.com",
      "name": "Novo Cliente",
      "role": "client",
      "is_verified": true
    }
  }
}
```

#### PUT /api/clients/{id}

Atualiza informações de um cliente existente.

**Permissões:** Admin, Client (apenas próprios dados)

**Parâmetros:**
- `id` (URL): ID do cliente

**Corpo da Requisição:**
```json
{
  "name": "Nome Atualizado", // opcional
  "company_name": "Empresa Atualizada", // opcional
  "phone": "11777777777", // opcional
  "address": "Endereço Atualizado", // opcional
  "city": "Cidade Atualizada", // opcional
  "state": "Estado Atualizado", // opcional
  "zip_code": "12345678" // opcional
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Cliente atualizado com sucesso",
  "client": {
    // dados atualizados do cliente
  }
}
```

#### DELETE /api/clients/{id}

Remove um cliente do sistema.

**Permissões:** Admin

**Parâmetros:**
- `id` (URL): ID do cliente

**Restrições:**
- Não é possível deletar clientes que possuem orçamentos associados

**Resposta de Sucesso (200):**
```json
{
  "message": "Cliente deletado com sucesso"
}
```

#### GET /api/clients/profile

Obtém o perfil do cliente autenticado.

**Permissões:** Client

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "user_id": 2,
  "company_name": "Minha Empresa",
  "phone": "11999999999",
  "address": "Meu Endereço",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01234567",
  "user": {
    "id": 2,
    "email": "meu@email.com",
    "name": "Meu Nome",
    "role": "client"
  }
}
```

#### PUT /api/clients/profile

Atualiza o perfil do cliente autenticado.

**Permissões:** Client

**Parâmetros:**
```json
{
  "name": "Nome Atualizado",
  "company_name": "Empresa Atualizada",
  "phone": "11888888888",
  "address": "Novo Endereço",
  "city": "Nova Cidade",
  "state": "Novo Estado",
  "zip_code": "87654321"
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Perfil atualizado com sucesso",
  "client": {
    // dados atualizados do perfil
  }
}
```

### Validações Específicas

#### Telefone

O sistema valida telefones brasileiros com os seguintes critérios:
- 10 ou 11 dígitos (incluindo DDD)
- DDD válido (11-99)
- Formato aceito: apenas números ou com formatação (11) 99999-9999

#### CEP

Validação de CEP brasileiro:
- Exatamente 8 dígitos
- Aceita formato com ou sem hífen (12345-678 ou 12345678)

### Casos de Uso Comuns

#### Busca de Clientes

Para buscar clientes por nome, email ou empresa:
```
GET /api/clients?search=joão&page=1&per_page=10
```

#### Listagem Paginada

Para obter uma lista paginada de clientes:
```
GET /api/clients?page=2&per_page=20
```

#### Atualização de Perfil

Clientes podem atualizar seus próprios dados através do endpoint de perfil:
```
PUT /api/clients/profile
```


## Gestão de Vendedores

### Visão Geral

O módulo de gestão de vendedores permite o cadastro e gerenciamento de vendedores no sistema. Cada vendedor possui uma taxa de comissão configurável e pode ser associado a um território específico. Vendedores têm acesso aos seus próprios orçamentos e estatísticas de performance.

### Permissões

- **Admin:** Acesso completo a todos os vendedores e suas configurações
- **Seller:** Pode visualizar e atualizar apenas seus próprios dados (exceto taxa de comissão)

### Endpoints de Vendedores

#### GET /api/sellers

Lista todos os vendedores do sistema.

**Permissões:** Admin

**Parâmetros de Query:**
- `page` (opcional): Número da página (padrão: 1)
- `per_page` (opcional): Itens por página (padrão: 10)
- `search` (opcional): Termo de busca (nome, email ou território)

**Resposta de Sucesso (200):**
```json
{
  "sellers": [
    {
      "id": 1,
      "user_id": 3,
      "commission_rate": 0.05,
      "territory": "São Paulo - Zona Sul",
      "created_at": "2025-08-12T01:00:00.000000",
      "updated_at": "2025-08-12T01:00:00.000000",
      "user": {
        "id": 3,
        "email": "vendedor@exemplo.com",
        "name": "Vendedor Exemplo",
        "role": "seller",
        "is_verified": true
      }
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 10
}
```

#### GET /api/sellers/{id}

Obtém informações detalhadas de um vendedor específico.

**Permissões:** Admin, Seller (apenas próprios dados)

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "user_id": 3,
  "commission_rate": 0.05,
  "territory": "São Paulo - Zona Sul",
  "created_at": "2025-08-12T01:00:00.000000",
  "updated_at": "2025-08-12T01:00:00.000000",
  "user": {
    "id": 3,
    "email": "vendedor@exemplo.com",
    "name": "Vendedor Exemplo",
    "role": "seller",
    "is_verified": true
  }
}
```

#### POST /api/sellers

Cria um novo vendedor no sistema.

**Permissões:** Admin

**Parâmetros:**
```json
{
  "email": "novovendedor@exemplo.com",
  "password": "SenhaSegura@123",
  "name": "Novo Vendedor",
  "commission_rate": 0.07, // opcional, padrão: 0.05 (5%)
  "territory": "Rio de Janeiro - Zona Norte" // opcional
}
```

**Validações:**
- Email deve ser único e ter formato válido
- Senha deve atender aos critérios de segurança
- Taxa de comissão deve estar entre 0 e 1 (0% a 100%)

**Resposta de Sucesso (201):**
```json
{
  "message": "Vendedor criado com sucesso",
  "seller": {
    "id": 2,
    "user_id": 4,
    "commission_rate": 0.07,
    "territory": "Rio de Janeiro - Zona Norte",
    "user": {
      "id": 4,
      "email": "novovendedor@exemplo.com",
      "name": "Novo Vendedor",
      "role": "seller",
      "is_verified": true
    }
  }
}
```

#### PUT /api/sellers/{id}

Atualiza informações de um vendedor existente.

**Permissões:** Admin, Seller (apenas próprios dados, exceto commission_rate)

**Parâmetros:**
```json
{
  "name": "Nome Atualizado", // opcional
  "territory": "Território Atualizado", // opcional
  "commission_rate": 0.08 // opcional, apenas Admin pode alterar
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Vendedor atualizado com sucesso",
  "seller": {
    // dados atualizados do vendedor
  }
}
```

#### DELETE /api/sellers/{id}

Remove um vendedor do sistema.

**Permissões:** Admin

**Restrições:**
- Não é possível deletar vendedores que possuem orçamentos associados

**Resposta de Sucesso (200):**
```json
{
  "message": "Vendedor deletado com sucesso"
}
```

#### GET /api/sellers/profile

Obtém o perfil do vendedor autenticado.

**Permissões:** Seller

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "user_id": 3,
  "commission_rate": 0.05,
  "territory": "São Paulo - Zona Sul",
  "user": {
    "id": 3,
    "email": "vendedor@exemplo.com",
    "name": "Vendedor Exemplo",
    "role": "seller"
  }
}
```

#### PUT /api/sellers/profile

Atualiza o perfil do vendedor autenticado.

**Permissões:** Seller

**Parâmetros:**
```json
{
  "name": "Nome Atualizado",
  "territory": "Território Atualizado"
}
```

**Nota:** Vendedores não podem alterar sua própria taxa de comissão.

#### GET /api/sellers/{id}/stats

Obtém estatísticas de performance de um vendedor.

**Permissões:** Admin, Seller (apenas próprias estatísticas)

**Resposta de Sucesso (200):**
```json
{
  "total_quotes": 25,
  "approved_quotes": 18,
  "pending_quotes": 5,
  "rejected_quotes": 2,
  "total_sales_value": 45000.00,
  "commission_earned": 2250.00,
  "conversion_rate": 72.0
}
```

### Métricas e KPIs

#### Taxa de Conversão

Calculada como: (Orçamentos Aprovados / Total de Orçamentos) × 100

#### Comissão Ganha

Calculada como: Valor Total de Vendas × Taxa de Comissão

#### Estatísticas Disponíveis

- **Total de Orçamentos:** Número total de orçamentos criados pelo vendedor
- **Orçamentos Aprovados:** Número de orçamentos com status "approved"
- **Orçamentos Pendentes:** Número de orçamentos com status "pending"
- **Orçamentos Rejeitados:** Número de orçamentos com status "rejected"
- **Valor Total de Vendas:** Soma dos valores dos orçamentos aprovados
- **Comissão Ganha:** Valor total de comissões baseado nas vendas
- **Taxa de Conversão:** Percentual de orçamentos aprovados

### Configuração de Territórios

Os territórios são campos de texto livre que permitem organizar vendedores por:
- Regiões geográficas (ex: "São Paulo - Zona Sul")
- Estados (ex: "Rio de Janeiro")
- Cidades específicas (ex: "Campinas")
- Tipos de cliente (ex: "Empresarial", "Residencial")

### Gestão de Comissões

#### Configuração de Taxa

- Taxa padrão: 5% (0.05)
- Faixa permitida: 0% a 100% (0.0 a 1.0)
- Apenas administradores podem alterar taxas de comissão
- Alterações afetam apenas vendas futuras

#### Cálculo de Comissão

A comissão é calculada automaticamente baseada em:
- Valor total do orçamento aprovado
- Taxa de comissão do vendedor no momento da aprovação
- Apenas orçamentos com status "approved" geram comissão

### Casos de Uso Comuns

#### Criação de Vendedor com Território

```json
POST /api/sellers
{
  "email": "vendedor.sp@empresa.com",
  "password": "Senha123!",
  "name": "João Silva",
  "commission_rate": 0.06,
  "territory": "São Paulo - Grande ABC"
}
```

#### Consulta de Performance

```
GET /api/sellers/1/stats
```

#### Atualização de Território

```json
PUT /api/sellers/profile
{
  "territory": "São Paulo - Zona Oeste"
}
```


## Gestão de Orçamentos

### Visão Geral

O módulo de gestão de orçamentos é o núcleo do sistema, permitindo a criação, acompanhamento e aprovação de orçamentos para produtos de cobertura. Cada orçamento inclui especificações técnicas, dimensões, materiais, preços e está associado a um cliente e vendedor.

### Ciclo de Vida do Orçamento

1. **Criação:** Vendedor ou admin cria orçamento para um cliente
2. **Cálculo:** Sistema calcula preço baseado em dimensões e materiais
3. **Apresentação:** Cliente recebe orçamento com visualização 3D
4. **Aprovação/Rejeição:** Cliente decide sobre o orçamento
5. **Finalização:** Orçamento aprovado gera comissão para vendedor

### Status de Orçamento

- **pending:** Aguardando decisão do cliente (padrão)
- **approved:** Aprovado pelo cliente
- **rejected:** Rejeitado pelo cliente
- **completed:** Serviço executado e finalizado

### Endpoints de Orçamentos

#### GET /api/quotes

Lista orçamentos baseado no perfil do usuário.

**Permissões:** Admin (todos), Seller (próprios), Client (próprios)

**Parâmetros de Query:**
- `page` (opcional): Número da página (padrão: 1)
- `per_page` (opcional): Itens por página (padrão: 10)
- `status` (opcional): Filtrar por status

**Resposta de Sucesso (200):**
```json
{
  "quotes": [
    {
      "id": 1,
      "client_id": 1,
      "seller_id": 1,
      "product_type": "toldo_retratil",
      "dimensions": {
        "width": 4.0,
        "length": 3.0,
        "height": 2.5,
        "angle": 15
      },
      "materials": {
        "estrutura": "aluminio",
        "cobertura": "lona_premium",
        "cor_estrutura": "branco",
        "cor_cobertura": "azul",
        "motorizado": true,
        "sensor_vento": true
      },
      "total_price": 2850.00,
      "status": "pending",
      "notes": "Cliente solicitou instalação urgente",
      "created_at": "2025-08-12T01:00:00.000000",
      "updated_at": "2025-08-12T01:00:00.000000",
      "client": {
        "id": 1,
        "company_name": "Empresa Cliente",
        "user": {
          "name": "Cliente Exemplo",
          "email": "cliente@exemplo.com"
        }
      },
      "seller": {
        "id": 1,
        "user": {
          "name": "Vendedor Exemplo",
          "email": "vendedor@exemplo.com"
        }
      }
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 10
}
```

#### GET /api/quotes/{id}

Obtém detalhes de um orçamento específico.

**Permissões:** Admin, Seller (próprios), Client (próprios)

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "client_id": 1,
  "seller_id": 1,
  "product_type": "toldo_retratil",
  "dimensions": {
    "width": 4.0,
    "length": 3.0,
    "height": 2.5,
    "angle": 15
  },
  "materials": {
    "estrutura": "aluminio",
    "cobertura": "lona_premium",
    "cor_estrutura": "branco",
    "cor_cobertura": "azul",
    "motorizado": true,
    "sensor_vento": true
  },
  "total_price": 2850.00,
  "status": "pending",
  "notes": "Cliente solicitou instalação urgente",
  "created_at": "2025-08-12T01:00:00.000000",
  "updated_at": "2025-08-12T01:00:00.000000",
  "client": {
    // dados completos do cliente
  },
  "seller": {
    // dados completos do vendedor
  }
}
```

#### POST /api/quotes

Cria um novo orçamento.

**Permissões:** Admin, Seller

**Parâmetros:**
```json
{
  "client_id": 1,
  "seller_id": 1, // opcional para admin, obrigatório se admin criar
  "product_type": "toldo_retratil",
  "dimensions": {
    "width": 4.0,
    "length": 3.0,
    "height": 2.5, // opcional, padrão: 2.5
    "angle": 15 // opcional, padrão: 0
  },
  "materials": {
    "estrutura": "aluminio",
    "cobertura": "lona_premium",
    "cor_estrutura": "branco",
    "cor_cobertura": "azul",
    "motorizado": true,
    "sensor_vento": true,
    "led_lighting": false
  },
  "total_price": 2850.00, // opcional, será calculado automaticamente se não fornecido
  "notes": "Observações sobre o orçamento" // opcional
}
```

**Tipos de Produto Disponíveis:**
- `toldo_fixo`: Toldo fixo
- `toldo_retratil`: Toldo retrátil
- `cobertura_policarbonato`: Cobertura de policarbonato
- `pergolado`: Pergolado
- `tenda`: Tenda

**Validações:**
- Cliente deve existir
- Vendedor deve existir (se especificado)
- Dimensões devem ter width e length positivos
- Preço deve ser positivo

**Resposta de Sucesso (201):**
```json
{
  "message": "Orçamento criado com sucesso",
  "quote": {
    // dados completos do orçamento criado
  },
  "pdf_password": "AbC123Xy" // senha para acessar PDF
}
```

#### PUT /api/quotes/{id}

Atualiza um orçamento existente.

**Permissões:** Admin, Seller (próprios)

**Parâmetros:**
```json
{
  "product_type": "toldo_fixo", // opcional
  "dimensions": {
    "width": 5.0,
    "length": 4.0,
    "height": 3.0
  }, // opcional
  "materials": {
    "estrutura": "aco",
    "cobertura": "lona_comum"
  }, // opcional
  "total_price": 3200.00, // opcional
  "status": "approved", // opcional
  "notes": "Observações atualizadas" // opcional
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Orçamento atualizado com sucesso",
  "quote": {
    // dados atualizados do orçamento
  }
}
```

#### DELETE /api/quotes/{id}

Remove um orçamento do sistema.

**Permissões:** Admin

**Resposta de Sucesso (200):**
```json
{
  "message": "Orçamento deletado com sucesso"
}
```

#### POST /api/quotes/{id}/calculate

Recalcula o preço de um orçamento baseado em novas especificações.

**Permissões:** Admin, Seller

**Parâmetros:**
```json
{
  "dimensions": {
    "width": 4.5,
    "length": 3.5,
    "height": 2.8
  },
  "materials": {
    "estrutura": "aluminio",
    "cobertura": "lona_premium",
    "motorizado": true,
    "sensor_vento": true
  },
  "complexity_factor": 1.2 // opcional, fator de complexidade (padrão: 1.0)
}
```

**Resposta de Sucesso (200):**
```json
{
  "calculated_price": 3150.75,
  "area": 15.75,
  "base_price_per_m2": 180.00,
  "breakdown": {
    "base_cost": 2835.00,
    "material_cost": 250.00,
    "complexity_adjustment": 65.75
  }
}
```

#### GET /api/quotes/{id}/3d-data

Obtém dados para visualização 3D do orçamento.

**Permissões:** Admin, Seller (próprios), Client (próprios)

**Resposta de Sucesso (200):**
```json
{
  "geometry": {
    "width": 4.0,
    "length": 3.0,
    "height": 2.5,
    "type": "toldo_retratil"
  },
  "materials": {
    "estrutura": "aluminio",
    "cobertura": "lona_premium"
  },
  "colors": {
    "structure": "#C0C0C0",
    "cover": "#4169E1",
    "frame": "#808080"
  },
  "features": {
    "retractable": true,
    "motorized": true,
    "led_lighting": false,
    "wind_sensor": true
  },
  "measurements": {
    "area": 12.0,
    "perimeter": 14.0,
    "coverage_angle": 15
  }
}
```

### Cálculo de Preços

#### Preços Base por Tipo de Produto

| Tipo de Produto | Preço Base (R$/m²) |
|------------------|-------------------|
| Toldo Fixo | R$ 120,00 |
| Toldo Retrátil | R$ 180,00 |
| Cobertura Policarbonato | R$ 95,00 |
| Pergolado | R$ 200,00 |
| Tenda | R$ 85,00 |

#### Custos Adicionais de Materiais

| Material/Acessório | Custo Adicional |
|-------------------|-----------------|
| Estrutura de Aço | +R$ 25,00/m² |
| Estrutura de Madeira | -R$ 15,00/m² |
| Lona Premium | +R$ 20,00/m² |
| Policarbonato | +R$ 40,00/m² |
| Vidro | +R$ 80,00/m² |
| Iluminação LED | +R$ 150,00 |
| Sensor de Vento | +R$ 200,00 |
| Controle Remoto | +R$ 100,00 |
| Sensor de Chuva | +R$ 180,00 |

#### Fórmula de Cálculo

```
Preço Final = (Área × Preço Base) + Custos de Materiais + Custos de Acessórios
Área = Largura × Comprimento
```

### Proteção de PDF

Cada orçamento possui uma senha única para proteger o PDF gerado:
- Senha gerada automaticamente na criação
- 8 caracteres alfanuméricos
- Pode ser regenerada por admin ou vendedor responsável
- Necessária para abrir o PDF do orçamento

### Notificações

O sistema envia notificações por email quando:
- Novo orçamento é criado (para o cliente)
- Status do orçamento é alterado
- PDF é gerado

### Filtros e Buscas

#### Filtro por Status

```
GET /api/quotes?status=pending
GET /api/quotes?status=approved
```

#### Paginação

```
GET /api/quotes?page=2&per_page=20
```

#### Combinação de Filtros

```
GET /api/quotes?status=approved&page=1&per_page=10
```

### Casos de Uso Comuns

#### Criação de Orçamento Completo

```json
POST /api/quotes
{
  "client_id": 1,
  "product_type": "toldo_retratil",
  "dimensions": {
    "width": 4.0,
    "length": 3.0,
    "height": 2.5,
    "angle": 10
  },
  "materials": {
    "estrutura": "aluminio",
    "cobertura": "lona_premium",
    "cor_estrutura": "branco",
    "cor_cobertura": "azul",
    "motorizado": true,
    "sensor_vento": true,
    "led_lighting": true
  },
  "notes": "Cliente prefere instalação no período da manhã"
}
```

#### Aprovação de Orçamento

```json
PUT /api/quotes/1
{
  "status": "approved"
}
```

#### Recálculo de Preço

```json
POST /api/quotes/1/calculate
{
  "dimensions": {
    "width": 5.0,
    "length": 4.0
  },
  "materials": {
    "motorizado": false,
    "sensor_vento": false
  }
}
```


## Visualização 3D

### Visão Geral

O módulo de visualização 3D permite a geração de representações tridimensionais dos produtos de cobertura, fornecendo dados estruturados que podem ser utilizados por bibliotecas JavaScript como Three.js no frontend. O sistema calcula geometrias, aplica materiais e cores, e fornece informações de cotação em tempo real.

### Funcionalidades

- Geração de geometria 3D baseada em especificações
- Aplicação de materiais e texturas
- Cálculo de cotas e dimensões
- Visualização de diferentes tipos de produtos
- Configuração de cores e acabamentos
- Dados para renderização em tempo real

### Endpoints de Visualização

#### GET /api/visualization/materials

Lista todos os materiais disponíveis para visualização.

**Permissões:** Público (sem autenticação)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "materials": {
    "estrutura": [
      {
        "id": "aluminio",
        "name": "Alumínio",
        "color": "#C0C0C0",
        "price_factor": 1.0
      },
      {
        "id": "aco",
        "name": "Aço",
        "color": "#808080",
        "price_factor": 1.2
      },
      {
        "id": "madeira",
        "name": "Madeira",
        "color": "#8B4513",
        "price_factor": 0.8
      }
    ],
    "cobertura": [
      {
        "id": "lona_comum",
        "name": "Lona Comum",
        "color": "#FFFFFF",
        "price_factor": 1.0
      },
      {
        "id": "lona_premium",
        "name": "Lona Premium",
        "color": "#F0F0F0",
        "price_factor": 1.5
      },
      {
        "id": "policarbonato",
        "name": "Policarbonato",
        "color": "#E6F3FF",
        "price_factor": 2.0
      },
      {
        "id": "vidro",
        "name": "Vidro",
        "color": "#E0F6FF",
        "price_factor": 3.0
      }
    ],
    "cores": [
      {
        "id": "branco",
        "name": "Branco",
        "hex": "#FFFFFF"
      },
      {
        "id": "bege",
        "name": "Bege",
        "hex": "#F5F5DC"
      },
      {
        "id": "cinza",
        "name": "Cinza",
        "hex": "#808080"
      },
      {
        "id": "azul",
        "name": "Azul",
        "hex": "#4169E1"
      },
      {
        "id": "verde",
        "name": "Verde",
        "hex": "#228B22"
      },
      {
        "id": "vermelho",
        "name": "Vermelho",
        "hex": "#DC143C"
      },
      {
        "id": "preto",
        "name": "Preto",
        "hex": "#000000"
      }
    ],
    "acessorios": [
      {
        "id": "led_lighting",
        "name": "Iluminação LED",
        "price": 150.0
      },
      {
        "id": "wind_sensor",
        "name": "Sensor de Vento",
        "price": 200.0
      },
      {
        "id": "remote_control",
        "name": "Controle Remoto",
        "price": 100.0
      },
      {
        "id": "rain_sensor",
        "name": "Sensor de Chuva",
        "price": 180.0
      }
    ]
  }
}
```

#### GET /api/visualization/products

Lista tipos de produtos disponíveis para visualização.

**Permissões:** Público (sem autenticação)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "products": [
    {
      "id": "toldo_fixo",
      "name": "Toldo Fixo",
      "description": "Toldo com estrutura fixa, ideal para áreas que necessitam proteção permanente",
      "base_price": 120.0,
      "features": ["estrutura_fixa", "resistente_vento", "baixa_manutencao"]
    },
    {
      "id": "toldo_retratil",
      "name": "Toldo Retrátil",
      "description": "Toldo com mecanismo retrátil, permite controle da cobertura",
      "base_price": 180.0,
      "features": ["retratil", "motorizado_opcional", "controle_remoto"]
    },
    {
      "id": "cobertura_policarbonato",
      "name": "Cobertura de Policarbonato",
      "description": "Cobertura transparente que permite passagem de luz",
      "base_price": 95.0,
      "features": ["transparente", "resistente_uv", "duravel"]
    },
    {
      "id": "pergolado",
      "name": "Pergolado",
      "description": "Estrutura decorativa com cobertura parcial ou total",
      "base_price": 200.0,
      "features": ["decorativo", "ventilacao", "personalizavel"]
    },
    {
      "id": "tenda",
      "name": "Tenda",
      "description": "Estrutura temporária para eventos e proteção",
      "base_price": 85.0,
      "features": ["portatil", "montagem_rapida", "economico"]
    }
  ]
}
```

#### POST /api/visualization/generate

Gera dados de visualização 3D baseado nas especificações fornecidas.

**Permissões:** Requer autenticação

**Parâmetros:**
```json
{
  "product_type": "toldo_retratil",
  "dimensions": {
    "width": 4.0,
    "length": 3.0,
    "height": 2.5,
    "angle": 15
  },
  "materials": {
    "estrutura": "aluminio",
    "cobertura": "lona_premium",
    "cor_estrutura": "branco",
    "cor_cobertura": "azul"
  },
  "accessories": {
    "motorizado": true,
    "sensor_vento": true,
    "led_lighting": false,
    "controle_remoto": true
  }
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "visualization_data": {
    "geometry": {
      "type": "toldo_retratil",
      "vertices": [
        [0, 0, 0],
        [4.0, 0, 0],
        [4.0, 3.0, 0],
        [0, 3.0, 0],
        [0, 0, 2.5],
        [4.0, 0, 2.5],
        [4.0, 3.0, 2.5],
        [0, 3.0, 2.5]
      ],
      "faces": [
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
        [4, 5, 6, 7]
      ],
      "normals": [
        [0, -1, 0],
        [1, 0, 0],
        [0, 1, 0],
        [-1, 0, 0],
        [0, 0, 1]
      ]
    },
    "materials": {
      "structure": {
        "type": "metal",
        "color": "#FFFFFF",
        "roughness": 0.3,
        "metalness": 0.8
      },
      "cover": {
        "type": "fabric",
        "color": "#4169E1",
        "roughness": 0.8,
        "metalness": 0.0
      }
    },
    "dimensions": {
      "width": 4.0,
      "length": 3.0,
      "height": 2.5,
      "area": 12.0,
      "perimeter": 14.0,
      "angle": 15
    },
    "features": {
      "retractable": true,
      "motorized": true,
      "wind_sensor": true,
      "led_lighting": false,
      "remote_control": true
    },
    "price_estimate": {
      "base_cost": 2160.0,
      "material_cost": 240.0,
      "accessory_cost": 400.0,
      "total": 2800.0
    }
  }
}
```

#### POST /api/visualization/calculate-price

Calcula preço baseado em especificações sem gerar geometria completa.

**Permissões:** Público (sem autenticação)

**Parâmetros:**
```json
{
  "product_type": "toldo_fixo",
  "dimensions": {
    "width": 5.0,
    "length": 4.0
  },
  "materials": {
    "estrutura": "aco",
    "cobertura": "policarbonato"
  },
  "accessories": {
    "led_lighting": true,
    "sensor_vento": false
  }
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "price_breakdown": {
    "area": 20.0,
    "base_price_per_m2": 120.0,
    "base_cost": 2400.0,
    "material_adjustments": {
      "estrutura_aco": 500.0,
      "cobertura_policarbonato": 800.0
    },
    "accessory_costs": {
      "led_lighting": 150.0
    },
    "subtotal": 3850.0,
    "taxes": 385.0,
    "total": 4235.0
  },
  "estimated_delivery": "15-20 dias úteis"
}
```

### Tipos de Geometria

#### Toldo Fixo

Estrutura retangular fixa com suportes laterais:
- Vértices principais definem a área de cobertura
- Suportes verticais nas extremidades
- Inclinação configurável para escoamento

#### Toldo Retrátil

Estrutura com mecanismo de abertura/fechamento:
- Geometria variável baseada no estado (aberto/fechado)
- Trilhos laterais para movimento
- Componentes motorizados opcionais

#### Cobertura de Policarbonato

Estrutura com painéis transparentes:
- Perfis de alumínio para fixação
- Painéis modulares
- Sistema de vedação

#### Pergolado

Estrutura decorativa com vigas:
- Pilares de sustentação
- Vigas horizontais
- Cobertura parcial ou total opcional

#### Tenda

Estrutura temporária:
- Armação desmontável
- Lona tensionada
- Ancoragem no solo

### Sistema de Cotas

#### Cotas Automáticas

O sistema gera automaticamente cotas para:
- Largura total
- Comprimento total
- Altura de instalação
- Ângulo de inclinação
- Distâncias entre suportes

#### Formato de Cotas

```json
{
  "dimensions": [
    {
      "type": "width",
      "value": 4.0,
      "unit": "m",
      "position": [2.0, -0.5, 0],
      "direction": "horizontal"
    },
    {
      "type": "length",
      "value": 3.0,
      "unit": "m",
      "position": [-0.5, 1.5, 0],
      "direction": "vertical"
    },
    {
      "type": "height",
      "value": 2.5,
      "unit": "m",
      "position": [4.5, 0, 1.25],
      "direction": "vertical"
    }
  ]
}
```

### Configuração de Materiais

#### Propriedades Físicas

Cada material possui propriedades para renderização realista:
- **Cor:** Cor base em hexadecimal
- **Rugosidade:** Valor de 0.0 (liso) a 1.0 (rugoso)
- **Metalicidade:** Valor de 0.0 (não metálico) a 1.0 (metálico)
- **Transparência:** Para materiais como policarbonato e vidro

#### Texturas

O sistema suporta aplicação de texturas:
- Padrões de tecido para lonas
- Texturas metálicas para estruturas
- Efeitos de transparência para policarbonato

### Integração com Frontend

#### Three.js

Dados otimizados para uso com Three.js:
```javascript
// Exemplo de uso dos dados retornados
const geometry = new THREE.BufferGeometry();
geometry.setFromPoints(visualizationData.geometry.vertices);

const material = new THREE.MeshStandardMaterial({
  color: visualizationData.materials.cover.color,
  roughness: visualizationData.materials.cover.roughness,
  metalness: visualizationData.materials.cover.metalness
});

const mesh = new THREE.Mesh(geometry, material);
```

#### Babylon.js

Compatibilidade com Babylon.js através de conversão de dados:
```javascript
// Conversão para Babylon.js
const babylonMesh = BABYLON.MeshBuilder.CreateGround(
  "toldo",
  {
    width: visualizationData.dimensions.width,
    height: visualizationData.dimensions.length
  },
  scene
);
```

### Performance e Otimização

#### Cache de Geometrias

- Geometrias comuns são cacheadas em memória
- Redução de tempo de processamento para configurações similares
- Invalidação automática quando materiais mudam

#### Simplificação de Malhas

- Diferentes níveis de detalhe baseados no uso
- Geometrias simplificadas para preview
- Geometrias detalhadas para visualização final

### Casos de Uso Comuns

#### Configurador Interativo

```javascript
// Atualização em tempo real
function updateVisualization(config) {
  fetch('/api/visualization/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(config)
  })
  .then(response => response.json())
  .then(data => {
    updateThreeJSScene(data.visualization_data);
  });
}
```

#### Cálculo de Preço Dinâmico

```javascript
// Cálculo sem geometria completa
function calculatePrice(specs) {
  fetch('/api/visualization/calculate-price', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(specs)
  })
  .then(response => response.json())
  .then(data => {
    updatePriceDisplay(data.price_breakdown);
  });
}
```


## Dashboard e Relatórios

### Visão Geral

O módulo de dashboard e relatórios fornece uma visão abrangente das operações do sistema, incluindo estatísticas de vendas, performance de vendedores, análise de clientes e relatórios financeiros. Os dados são apresentados de forma estruturada para facilitar a criação de gráficos e visualizações no frontend.

### Permissões por Tipo de Usuário

- **Admin:** Acesso completo a todos os relatórios e estatísticas
- **Seller:** Acesso às próprias estatísticas e dados de clientes
- **Client:** Sem acesso ao dashboard (apenas visualização de próprios orçamentos)

### Endpoints de Dashboard

#### GET /api/dashboard/stats

Obtém estatísticas gerais do dashboard.

**Permissões:** Admin, Seller

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "stats": {
    "overview": {
      "total_clients": 45,
      "total_sellers": 8,
      "total_quotes": 127,
      "total_revenue": 285750.00,
      "conversion_rate": 68.5,
      "average_ticket": 3250.75
    },
    "monthly": {
      "quotes": 23,
      "revenue": 52400.00
    },
    "status_breakdown": {
      "pending": {
        "count": 15,
        "total_value": 42500.00
      },
      "approved": {
        "count": 87,
        "total_value": 285750.00
      },
      "rejected": {
        "count": 25,
        "total_value": 0.00
      }
    }
  }
}
```

#### GET /api/dashboard/charts/revenue

Obtém dados para gráfico de receita ao longo do tempo.

**Permissões:** Admin, Seller

**Parâmetros de Query:**
- `period` (opcional): "monthly", "weekly", "yearly" (padrão: "monthly")

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "chart_data": [
    {
      "period": "2025-01",
      "revenue": 45200.00,
      "count": 18
    },
    {
      "period": "2025-02",
      "revenue": 52400.00,
      "count": 23
    },
    {
      "period": "2025-03",
      "revenue": 38900.00,
      "count": 16
    },
    {
      "period": "2025-04",
      "revenue": 61300.00,
      "count": 27
    },
    {
      "period": "2025-05",
      "revenue": 48750.00,
      "count": 21
    },
    {
      "period": "2025-06",
      "revenue": 55200.00,
      "count": 24
    }
  ],
  "period": "monthly"
}
```

#### GET /api/dashboard/charts/products

Obtém dados para gráfico de produtos mais vendidos.

**Permissões:** Admin, Seller

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "chart_data": [
    {
      "product_type": "toldo_retratil",
      "quantity": 45,
      "revenue": 125400.00,
      "average_price": 2786.67
    },
    {
      "product_type": "toldo_fixo",
      "quantity": 32,
      "revenue": 78200.00,
      "average_price": 2443.75
    },
    {
      "product_type": "cobertura_policarbonato",
      "quantity": 28,
      "revenue": 52800.00,
      "average_price": 1885.71
    },
    {
      "product_type": "pergolado",
      "quantity": 15,
      "revenue": 42500.00,
      "average_price": 2833.33
    },
    {
      "product_type": "tenda",
      "quantity": 7,
      "revenue": 8950.00,
      "average_price": 1278.57
    }
  ]
}
```

#### GET /api/dashboard/recent-activity

Obtém atividades recentes do sistema.

**Permissões:** Admin, Seller

**Parâmetros de Query:**
- `limit` (opcional): Número máximo de atividades (padrão: 10)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "activities": [
    {
      "type": "quote",
      "id": 127,
      "description": "Orçamento #127 - toldo_retratil",
      "status": "approved",
      "value": 3250.00,
      "client_name": "João Silva",
      "seller_name": "Maria Santos",
      "created_at": "2025-08-12T10:30:00.000000",
      "updated_at": "2025-08-12T14:45:00.000000"
    },
    {
      "type": "quote",
      "id": 126,
      "description": "Orçamento #126 - pergolado",
      "status": "pending",
      "value": 4200.00,
      "client_name": "Ana Costa",
      "seller_name": "Carlos Oliveira",
      "created_at": "2025-08-12T09:15:00.000000",
      "updated_at": "2025-08-12T09:15:00.000000"
    }
  ]
}
```

### Endpoints de Relatórios

#### GET /api/dashboard/reports/sellers

Relatório de performance dos vendedores (apenas Admin).

**Permissões:** Admin

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "report_data": [
    {
      "seller_id": 1,
      "name": "Maria Santos",
      "email": "maria@empresa.com",
      "commission_rate": 0.05,
      "total_quotes": 35,
      "approved_quotes": 28,
      "pending_quotes": 5,
      "total_sales": 89500.00,
      "commission_earned": 4475.00,
      "conversion_rate": 80.0,
      "average_ticket": 3196.43
    },
    {
      "seller_id": 2,
      "name": "Carlos Oliveira",
      "email": "carlos@empresa.com",
      "commission_rate": 0.06,
      "total_quotes": 28,
      "approved_quotes": 18,
      "pending_quotes": 7,
      "total_sales": 65200.00,
      "commission_earned": 3912.00,
      "conversion_rate": 64.3,
      "average_ticket": 3622.22
    }
  ]
}
```

#### GET /api/dashboard/reports/clients

Relatório de clientes e seus gastos.

**Permissões:** Admin, Seller

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "report_data": [
    {
      "client_id": 1,
      "name": "João Silva",
      "email": "joao@cliente.com",
      "company_name": "Silva & Associados",
      "city": "São Paulo",
      "state": "SP",
      "total_quotes": 5,
      "total_spent": 15750.00,
      "last_quote_date": "2025-08-10T15:30:00.000000",
      "average_order": 3150.00
    },
    {
      "client_id": 2,
      "name": "Ana Costa",
      "email": "ana@cliente.com",
      "company_name": "Costa Empreendimentos",
      "city": "Rio de Janeiro",
      "state": "RJ",
      "total_quotes": 3,
      "total_spent": 12400.00,
      "last_quote_date": "2025-08-12T09:15:00.000000",
      "average_order": 4133.33
    }
  ]
}
```

#### GET /api/dashboard/reports/financial

Relatório financeiro detalhado (apenas Admin).

**Permissões:** Admin

**Parâmetros de Query:**
- `start_date` (opcional): Data inicial (formato: YYYY-MM-DD)
- `end_date` (opcional): Data final (formato: YYYY-MM-DD)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "financial_report": {
    "period": {
      "start_date": "2025-07-01",
      "end_date": "2025-08-12"
    },
    "summary": {
      "total_revenue": 125400.00,
      "total_commissions": 7524.00,
      "net_revenue": 117876.00,
      "commission_percentage": 6.0
    },
    "revenue_by_status": [
      {
        "status": "approved",
        "count": 42,
        "total": 125400.00
      },
      {
        "status": "pending",
        "count": 8,
        "total": 24500.00
      },
      {
        "status": "rejected",
        "count": 12,
        "total": 0.00
      }
    ],
    "revenue_by_product": [
      {
        "product_type": "toldo_retratil",
        "count": 18,
        "total": 52400.00
      },
      {
        "product_type": "toldo_fixo",
        "count": 15,
        "total": 38200.00
      },
      {
        "product_type": "pergolado",
        "count": 6,
        "total": 24800.00
      },
      {
        "product_type": "cobertura_policarbonato",
        "count": 3,
        "total": 10000.00
      }
    ],
    "seller_commissions": [
      {
        "seller_name": "Maria Santos",
        "commission_rate": 0.05,
        "sales": 45200.00,
        "commission": 2260.00
      },
      {
        "seller_name": "Carlos Oliveira",
        "commission_rate": 0.06,
        "sales": 38400.00,
        "commission": 2304.00
      }
    ]
  }
}
```

### Métricas e KPIs

#### Indicadores Principais

| Métrica | Descrição | Cálculo |
|---------|-----------|---------|
| Taxa de Conversão | Percentual de orçamentos aprovados | (Aprovados / Total) × 100 |
| Ticket Médio | Valor médio por venda | Total de Vendas / Número de Vendas |
| Receita Líquida | Receita após comissões | Receita Total - Comissões |
| ROI por Vendedor | Retorno por vendedor | (Vendas - Comissões) / Comissões |

#### Análise Temporal

- **Crescimento MoM:** Comparação mês a mês
- **Sazonalidade:** Identificação de padrões sazonais
- **Tendências:** Análise de tendências de longo prazo

#### Segmentação

- **Por Produto:** Performance por tipo de produto
- **Por Região:** Análise geográfica de vendas
- **Por Vendedor:** Performance individual
- **Por Cliente:** Análise de valor do cliente

### Filtros e Períodos

#### Filtros Temporais

```
GET /api/dashboard/charts/revenue?period=weekly
GET /api/dashboard/charts/revenue?period=monthly
GET /api/dashboard/charts/revenue?period=yearly
```

#### Filtros de Data Específica

```
GET /api/dashboard/reports/financial?start_date=2025-01-01&end_date=2025-06-30
```

### Exportação de Dados

#### Formatos Suportados

- **JSON:** Dados estruturados para integração
- **CSV:** Para análise em planilhas
- **PDF:** Relatórios formatados

#### Endpoints de Exportação

```
GET /api/dashboard/export/sellers?format=csv
GET /api/dashboard/export/financial?format=pdf&start_date=2025-01-01
```

### Integração com Gráficos

#### Chart.js

Dados otimizados para Chart.js:
```javascript
// Exemplo de uso com Chart.js
const chartData = {
  labels: revenueData.map(item => item.period),
  datasets: [{
    label: 'Receita',
    data: revenueData.map(item => item.revenue),
    backgroundColor: 'rgba(54, 162, 235, 0.2)',
    borderColor: 'rgba(54, 162, 235, 1)',
    borderWidth: 1
  }]
};
```

#### D3.js

Compatibilidade com D3.js para visualizações customizadas:
```javascript
// Exemplo de uso com D3.js
d3.json('/api/dashboard/charts/products')
  .then(data => {
    const svg = d3.select('#chart');
    // Criar visualização personalizada
  });
```

### Cache e Performance

#### Cache de Relatórios

- Relatórios são cacheados por 15 minutos
- Cache invalidado quando novos dados são inseridos
- Diferentes caches para diferentes usuários/permissões

#### Otimizações

- Consultas otimizadas com índices apropriados
- Agregações calculadas em tempo de consulta
- Paginação para grandes volumes de dados

### Alertas e Notificações

#### Alertas Automáticos

- Queda na taxa de conversão
- Metas de vendas não atingidas
- Orçamentos pendentes há muito tempo

#### Configuração de Alertas

```json
{
  "alert_type": "conversion_rate",
  "threshold": 60.0,
  "period": "monthly",
  "recipients": ["admin@empresa.com"]
}
```

### Casos de Uso Comuns

#### Dashboard Executivo

Combinação de múltiplos endpoints para visão completa:
```javascript
Promise.all([
  fetch('/api/dashboard/stats'),
  fetch('/api/dashboard/charts/revenue?period=monthly'),
  fetch('/api/dashboard/charts/products'),
  fetch('/api/dashboard/recent-activity?limit=5')
]).then(responses => {
  // Processar dados para dashboard
});
```

#### Relatório de Performance

Análise detalhada de vendedor:
```javascript
fetch('/api/dashboard/reports/sellers')
  .then(response => response.json())
  .then(data => {
    generatePerformanceReport(data.report_data);
  });
```

#### Análise Financeira

Relatório financeiro com período específico:
```javascript
const startDate = '2025-01-01';
const endDate = '2025-06-30';
fetch(`/api/dashboard/reports/financial?start_date=${startDate}&end_date=${endDate}`)
  .then(response => response.json())
  .then(data => {
    generateFinancialAnalysis(data.financial_report);
  });
```


## Geração de PDFs

### Visão Geral

O módulo de geração de PDFs permite criar documentos profissionais para orçamentos e relatórios, com proteção por senha e formatação personalizada. O sistema utiliza a biblioteca ReportLab para gerar PDFs de alta qualidade com layout responsivo e elementos visuais atraentes.

### Funcionalidades

- Geração de PDFs de orçamentos com proteção por senha
- Relatórios em PDF para vendedores, clientes e análises financeiras
- Layout profissional com logotipo e identidade visual
- Proteção por senha única para cada documento
- Preview de PDFs sem proteção
- Regeneração de senhas de acesso

### Endpoints de PDF

#### GET /api/pdf/quote/{id}

Gera e baixa o PDF de um orçamento específico.

**Permissões:** Admin, Seller (próprios), Client (próprios)

**Parâmetros:**
- `id` (URL): ID do orçamento
- `protected` (query, opcional): "true" para PDF protegido, "false" para sem proteção (padrão: "true")

**Exemplo de Requisição:**
```
GET /api/pdf/quote/123?protected=true
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
Retorna o arquivo PDF para download com headers apropriados:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="orcamento_123_20250812.pdf"
```

#### GET /api/pdf/quote/{id}/preview

Gera preview do PDF sem proteção por senha.

**Permissões:** Admin, Seller (próprios), Client (próprios)

**Resposta de Sucesso (200):**
Retorna o PDF para visualização no navegador:
```
Content-Type: application/pdf
Content-Disposition: inline
```

#### POST /api/pdf/quote/{id}/password

Obtém a senha do PDF do orçamento.

**Permissões:** Admin, Seller (próprios), Client (próprios)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "pdf_password": "AbC123Xy",
  "quote_id": 123
}
```

#### POST /api/pdf/quote/{id}/regenerate-password

Regenera a senha do PDF do orçamento.

**Permissões:** Admin, Seller (próprios)

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Nova senha gerada com sucesso",
  "pdf_password": "XyZ789Mn",
  "quote_id": 123
}
```

#### POST /api/pdf/unlock

Valida senha de PDF (para uso no frontend).

**Permissões:** Público (sem autenticação)

**Parâmetros:**
```json
{
  "quote_id": 123,
  "password": "AbC123Xy"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Senha correta",
  "quote_id": 123
}
```

**Resposta de Erro (401):**
```json
{
  "success": false,
  "error": "Senha incorreta"
}
```

### Relatórios em PDF

#### GET /api/pdf/report/sellers

Gera PDF do relatório de vendedores.

**Permissões:** Admin

**Resposta de Sucesso (200):**
Retorna arquivo PDF com relatório de performance dos vendedores.

#### GET /api/pdf/report/clients

Gera PDF do relatório de clientes.

**Permissões:** Admin, Seller

**Resposta de Sucesso (200):**
Retorna arquivo PDF com relatório de clientes e seus gastos.

#### GET /api/pdf/report/financial

Gera PDF do relatório financeiro.

**Permissões:** Admin

**Parâmetros de Query:**
- `start_date` (opcional): Data inicial (YYYY-MM-DD)
- `end_date` (opcional): Data final (YYYY-MM-DD)

**Resposta de Sucesso (200):**
Retorna arquivo PDF com análise financeira detalhada.

### Estrutura do PDF de Orçamento

#### Cabeçalho

- Logotipo da empresa
- Nome da empresa: "COBERTURAS CASADOS TOLDOS"
- Slogan: "Soluções em Toldos e Coberturas"

#### Informações do Orçamento

| Campo | Descrição |
|-------|-----------|
| Número do Orçamento | ID único do orçamento |
| Data | Data de geração do PDF |
| Status | Status atual do orçamento |
| Validade | Prazo de validade (30 dias) |

#### Dados do Cliente

- Nome completo
- Email de contato
- Empresa (se aplicável)
- Telefone
- Endereço completo
- Cidade e Estado

#### Especificações do Produto

- Tipo de produto (toldo, cobertura, etc.)
- Dimensões detalhadas (largura, comprimento, altura)
- Área total de cobertura
- Materiais selecionados
- Acessórios inclusos

#### Valor do Orçamento

Tabela detalhada com:
- Descrição do produto/serviço
- Quantidade (área em m²)
- Valor unitário por m²
- Valor total

#### Condições Comerciais

- Prazo de entrega: 15 a 20 dias úteis
- Forma de pagamento: 50% aprovação + 50% entrega
- Garantia: 12 meses contra defeitos
- Instalação inclusa
- Validade do orçamento: 30 dias

#### Rodapé

Informações de contato da empresa.

### Proteção por Senha

#### Geração de Senhas

- Senhas alfanuméricas de 8 caracteres
- Geradas automaticamente na criação do orçamento
- Únicas para cada orçamento
- Podem ser regeneradas por admin ou vendedor responsável

#### Segurança

- Senhas armazenadas em texto plano no banco (para recuperação)
- PDFs protegidos usando criptografia padrão PDF
- Acesso controlado por permissões de usuário

#### Fluxo de Acesso

1. Cliente recebe orçamento por email
2. Tenta abrir PDF e é solicitada senha
3. Cliente solicita senha ao vendedor
4. Vendedor fornece senha via endpoint da API
5. Cliente acessa conteúdo do PDF

### Customização Visual

#### Cores Corporativas

- Azul principal: #2E86AB
- Cinza para texto: #333333
- Fundo claro: #F8F9FA

#### Tipografia

- Títulos: Helvetica-Bold, 24pt
- Subtítulos: Helvetica-Bold, 16pt
- Texto normal: Helvetica, 11pt

#### Layout

- Margens: 2cm em todas as bordas
- Espaçamento consistente entre seções
- Tabelas com bordas e sombreamento
- Alinhamento profissional

### Relatórios Especializados

#### Relatório de Vendedores

Inclui:
- Lista de todos os vendedores
- Estatísticas de performance
- Total de orçamentos e vendas
- Comissões ganhas
- Taxa de conversão

#### Relatório de Clientes

Inclui:
- Lista de clientes ativos
- Histórico de compras
- Valor total gasto
- Última data de orçamento
- Informações de contato

#### Relatório Financeiro

Inclui:
- Resumo financeiro do período
- Receita por tipo de produto
- Comissões por vendedor
- Análise de status de orçamentos
- Gráficos e tabelas detalhadas

### Casos de Uso Comuns

#### Download de Orçamento Protegido

```javascript
// Baixar PDF protegido
fetch('/api/pdf/quote/123?protected=true', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'orcamento_123.pdf';
  a.click();
});
```

#### Validação de Senha

```javascript
// Validar senha antes de mostrar conteúdo
function validatePDFPassword(quoteId, password) {
  return fetch('/api/pdf/unlock', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      quote_id: quoteId,
      password: password
    })
  })
  .then(response => response.json())
  .then(data => data.success);
}
```

#### Preview sem Senha

```javascript
// Mostrar preview para usuários autenticados
function showPDFPreview(quoteId) {
  const iframe = document.createElement('iframe');
  iframe.src = `/api/pdf/quote/${quoteId}/preview`;
  iframe.style.width = '100%';
  iframe.style.height = '600px';
  document.getElementById('pdf-container').appendChild(iframe);
}
```

#### Regenerar Senha

```javascript
// Regenerar senha (admin/vendedor)
function regeneratePassword(quoteId) {
  return fetch(`/api/pdf/quote/${quoteId}/regenerate-password`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert(`Nova senha: ${data.pdf_password}`);
      return data.pdf_password;
    }
  });
}
```

### Tratamento de Erros

#### Erros Comuns

| Código | Erro | Descrição |
|--------|------|-----------|
| 401 | Unauthorized | Token inválido ou ausente |
| 403 | Forbidden | Sem permissão para acessar o orçamento |
| 404 | Not Found | Orçamento não encontrado |
| 500 | Internal Error | Erro na geração do PDF |

#### Exemplo de Tratamento

```javascript
fetch('/api/pdf/quote/123')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.blob();
  })
  .then(blob => {
    // Processar PDF
  })
  .catch(error => {
    console.error('Erro ao gerar PDF:', error);
    alert('Erro ao gerar PDF. Tente novamente.');
  });
```

### Performance e Otimização

#### Cache de PDFs

- PDFs são gerados sob demanda
- Não há cache persistente (dados podem mudar)
- Geração otimizada com templates reutilizáveis

#### Limitações

- Tamanho máximo de PDF: 50MB
- Timeout de geração: 30 segundos
- Máximo 10 gerações simultâneas por usuário

### Integração com Email

#### Envio Automático

PDFs podem ser enviados automaticamente por email quando:
- Novo orçamento é criado
- Status do orçamento é alterado
- Cliente solicita reenvio

#### Template de Email

```html
Prezado(a) Cliente,

Segue em anexo seu orçamento #123.

O arquivo PDF está protegido por senha.
Para obter a senha, entre em contato com seu vendedor.

Atenciosamente,
Coberturas Casados Toldos
```


## Códigos de Erro

### Códigos de Status HTTP

| Código | Status | Descrição | Quando Ocorre |
|--------|--------|-----------|---------------|
| 200 | OK | Requisição bem-sucedida | Operações de consulta e atualização |
| 201 | Created | Recurso criado com sucesso | Criação de usuários, orçamentos, etc. |
| 400 | Bad Request | Dados inválidos na requisição | Validação de campos obrigatórios |
| 401 | Unauthorized | Autenticação necessária ou inválida | Token ausente ou expirado |
| 403 | Forbidden | Acesso negado | Permissões insuficientes |
| 404 | Not Found | Recurso não encontrado | ID inexistente |
| 409 | Conflict | Conflito de dados | Email já cadastrado |
| 422 | Unprocessable Entity | Dados válidos mas não processáveis | Regras de negócio violadas |
| 500 | Internal Server Error | Erro interno do servidor | Falhas não tratadas |

### Mensagens de Erro Padronizadas

#### Autenticação

```json
{
  "error": "Token de autorização necessário"
}
```

```json
{
  "error": "Token inválido ou expirado"
}
```

```json
{
  "error": "Credenciais inválidas"
}
```

#### Autorização

```json
{
  "error": "Acesso negado. Permissões insuficientes."
}
```

```json
{
  "error": "Apenas administradores podem acessar este recurso"
}
```

#### Validação

```json
{
  "error": "Email já está em uso"
}
```

```json
{
  "error": "Senha deve ter pelo menos 8 caracteres"
}
```

```json
{
  "error": "Campos obrigatórios: email, password, name"
}
```

#### Recursos

```json
{
  "error": "Usuário não encontrado"
}
```

```json
{
  "error": "Orçamento não encontrado"
}
```

```json
{
  "error": "Cliente não encontrado"
}
```

### Tratamento de Erros no Frontend

#### Exemplo Genérico

```javascript
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    handleApiError(error);
    throw error;
  }
}

function handleApiError(error) {
  if (error.message.includes('Token')) {
    // Redirecionar para login
    window.location.href = '/login';
  } else if (error.message.includes('Acesso negado')) {
    // Mostrar mensagem de permissão
    showErrorMessage('Você não tem permissão para esta ação');
  } else {
    // Erro genérico
    showErrorMessage(error.message);
  }
}
```

## Exemplos de Uso

### Fluxo Completo de Orçamento

#### 1. Registro e Login

```javascript
// Registrar novo cliente
const registerData = {
  email: 'cliente@exemplo.com',
  password: 'MinhaSenh@123',
  name: 'João Silva',
  role: 'client'
};

const registerResponse = await fetch('/api/auth/register', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(registerData)
});

// Login após verificação de email
const loginData = {
  email: 'cliente@exemplo.com',
  password: 'MinhaSenh@123'
};

const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(loginData)
});

const { access_token } = await loginResponse.json();
```

#### 2. Criação de Orçamento (Vendedor)

```javascript
// Criar orçamento para cliente
const quoteData = {
  client_id: 1,
  product_type: 'toldo_retratil',
  dimensions: {
    width: 4.0,
    length: 3.0,
    height: 2.5,
    angle: 15
  },
  materials: {
    estrutura: 'aluminio',
    cobertura: 'lona_premium',
    cor_estrutura: 'branco',
    cor_cobertura: 'azul',
    motorizado: true,
    sensor_vento: true
  },
  notes: 'Cliente solicitou instalação urgente'
};

const quoteResponse = await fetch('/api/quotes', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${sellerToken}`
  },
  body: JSON.stringify(quoteData)
});

const { quote, pdf_password } = await quoteResponse.json();
```

#### 3. Visualização 3D

```javascript
// Gerar dados para visualização 3D
const visualizationData = {
  product_type: 'toldo_retratil',
  dimensions: quote.dimensions,
  materials: quote.materials,
  accessories: {
    motorizado: true,
    sensor_vento: true,
    led_lighting: false
  }
};

const visualResponse = await fetch('/api/visualization/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(visualizationData)
});

const { visualization_data } = await visualResponse.json();

// Usar dados com Three.js
const scene = new THREE.Scene();
const geometry = new THREE.BufferGeometry();
geometry.setFromPoints(visualization_data.geometry.vertices.map(v => new THREE.Vector3(...v)));

const material = new THREE.MeshStandardMaterial({
  color: visualization_data.materials.cover.color,
  roughness: visualization_data.materials.cover.roughness
});

const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

#### 4. Aprovação do Orçamento (Cliente)

```javascript
// Cliente aprova orçamento
const approvalResponse = await fetch(`/api/quotes/${quote.id}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${clientToken}`
  },
  body: JSON.stringify({
    status: 'approved'
  })
});
```

#### 5. Download do PDF

```javascript
// Download do PDF protegido
const pdfResponse = await fetch(`/api/pdf/quote/${quote.id}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const pdfBlob = await pdfResponse.blob();
const url = window.URL.createObjectURL(pdfBlob);
const a = document.createElement('a');
a.href = url;
a.download = `orcamento_${quote.id}.pdf`;
a.click();

// Obter senha do PDF
const passwordResponse = await fetch(`/api/pdf/quote/${quote.id}/password`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { pdf_password } = await passwordResponse.json();
console.log('Senha do PDF:', pdf_password);
```

### Dashboard Administrativo

```javascript
// Carregar dados do dashboard
async function loadDashboard() {
  try {
    const [stats, revenue, products, activity] = await Promise.all([
      fetch('/api/dashboard/stats', {
        headers: {'Authorization': `Bearer ${adminToken}`}
      }).then(r => r.json()),
      
      fetch('/api/dashboard/charts/revenue?period=monthly', {
        headers: {'Authorization': `Bearer ${adminToken}`}
      }).then(r => r.json()),
      
      fetch('/api/dashboard/charts/products', {
        headers: {'Authorization': `Bearer ${adminToken}`}
      }).then(r => r.json()),
      
      fetch('/api/dashboard/recent-activity?limit=10', {
        headers: {'Authorization': `Bearer ${adminToken}`}
      }).then(r => r.json())
    ]);

    // Atualizar interface
    updateStatsCards(stats.stats.overview);
    createRevenueChart(revenue.chart_data);
    createProductsChart(products.chart_data);
    updateActivityFeed(activity.activities);
    
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error);
  }
}

function updateStatsCards(overview) {
  document.getElementById('total-clients').textContent = overview.total_clients;
  document.getElementById('total-revenue').textContent = 
    `R$ ${overview.total_revenue.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
  document.getElementById('conversion-rate').textContent = 
    `${overview.conversion_rate}%`;
  document.getElementById('average-ticket').textContent = 
    `R$ ${overview.average_ticket.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
}

function createRevenueChart(data) {
  const ctx = document.getElementById('revenue-chart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(item => item.period),
      datasets: [{
        label: 'Receita Mensal',
        data: data.map(item => item.revenue),
        borderColor: '#2E86AB',
        backgroundColor: 'rgba(46, 134, 171, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return 'R$ ' + value.toLocaleString('pt-BR');
            }
          }
        }
      }
    }
  });
}
```

### Configurador de Produto

```javascript
class ProductConfigurator {
  constructor() {
    this.config = {
      product_type: 'toldo_retratil',
      dimensions: { width: 3.0, length: 2.0, height: 2.5 },
      materials: { estrutura: 'aluminio', cobertura: 'lona_comum' },
      accessories: {}
    };
    this.scene = null;
    this.init();
  }

  async init() {
    await this.loadMaterials();
    this.setupUI();
    this.initThreeJS();
    this.updateVisualization();
  }

  async loadMaterials() {
    const response = await fetch('/api/visualization/materials');
    this.materials = await response.json();
  }

  setupUI() {
    // Configurar controles de dimensões
    document.getElementById('width-slider').addEventListener('input', (e) => {
      this.config.dimensions.width = parseFloat(e.target.value);
      this.updateVisualization();
      this.updatePrice();
    });

    document.getElementById('length-slider').addEventListener('input', (e) => {
      this.config.dimensions.length = parseFloat(e.target.value);
      this.updateVisualization();
      this.updatePrice();
    });

    // Configurar seletores de material
    document.getElementById('structure-select').addEventListener('change', (e) => {
      this.config.materials.estrutura = e.target.value;
      this.updateVisualization();
      this.updatePrice();
    });

    document.getElementById('cover-select').addEventListener('change', (e) => {
      this.config.materials.cobertura = e.target.value;
      this.updateVisualization();
      this.updatePrice();
    });
  }

  initThreeJS() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, 800/600, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer();
    this.renderer.setSize(800, 600);
    document.getElementById('3d-container').appendChild(this.renderer.domElement);

    // Iluminação
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    this.scene.add(directionalLight);

    // Controles de câmera
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.camera.position.set(5, 5, 5);
    this.controls.update();

    this.animate();
  }

  async updateVisualization() {
    try {
      const response = await fetch('/api/visualization/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(this.config)
      });

      const { visualization_data } = await response.json();
      this.renderProduct(visualization_data);
      
    } catch (error) {
      console.error('Erro ao atualizar visualização:', error);
    }
  }

  renderProduct(data) {
    // Limpar objetos existentes
    while(this.scene.children.length > 2) { // Manter luzes
      this.scene.remove(this.scene.children[2]);
    }

    // Criar geometria
    const geometry = new THREE.BufferGeometry();
    const vertices = new Float32Array(data.geometry.vertices.flat());
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

    // Criar material
    const material = new THREE.MeshStandardMaterial({
      color: data.materials.cover.color,
      roughness: data.materials.cover.roughness,
      metalness: data.materials.cover.metalness
    });

    // Criar mesh
    const mesh = new THREE.Mesh(geometry, material);
    this.scene.add(mesh);

    // Adicionar cotas
    this.addDimensions(data.dimensions);
  }

  addDimensions(dimensions) {
    const loader = new THREE.FontLoader();
    loader.load('/fonts/helvetiker_regular.typeface.json', (font) => {
      // Cota de largura
      const widthGeometry = new THREE.TextGeometry(`${dimensions.width}m`, {
        font: font,
        size: 0.2,
        height: 0.01
      });
      const widthMaterial = new THREE.MeshBasicMaterial({color: 0x000000});
      const widthMesh = new THREE.Mesh(widthGeometry, widthMaterial);
      widthMesh.position.set(dimensions.width/2, -0.5, 0);
      this.scene.add(widthMesh);

      // Cota de comprimento
      const lengthGeometry = new THREE.TextGeometry(`${dimensions.length}m`, {
        font: font,
        size: 0.2,
        height: 0.01
      });
      const lengthMaterial = new THREE.MeshBasicMaterial({color: 0x000000});
      const lengthMesh = new THREE.Mesh(lengthGeometry, lengthMaterial);
      lengthMesh.position.set(-0.5, dimensions.length/2, 0);
      lengthMesh.rotation.z = Math.PI/2;
      this.scene.add(lengthMesh);
    });
  }

  async updatePrice() {
    try {
      const response = await fetch('/api/visualization/calculate-price', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(this.config)
      });

      const { price_breakdown } = await response.json();
      
      document.getElementById('total-price').textContent = 
        `R$ ${price_breakdown.total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
      
      document.getElementById('area').textContent = 
        `${price_breakdown.area} m²`;
        
    } catch (error) {
      console.error('Erro ao calcular preço:', error);
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}

// Inicializar configurador
const configurator = new ProductConfigurator();
```

## Configuração e Deploy

### Variáveis de Ambiente

```bash
# Configurações do Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_secreta_muito_segura

# Banco de dados
DATABASE_URL=sqlite:///toldos.db
# ou para PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/toldos_db

# JWT
JWT_SECRET_KEY=sua_chave_jwt_secreta
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hora
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 dias

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
MAIL_DEFAULT_SENDER=noreply@toldos.com

# CORS
CORS_ORIGINS=http://localhost:3000,https://seudominio.com
```

### Instalação

```bash
# Clonar repositório
git clone <url_do_repositorio>
cd toldos_backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Inicializar banco de dados
python -c "from src.main import app; app.app_context().push(); from src.models.user import db; db.create_all()"

# Executar aplicação
python src/main.py
```

### Deploy em Produção

#### Usando Gunicorn

```bash
# Instalar Gunicorn
pip install gunicorn

# Executar com Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app
```

#### Usando Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:app"]
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.toldos.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoramento

#### Health Check

```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

#### Logs

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Backup

#### Banco de Dados

```bash
# SQLite
cp toldos.db backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL
pg_dump toldos_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Arquivos

```bash
# Backup completo
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz src/ static/ uploads/
```

---

**Documentação gerada por Manus AI**  
**Versão:** 1.0  
**Data:** 12 de agosto de 2025

Para suporte técnico ou dúvidas sobre a API, entre em contato com a equipe de desenvolvimento.

