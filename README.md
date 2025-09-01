### Sistema de Gestão de Protocolos em Django

Este é um sistema de gestão de protocolos baseado em Python com o framework Django. Ele permite o registro, acompanhamento e organização de protocolos de atendimento, problemas ou tarefas, oferecendo um dashboard para visualização geral e ferramentas de busca e exportação.

---

### Funcionalidades ✨

* **Dashboard**: Visão geral com o total de protocolos e a contagem por status (Aberto, Em Andamento, Finalizado).
* **Novo Protocolo**: Criação de novos protocolos com campos como clientes, BUIC do dispositivo e descrição do problema.
* **Gestão de Clientes**: Possibilidade de adicionar novos clientes via um formulário AJAX diretamente da página de criação de protocolo.
* **Busca Global**: Funcionalidade de busca por protocolos e clientes, procurando em campos como número do protocolo, BUIC, descrição do problema e nome/email do cliente.
* **Exportação de Dados**: Exporta todos os protocolos para um arquivo CSV.
* **População de Dados (Seed)**: Um comando de gestão (`seed_data`) para popular o banco de dados com usuários e protocolos de exemplo, facilitando a configuração inicial.
* **Integração com o Admin do Django**: Interface administrativa customizada para gerenciar usuários, clientes, protocolos e atualizações.

---

### Pré-requisitos 🛠️

* Python 3.x
* Django (A versão usada é a 5.2.5)
* PostgreSQL
* Biblioteca Python para PostgreSQL (ex: `psycopg2`)

---

### Instalação e Configuração 🚀

1.  **Clone o Repositório**:
    ```bash
    git clone [https://github.com/kemersonpassos/sistema_protocolos2-master-main.git]
    cd sistema_protocolos2-master
    ```

2.  **Crie e Ative um Ambiente Virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3.  **Instale as Dependências**:
    ```bash
    # Se você tiver um arquivo requirements.txt, use:
    # pip install -r requirements.txt
    # Caso contrário, instale manualmente:
    pip install Django psycopg2-binary
    ```

4.  **Configure o Banco de Dados**:
    Abra o arquivo `sistema_protocolos/settings.py` e configure as credenciais do seu banco de dados PostgreSQL. O projeto está configurado para o Supabase, mas você pode alterar para a sua configuração local.

5.  **Execute as Migrações do Banco de Dados**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Popule o Banco de Dados com Dados de Exemplo**:
    Você pode usar o comando personalizado para criar um superusuário e dados de teste.
    ```bash
    python manage.py seed_data
    ```
    Este comando criará um superusuário com as credenciais `admin/adminpassword` e alguns clientes e protocolos de exemplo.

---

### Como Executar o Projeto

Após a configuração, você pode iniciar o servidor de desenvolvimento do Django.

```bash
python manage.py runserver
