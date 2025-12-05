# 📅 API de Gestão de Eventos

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-green.svg?logo=Django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14%2B-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Sobre o Projeto
Este sistema é uma API RESTful robusta para gerenciamento completo de eventos acadêmicos e corporativos. O projeto permite que organizadores criem eventos e atividades, enquanto participantes podem se inscrever e visualizar a programação.

O sistema conta com painel administrativo moderno (**Jazzmin**), documentação automática (**Spectacular**) e autenticação (**Token** para API).

---

## 🚀 Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| **Django** | Framework Web Principal |
| **Django REST Framework** | Criação da API e Serializers |
| **SQLite3** | Banco de dados (ambiente de desenvolvimento) |
| **Django Filter** | Filtros avançados de busca |
| **Jazzmin** | Interface administrativa moderna e responsiva |
| **Drf-Spectacular** | Documentação interativa (Swagger UI) |
| **Pillow** | Gerenciamento de imagens (Banners dos eventos) |

---

## 📂 Estrutura do Projeto

```bash
gestao_eventos/          # Raiz do Projeto
│
├── media/               # Uploads (Banners de eventos)
├── templates/
│   └── index.html       # Frontend (Landing Page)
├── core/                # App Principal
│   ├── models.py        # Banco de Dados (Eventos, Atividades, etc)
│   ├── views.py         # Lógica (ViewSets e Actions)
│   ├── serializers.py   # Validação e Transformação JSON
│   ├── urls.py          # Rotas da API
│   └── tests.py         # Testes Automatizados
├── gestao_eventos/      # Configurações do Django
│   ├── settings.py      # Configuração de Apps, Banco e Auth
│   └── urls.py          # Rotas Globais (Admin, API, Docs)
├── manage.py
└── requirements.txt
```
---

## 🗂️  Modelo de Dados (Entidades)
O banco de dados foi modelado para suportar relacionamentos complexos:

### 1. **Participante (User)**:
- Usuário customizado (herda de AbstractUser).
- Campos extras: celular, tipo (estudante, palestrante, organizador).

### 2. **Evento**:
- Entidade principal.
- Possui banner (imagem), datas, local e descrição.
- Relacionamento 1:N com Atividades.

### 3. **Atividade**:
- Sub-eventos (Workshops, Palestras).
- Possui um responsavel (Participante).

### 4. **Inscrição**:
- Tabela associativa (N:N) entre Participante e Evento.
- Registra a data e evita inscrições duplicadas.

---

## ⚙️ Instalação e Configuração
Siga os passos abaixo para rodar o projeto localmente:

### 1. Configurar Ambiente
```bash
# Clone o repositório
git clone https://github.com/mateussalvador/gestao-eventos.git
cd gestao-eventos

# Crie e ative o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

```
### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Banco de Dados e Usuário
```bash
# Cria as tabelas no banco SQLite
python manage.py makemigrations
python manage.py migrate

# Cria o administrador do sistema
python manage.py createsuperuser
# Defina usuário (ex: admin) e senha (ex: 123)
```

### 4. Rodar o Servidor
```bash
python manage.py runserver
```

---

## 🔌 Documentação da API
A documentação interativa é gerada automaticamente pelo Swagger. Acesse: http://127.0.0.1:8000/api/docs/

### Principais Endpoints
| Método | Rota                             | Descrição                     | Auth |
| :----- | :------------------------------- | :---------------------------- | :--- |
| POST   | /api/token/                      | Obtém Token de Acesso (Login) |  🔓  |
| GET    | /api/eventos                     | Lista todos os eventos        |  🔓  |
| POST   | /api/eventos/                    | Cria novo evento              |  🔒
| GET    | /api/eventos/{id}/dashboard/     | Dados do evento               |  🔓  |
| POST   | /api/eventos/{id}/participantes/ | Inscrever-se no evento        |  🔒  |
| GET    | /api/atividades/                 | Lista atividades              |  🔓  |

**Nota:** Rotas com 🔒 exigem o `header Authorization: Token SEU_TOKEN`.

---

## 🧪 Testes Automatizados
O projeto inclui testes unitários para validar regras de negócio (ex: impedir inscrição dupla).

Para rodar os testes:
```bash
python manage.py test
```

---

## 🎨 Painel Administrativo
O sistema utiliza o Jazzmin para uma interface administrativa profissional. Acesse: http://127.0.0.1:8000/admin/

### Funcionalidades do Admin:
- Gerenciar Usuários e Permissões.
- Criar Eventos e fazer upload de Banners.
- Monitorar Inscrições.
