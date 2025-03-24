from socketio import AsyncServer, ASGIApp
from app.share.jwt.domain.payload import MeterPayload, UserPayload
from app.share.socketio.infra.session_repo_impl import SessionMeterSocketIORepositoryImpl, SessionUserSocketIORepositoryImpl

sio = AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = ASGIApp(sio)

# Receive


@sio.on("connect", namespace="/receive/")
async def receive_connection(sid, environ):
    print(f"📡 Nuevo conexión en receive: {sid}")
    token = environ.get("HTTP_ACCESS_TOKEN")

    # Guardar información del medidor
    SessionMeterSocketIORepositoryImpl.add(sid, MeterPayload(
        id_workspace="1",
        owner="correo",
        id_meter="1",
        exp=1232.0
    ))

    if not token:
        await sio.disconnect(sid, namespace="/receive/")
        print(f"📡 Desconexión: {sid}")
        return


@sio.on("message", namespace="/receive/")
async def receive_message(sid, data):

    # Obtener información del medidor
    payload = SessionMeterSocketIORepositoryImpl.get(sid)
    print(f"Payload del medidor: {payload}")

    # Enviar el mensaje al namespace subscribe, a la sala específica

    await sio.emit("message", data, namespace="/subscribe/", room=payload.owner)
    print(f"📤 Mensaje enviado a sala {payload.owner} en namespace /subscribe/")


@sio.on("disconnect", namespace="/receive/")
async def receive_disconnection(sid):
    print(f"📡 Desconexión de receive: {sid}")
    # Limpiar datos si es necesario


@sio.on("connect", namespace="/subscribe/")
async def subscribe_connection(sid, environ):
    print(f"📡 Nuevo conexión en subscribe: {sid}")
    token = environ.get("HTTP_ACCESS_TOKEN")

    # Guardar información del usuario
    user_payload = UserPayload(
        email="correo",
        exp=100.0,
        phone="123456789",
        rol="admin",
        username="admin"
    )

    SessionUserSocketIORepositoryImpl.add(sid, user_payload)

    if not token:
        await sio.disconnect(sid, namespace="/subscribe/")
        print(f"📡 Desconexión: {sid}")
        return

    # Crear la sala con el email del usuario
    await sio.enter_room(sid, user_payload.email, namespace="/subscribe/")
    print(
        f"🔗 Cliente {sid} unido a la sala {user_payload.email} en namespace /subscribe/")

    # Enviar confirmación al cliente
    await sio.emit("joined", {"room": user_payload.email}, room=sid, namespace="/subscribe/")


@sio.on("disconnect", namespace="/subscribe/")
async def subscribe_disconnection(sid):
    print(f"📡 Desconexión de subscribe: {sid}")
    SessionUserSocketIORepositoryImpl.delete(sid)
