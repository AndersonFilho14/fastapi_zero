import random
import string

from locust import HttpUser, SequentialTaskSet, between, task


def random_suffix(n: int = 8) -> str:
    """Gera um sufixo aleatório para evitar colisão de e-mails/usernames."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class ToDoUserFlow(SequentialTaskSet):
    """
    Simula o ciclo de vida completo de um usuário:
      1. Registra uma conta nova
      2. Faz login e obtém o token JWT
      3. Cria algumas tarefas
      4. Lista as tarefas
      5. Atualiza uma tarefa
      6. Deleta uma tarefa
    """

    token: str | None = None
    created_todo_ids: list[int]

    def on_start(self):
        """Executado uma vez quando o usuário virtual começa."""
        self.created_todo_ids = []
        suffix = random_suffix()
        self.email = f"user_{suffix}@example.com"
        self.password = "Senha@123"
        self.username = f"locust_{suffix}"

        # 1. Registra o usuário
        with self.client.post(
            "/users/",
            json={
                "username": self.username,
                "email": self.email,
                "password": self.password,
            },
            catch_response=True,
            name="[setup] POST /users/ - registrar",
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"Falha ao registrar usuário: {resp.status_code} {resp.text}")
                return

        # 2. Faz login
        with self.client.post(
            "/auth/token",
            data={"username": self.email, "password": self.password},
            catch_response=True,
            name="[setup] POST /auth/token - login",
        ) as resp:
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
            else:
                resp.failure(f"Falha no login: {resp.status_code} {resp.text}")


    @task
    def criar_tarefa(self):
        """Cria uma nova tarefa ToDo."""
        if not self.token:
            return

        payload = {
            "title": f"Tarefa {random_suffix(4)}",
            "description": "Descrição gerada pelo Locust para teste de carga",
            "state": "todo",
        }

        with self.client.post(
            "/to_dos/",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="POST /to_dos/ - criar tarefa",
        ) as resp:
            if resp.status_code == 200:
                todo_id = resp.json().get("id")
                if todo_id:
                    self.created_todo_ids.append(todo_id)
            else:
                resp.failure(f"Falha ao criar tarefa: {resp.status_code} {resp.text}")

    @task
    def listar_tarefas(self):
        """Lista as tarefas do usuário autenticado."""
        if not self.token:
            return

        self.client.get(
            "/to_dos/",
            headers={"Authorization": f"Bearer {self.token}"},
            name="GET /to_dos/ - listar tarefas",
        )

    @task
    def atualizar_tarefa(self):
        """Atualiza o estado de uma tarefa existente."""
        if not self.token or not self.created_todo_ids:
            return

        todo_id = random.choice(self.created_todo_ids)
        new_state = random.choice(["todo", "doing", "done"])

        with self.client.patch(
            f"/to_dos/{todo_id}",
            json={"state": new_state},
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="PATCH /to_dos/{id} - atualizar tarefa",
        ) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Falha ao atualizar tarefa: {resp.status_code} {resp.text}")

    @task
    def deletar_tarefa(self):
        """Deleta uma tarefa existente."""
        if not self.token or not self.created_todo_ids:
            return

        todo_id = self.created_todo_ids.pop()

        with self.client.delete(
            f"/to_dos/{todo_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="DELETE /to_dos/{id} - deletar tarefa",
        ) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Falha ao deletar tarefa: {resp.status_code} {resp.text}")

    @task
    def health_check(self):
        """Verifica o endpoint de saúde da API."""
        self.client.get("/health", name="GET /health - health check")


class UsuarioLocust(HttpUser):
    """
    Usuário virtual que simula o fluxo completo da aplicação.
    O tempo de espera entre as tarefas é entre 1 e 3 segundos,
    simulando um usuário humano real.
    """

    tasks = [ToDoUserFlow]
    wait_time = between(0,0)

