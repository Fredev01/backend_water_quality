from app.share.users.infra.users_repo_impl import UserRepositoryImpl
from app.share.users.domain.model.auth import UserRegister
from app.share.users.domain.enum.roles import Roles
import getpass


def main():
    print("Crear usuario administrador")
    username = input("Nombre de usuario: ")
    email = input("Email: ")
    phone = input("Teléfono: ")
    # Usar getpass para que la contraseña no sea visible al escribirla
    password = getpass.getpass("Contraseña: ")

    user_data = UserRegister(
        username=username,
        email=email,
        phone=phone,
        password=password,
    )

    repo = UserRepositoryImpl()
    user = repo.create_user(user_data, rol=Roles.ADMIN)
    print(f"Usuario administrador '{user.username}' creado exitosamente.")


if __name__ == "__main__":
    main()
