# Documentação da API - Rotas de Autenticação (`routes/auth.py`)

Este documento descreve os endpoints da API relacionados à autenticação definidos em `routes/auth.py`.

---

## 1. Login

- **Endpoint:** `/login`
- **Métodos:** `GET`, `POST`
- **Descrição:** Realiza o login de um usuário.
- **Corpo da Requisição (POST):**
  - `email` (String, obrigatório): Endereço de email do usuário.
  - `password` (String, obrigatório): Senha do usuário.
  - `remember_me` (Boolean, opcional): Se deve lembrar a sessão de login.
- **Resposta (POST - Sucesso):**
  - Redireciona para o painel para admins e gerentes, ou para a página de rotas para vendedores.
- **Resposta (POST - Falha):**
  - Renderiza a página de login (`auth/login.html`) com uma mensagem de erro se o login falhar (email ou senha inválidos).
- **Template:** `auth/login.html`

---

## 2. Registro (Registro de Admin)

- **Endpoint:** `/register`
- **Métodos:** `GET`, `POST`
- **Descrição:** Registra um novo usuário admin e empresa.
- **Corpo da Requisição (POST):**
  - `company_name` (String, obrigatório): Nome da empresa.
  - `cnpj` (String, obrigatório): CNPJ da empresa.
  - `username` (String, obrigatório): Nome de usuário do admin.
  - `email` (String, obrigatório): Endereço de email do admin.
  - `password` (String, obrigatório): Senha do admin.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de login (`auth.login`) após registro bem-sucedido.
- **Resposta (POST - Falha):**
  - Renderiza a página de registro (`auth/register.html`) com uma mensagem de erro se o registro falhar (ex: email já registrado, CNPJ já possui um admin).
- **Template:** `auth/register.html`

---

## 3. Logout

- **Endpoint:** `/logout`
- **Métodos:** `GET`
- **Descrição:** Realiza o logout do usuário atualmente logado.
- **Autenticação Necessária:** Sim (`@login_required`)
- **Resposta (GET - Sucesso):**
  - Redireciona para a página de login (`auth.login`) após o logout.
  - Exibe uma mensagem de sucesso ("Você saiu do sistema").

---

## 4. Perfil

- **Endpoint:** `/profile`
- **Métodos:** `GET`, `POST`
- **Descrição:** Exibe e atualiza as informações do perfil do usuário.
- **Autenticação Necessária:** Sim (`@login_required`)
- **Corpo da Requisição (POST):**
  - `username` (String, obrigatório): Novo nome de usuário.
  - `email` (String, obrigatório): Novo endereço de email.
  - `current_password` (String, opcional): Senha atual (necessária se estiver alterando a senha).
  - `new_password` (String, opcional): Nova senha.
- **Resposta (GET):**
  - Renderiza a página de perfil (`auth/profile.html`) com as informações atuais do perfil do usuário.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de perfil (`auth.profile`) após atualização bem-sucedida.
  - Exibe uma mensagem de sucesso ("Perfil atualizado com sucesso!").
- **Resposta (POST - Falha):**
  - Renderiza a página de perfil (`auth/profile.html`) com uma mensagem de erro se a atualização falhar (ex: senha atual incorreta, email já em uso).
- **Template:** `auth/profile.html`

---

## 5. Criar Usuário (Admin/Gerente)

- **Endpoint:** `/users/create`
- **Métodos:** `GET`, `POST`
- **Descrição:** Cria um novo usuário (vendedor ou gerente) por um admin ou gerente.
- **Autenticação Necessária:** Sim (`@login_required`)
- **Permissões:** Acessível apenas para admins e gerentes. Gerentes só podem criar vendedores.
- **Corpo da Requisição (POST):**
  - `username` (String, obrigatório): Nome de usuário do novo usuário.
  - `email` (String, obrigatório): Endereço de email do novo usuário.
  - `password` (String, obrigatório): Senha do novo usuário.
  - `role` (String, obrigatório): Função do usuário (`'seller'` ou `'manager'`, admin pode escolher, gerente é fixo em `'seller'`).
- **Resposta (GET):**
  - Renderiza a página de criação de usuário (`auth/create_user.html`) com o formulário de criação.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de gerenciamento de usuários (`main.manage_users`) após criação bem-sucedida.
  - Exibe uma mensagem de sucesso (ex: "Usuário {new_user.username} criado com sucesso!").
- **Resposta (POST - Falha):**
  - Renderiza a página de criação de usuário (`auth/create_user.html`) com uma mensagem de erro se a criação falhar (ex: email já registrado, nome de usuário já em uso).
- **Template:** `auth/create_user.html`

---

## 6. Atribuir Gerentes ao Vendedor (Admin)

- **Endpoint:** `/users/assign/managers/<int:seller_id>`
- **Métodos:** `GET`, `POST`
- **Descrição:** Atribui gerentes a um vendedor (relacionamento muitos-para-muitos).
- **Autenticação Necessária:** Sim (`@login_required`)
- **Permissões:** Acessível apenas para admins.
- **Parâmetros de URL:**
  - `seller_id` (Inteiro, obrigatório): ID do vendedor para atribuir gerentes.
- **Corpo da Requisição (POST):**
  - `users` (Lista de Inteiros, opcional): Lista de IDs dos gerentes para atribuir ao vendedor.
- **Resposta (GET):**
  - Renderiza a página de atribuição de usuários (`auth/assign_users.html`) com uma lista de gerentes para escolher. Pré-seleciona gerentes atualmente atribuídos.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de gerenciamento de usuários (`main.manage_users`) após atribuição bem-sucedida.
  - Exibe uma mensagem de sucesso (ex: "Gerentes atribuídos ao vendedor {seller.username} com sucesso!").
- **Resposta (POST - Falha):**
  - Renderiza a página de atribuição de usuários (`auth/assign_users.html`) com uma mensagem de erro se a atribuição falhar.
- **Template:** `auth/assign_users.html`
- **Variável de Título:** `title=f'Atribuir Gerentes ao Vendedor: {seller.username}'`
- **Variável de Usuário:** `user=seller` (objeto do vendedor)

---

## 7. Atribuir Vendedores ao Gerente (Admin)

- **Endpoint:** `/users/assign/sellers/<int:manager_id>`
- **Métodos:** `GET`, `POST`
- **Descrição:** Atribui vendedores a um gerente (relacionamento muitos-para-muitos).
- **Autenticação Necessária:** Sim (`@login_required`)
- **Permissões:** Acessível apenas para admins.
- **Parâmetros de URL:**
  - `manager_id` (Inteiro, obrigatório): ID do gerente para atribuir vendedores.
- **Corpo da Requisição (POST):**
  - `users` (Lista de Inteiros, opcional): Lista de IDs dos vendedores para atribuir ao gerente.
- **Resposta (GET):**
  - Renderiza a página de atribuição de usuários (`auth/assign_users.html`) com uma lista de vendedores para escolher. Pré-seleciona vendedores atualmente atribuídos.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de gerenciamento de usuários (`main.manage_users`) após atribuição bem-sucedida.
  - Exibe uma mensagem de sucesso (ex: "Vendedores atribuídos ao gerente {manager.username} com sucesso!").
- **Resposta (POST - Falha):**
  - Renderiza a página de atribuição de usuários (`auth/assign_users.html`) com uma mensagem de erro se a atribuição falhar.
- **Template:** `auth/assign_users.html`
- **Variável de Título:** `title=f'Atribuir Vendedores ao Gerente: {manager.username}'`
- **Variável de Usuário:** `user=manager` (objeto do gerente)

---

## 8. Desatribuir Gerente do Vendedor (Admin)

- **Endpoint:** `/unassign_manager/<int:seller_id>`
- **Métodos:** `POST`
- **Descrição:** Remove a atribuição de um gerente de um vendedor.
- **Autenticação Necessária:** Sim (`@login_required`)
- **Permissões:** Acessível apenas para admins.
- **Parâmetros de URL:**
  - `seller_id` (Inteiro, obrigatório): ID do vendedor para remover atribuição do gerente.
- **Corpo da Requisição (POST):**
  - `manager_id` (Inteiro, obrigatório): ID do gerente para desatribuir.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de atribuição de gerentes ao vendedor (`auth.assign_managers_to_seller`) após remoção bem-sucedida.
  - Exibe uma mensagem de sucesso (ex: "Gerente {manager.display_name} desvinculado do vendedor {seller.display_name}.").
- **Resposta (POST - Falha):**
  - Redireciona para a página de atribuição de gerentes ao vendedor (`auth.assign_managers_to_seller`) com uma mensagem de erro se a remoção falhar (ex: gerente não especificado, sem permissão).

---

## 9. Excluir Usuário (Admin/Gerente)

- **Endpoint:** `/delete_user/<int:user_id>`
- **Métodos:** `POST`
- **Descrição:** Exclui uma conta de usuário (vendedor ou gerente). Admins podem excluir qualquer vendedor ou gerente. Gerentes só podem excluir vendedores que gerenciam.
- **Autenticação Necessária:** Sim (`@login_required`)
- **Permissões:** Acessível para admins e gerentes (com restrições).
- **Parâmetros de URL:**
  - `user_id` (Inteiro, obrigatório): ID do usuário a ser excluído.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página inicial (`main.index`) após exclusão bem-sucedida.
  - Exibe uma mensagem de sucesso (ex: "Conta de {user_to_delete.display_name} excluída com sucesso.").
- **Resposta (POST - Falha):**
  - Redireciona para a página inicial (`main.index`) com uma mensagem de erro se a exclusão falhar (ex: sem permissão, tentando excluir admin, tentando excluir a si mesmo).

---

## 10. Desatribuir Vendedor do Gerente (Admin)

- **Endpoint:** `/unassign_seller/<int:manager_id>`
- **Métodos:** `POST`
- **Descrição:** Remove a atribuição de um vendedor de um gerente.
- **Autenticação Necessária:** Sim (`@login_required`)
- **Permissões:** Acessível apenas para admins.
- **Parâmetros de URL:**
  - `manager_id` (Inteiro, obrigatório): ID do gerente para remover atribuição do vendedor.
- **Corpo da Requisição (POST):**
  - `seller_id` (Inteiro, obrigatório): ID do vendedor para desatribuir.
- **Resposta (POST - Sucesso):**
  - Redireciona para a página de atribuição de vendedores ao gerente (`auth.assign_sellers_to_manager`) após remoção bem-sucedida.
  - Exibe uma mensagem de sucesso (ex: "Vendedor {seller.display_name} desvinculado do gerente {manager.display_name}.").
- **Resposta (POST - Falha):**
  - Redireciona para a página de atribuição de vendedores ao gerente (`auth.assign_sellers_to_manager`) com uma mensagem de erro se a remoção falhar (ex: vendedor nWão especificado, sem permissão).

---

**Nota:** Esta documentação é baseada nas rotas definidas em `routes/auth.py`. Ela fornece detalhes sobre cada endpoint, seus métodos, descrições, parâmetros e respostas.
