

  # 📘 Projeto Gestão de Eventos API

  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python)](https://www.python.org/downloads/)
  [![Django](https://img.shields.io/badge/Django-5.0%2B-green.svg?logo=Django)](https://www.djangoproject.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

  ## Instituições de Fomento e Parceria
  [![Website IFB](https://img.shields.io/badge/Website-IFB-%23508C3C.svg?labelColor=%23C8102E)](https://www.ifb.edu.br/)  
  [![Website ihwbr](https://img.shields.io/badge/Website-ihwbr-%23DAA520.svg?labelColor=%232E2E2E)](https://hardware.org.br/)

---

  ## Orientador
  Inclua aqui o nome e link para o perfil do orientador responsável.

---

  ## Sumário

  - [Visão Geral](#visão-geral)
  - [Pacotes Utilizados](#pacotes-utilizados)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Diagrama de Banco de Dados](#diagrama-de-banco-de-dados)
  - [Documentação da API](#documentação-da-api)
  - [Configuração do Ambiente](#configuração-do-ambiente)
  - [Deploy](#deploy)

---

  ## Visão Geral

  Este projeto implementa uma **API de Gestão de Projetos Colaborativos** voltada para coordenadores, professores e estudantes.  
  O sistema permite organizar **projetos**, **equipes** e **usuários**, com regras de permissão claras:

  - **Admin/staff** → pode criar, editar e excluir projetos e equipes, além de definir líderes.  
  - **Usuário comum (aluno/professor)** → só pode listar e consultar projetos e equipes em que participa.  

  Funcionalidades principais:
  - Cadastro de projetos com status e datas.  
  - Criação de equipes vinculadas a projetos.  
  - Definição de membros e líder da equipe.  
  - Dashboard de projetos com equipes e participantes.  
  - Documentação interativa da API (Swagger/ReDoc).  

---

  ## Pacotes Utilizados

  | Pacote                  | Versão | Descrição                                      |
  | ----------------------- | ------ | ---------------------------------------------- |
  | Django                  | >=5.0  | Framework web principal                        |
  | djangorestframework     | latest | Toolkit para construção de APIs REST           |
  | drf-spectacular         | latest | Geração automática de documentação OpenAPI     |
  | drf-spectacular-sidecar | latest | Arquivos estáticos para Swagger/ReDoc          |
  | rest_framework.authtoken| latest | Autenticação via token                         |
  | sqlite3                 | latest | Banco de dados leve para desenvolvimento       |

  > **Nota:** Consulte o arquivo `requirements.txt` para a lista completa e versões exatas.

---

  ## Estrutura do Projeto
  ```bash
02-Gerencia_projetos/ 
├── manage.py 
├── requirements.txt 
├── devlab/ 
│ ├── settings.py 
| │ ── urls.py 
│ └── wsgi.py 
├── core/ 
│ ├── models.py 
│ ├── views.py 
│ ├── serializers.py 
│ ├── admin.py 
│ └── ... 
└── docs/ └── database_diagram.png

  ```
  - **projeto/** → configurações principais do Django.  
  - **core/** → aplicação principal com modelos, views, serializers e rotas.  
  - **docs/** → documentação auxiliar (diagramas, imagens).  

---

  ## Diagrama de Banco de Dados

  ![Diagrama de Banco de Dados](./docs/database_diagram.png)



# Diagrama ER – DevLab Project API

## Entidades e Relacionamentos

### Projeto
| Campo             | Tipo      | Descrição                                |
| ----------------- | --------- | ---------------------------------------- |
| id                | PK (int)  | Identificador único do projeto           |
| titulo            | CharField | Nome do projeto                          |
| descricao         | TextField | Descrição detalhada                      |
| cliente           | CharField | Cliente responsável                      |
| status            | CharField | Status (planejado, andamento, concluído) |
| data_inicio       | DateField | Data de início                           |
| data_fim_prevista | DateField | Data prevista de término                 |

---

### Equipe
| Campo      | Tipo      | Descrição                         |
| ---------- | --------- | --------------------------------- |
| id         | PK (int)  | Identificador único da equipe     |
| nome       | CharField | Nome da equipe                    |
| descricao  | TextField | Descrição da equipe               |
| projeto_id | FK (int)  | Chave estrangeira → Projeto (1:N) |
| lider_id   | OneToOne  | Chave única → User (1:1)          |

---

### User
| Campo    | Tipo       | Descrição                      |
| -------- | ---------- | ------------------------------ |
| id       | PK (int)   | Identificador único do usuário |
| username | CharField  | Nome de login                  |
| email    | EmailField | Email do usuário               |
| password | CharField  | Senha (hash)                   |





---



## 🔗 Relacionamentos

- **Projeto (1) ↔ (N) Equipe**  
  Um projeto pode ter várias equipes, mas cada equipe pertence a um único projeto.

- **Equipe (N) ↔ (N) User (membros)**  
  Uma equipe pode ter vários membros, e um usuário pode participar de várias equipes.

- **Equipe (1) ↔ (1) User (líder)**  
  Uma equipe tem um líder único, e um usuário pode liderar apenas uma equipe.

---

## 📐 Representação Visual em Texto



  **Entidades principais:**
  - **Projeto** → agrupa várias equipes.  
  - **Equipe** → pertence a um projeto, tem membros e um líder.  
  - **User** → pode estar em várias equipes e liderar uma delas.  

  Relacionamentos:
  - Projeto ↔ Equipe → **1:N**  
  - Equipe ↔ User (membros) → **N:N**  
  - Equipe ↔ User (líder) → **1:1**  

---

  ## Documentação da API

  A documentação interativa está disponível em:
  - `/api/docs/` → Swagger UI  / spectacular
  - `/api/docs/redoc/` → ReDoc  

  ### Endpoints Principais

  | Método | Endpoint                        | Descrição                                   | Autenticação |
  | ------ | ------------------------------- | ------------------------------------------- | ------------ |
  | GET    | `/api/projetos/`                | Lista projetos (admin vê todos, usuário só os seus) | Requerida    |
  | GET    | `/api/projetos/{id}/dashboard/` | Detalhes do projeto + equipes + participantes | Requerida    |
  | GET    | `/api/equipes/`                 | Lista equipes (admin vê todas, usuário só as suas) | Requerida    |
  | POST   | `/api/equipes/{id}/definir_lider/` | Define líder da equipe (admin apenas)       | Requerida    |
  | GET    | `/api/users/{id}/visao_geral/`  | Dados do usuário + projetos + equipes       | Requerida    |



  ## Configuração do Ambiente

1. **Clone o repositório:**


```bash
     git clone [https://github.com/usuario/projeto_api.git](https://github.com/diegomo2/Projeto_integrador_gerencia_projetos.git)
     cd Projeto_integrador_gerencia_projetos
```

  1. **Crie um ambiente virtual:**

     

      ```bash
         python -m venv venv
         source venv/bin/activate  # Linux/Mac
         venv\Scripts\activate     # Windows
      ```

  2. **Instale as dependências:**

     

     ```bash
     pip install -r requirements.txt
     ```

  3. **Configure as variáveis de ambiente:**

     

     ```bash
     cp .env.example .env
     # Edite .env com suas credenciais
     ```

  4. **Aplique as migrações e inicie o servidor:**

     

     ```bash
     python manage.py migrate
     python manage.py createsuperuser
     python manage.py runserver
     ```



  ## Deploy (opcional)

  ### Plataforma Recomendada: [Render / Railway / AWS]

  1. **Prepare o** `Procfile`**:**

     Código

     ```
     web: gunicorn projeto.wsgi:application --log-file -
     ```

  2. **Configure variáveis de ambiente** na plataforma de deploy.

  3. **Execute migrações em produção:**

     bash

     ```
     python manage.py migrate
     ```

  4. **Colete arquivos estáticos (se aplicável):**

     bash

     ```
     python manage.py collectstatic
     ```
