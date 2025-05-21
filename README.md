# Microsserviço de Pagamentos

Este repositório contém o microsserviço de pagamentos responsável por gerenciar as transações financeiras da plataforma.

## Tecnologias

- **Framework**: FastAPI
- **Linguagem**: Python 3.10+
- **Banco de Dados**: MongoDB
- **Testes**: Pytest + Coverage

## Estrutura do Projeto

```
tech/
├── api/
│   └── payments_router.py
├── domain/
│   └── entities/
├── infra/
│   └── repositories/
├── interfaces/
│   ├── controllers/
│   └── schemas/
└── use_cases/
    └── payments/
```

## Configuração do Ambiente

### Requisitos

- Python 3.10+
- MongoDB 5.0+


## Banco de Dados

O serviço utiliza MongoDB como banco de dados principal. A estrutura básica inclui:

- **Database**: `payments_db`
- **Collections**: `payments`, `payment_methods`

## Endpoints da API

- `GET /api/payments/` - Lista pagamentos
- `GET /api/payments/{id}` - Obtém um pagamento específico
- `POST /api/payments/` - Cria um novo pagamento
- `PUT /api/payments/{id}` - Atualiza um pagamento
- `DELETE /api/payments/{id}` - Remove um pagamento

## Testes

### Executando Testes Unitários

```bash
# Execute todos os testes
pytest

# Execute testes com cobertura
pytest --cov=tech tests/

# Gere relatório de cobertura
pytest --cov=tech --cov-report=html tests/
```

### Executando Testes BDD

O projeto utiliza testes BDD (Behavior-Driven Development) com Behave para garantir que os requisitos de negócio sejam atendidos.

```bash
# Execute todos os testes BDD
behave tests/tech/bdd/features/

# Execute um cenário específico
behave tests/tech/bdd/features/orders.feature

# Execute testes BDD com tags específicas
behave tests/tech/bdd/features/ --tags=checkout
```

### Cobertura de Testes


![Cobertura de Testes](.coverage.png)

> **Nota**: A imagem acima mostra a estrutura de diretórios de teste, incluindo nossos testes BDD que seguem a metodologia Gherkin para definir cenários de negócio.

## Repositórios Relacionados

- [Microsserviço de Produtos](https://github.com/sua-organizacao/products-microservice)
- [Microsserviço de Usuários](https://github.com/sua-organizacao/users-microservice)
- [API Gateway](https://github.com/sua-organizacao/api-gateway)