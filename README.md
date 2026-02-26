# 🚀 FastAPI Study: Task Manager API

Este repositório contém uma aplicação rápida e simples desenvolvida com o objetivo de estudar e praticar o ecossistema do **FastAPI**. 

A aplicação consiste em uma API para gerenciamento de usuários e tarefas (To-Do), focando em conceitos essenciais de back-end, como banco de dados assíncrono, segurança, testes e boas práticas.

## 🛠️ Funcionalidades

- **Gestão de Usuários:** Criação e listagem de usuários com verificação de dados duplicados (email/username).
- **Gestão de Tarefas:** Criação de tarefas e vínculo direto com o usuário criador.
- **Segurança e Autenticação:** - Autenticação via **JWT (JSON Web Tokens)** com tempo de expiração.
  - Senhas salvas com hash de segurança.
  - Validação de usuários por rota (garantindo que um usuário só possa acessar/modificar os recursos permitidos a ele).
- **Testes Automatizados:** Cobertura de testes garantindo que as regras de negócio e rotas funcionem como o esperado em cada etapa.

## 💻 Tecnologias Utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/):** Framework web principal para a construção da API.
- **[SQLAlchemy](https://www.sqlalchemy.org/):** ORM utilizado para o controle e consultas ao banco de dados de forma assíncrona.
- **[Poetry](https://python-poetry.org/):** Gerenciador de dependências e ambientes virtuais.
- **[Pytest](https://docs.pytest.org/) & Coverage:** Ferramentas para testes das rotas/consultas e validação da cobertura de testes.

## 🔍 Exemplo de Código

Abaixo, um exemplo de como a rota de criação de usuários foi construída, utilizando sessões assíncronas do banco de dados e injeção de dependências do FastAPI:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from http import HTTPStatus

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: AsyncSession = Depends(get_session)):
    # Verifica se o usuário ou email já existem
    db_user = await session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Username já existe")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Email já existe")

    # Cria o usuário com a senha criptografada
    db_user = User(
        **user.model_dump(exclude={"password"}),
        password=get_password_hash(user.password),
    )
    
    session.add(instance=db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user
```

## ⚙️ Como executar o projeto

Certifique-se de ter o **Poetry** instalado na sua máquina.

**1. Clone o repositório:**
```bash
git clone https://github.com/AndersonFilho14/fastapi_zero.git
cd <NOME-DA-PASTA>
```

**2. Instale as dependências:**
```bash
poetry install
```

**3. Ative o ambiente virtual:**
```bash
poetry shell
```

**4. Rode os testes (opcional):**
```bash
pytest --cov
```

**5. Inicie a aplicação:**
```bash
uvicorn main:app --reload
```
> **Nota:** Acesse a documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI em: `http://127.0.0.1:8000/docs`