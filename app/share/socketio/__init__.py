from socketio import AsyncServer, ASGIApp
from app.share.jwt.domain.payload import MeterPayload, UserPayload
from app.share.jwt.infrastructure.access_token import AccessToken
from app.share.socketio.domain.model import RecordBody
from app.share.socketio.infra.session_repo_impl import SessionMeterSocketIORepositoryImpl, SessionUserSocketIORepositoryImpl
from jwt.exceptions import DecodeError, InvalidTokenError, ExpiredSignatureError

sio = AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = ASGIApp(sio)

access_token_connection = AccessToken[MeterPayload]()
access_token_user = AccessToken[UserPayload]()


# Receive


@sio.on("connect", namespace="/receive/")
async def receive_connection(sid, environ):
    try:
        print(f"📡 Nuevo conexión en receive: {sid}")

        token = environ.get("HTTP_ACCESS_TOKEN")

        decoded_token = access_token_connection.validate(token)

        # Guardar información del medidor
        SessionMeterSocketIORepositoryImpl.add(
            sid, MeterPayload(**decoded_token))
    except Exception as e:
        print(e)
        await sio.disconnect(sid, namespace="/receive/")
        print(f"📡 Desconexión: {sid}")
        return


@sio.on("message", namespace="/receive/")
async def receive_message(sid, data: RecordBody):

    # Obtener información del medidor
    payload = SessionMeterSocketIORepositoryImpl.get(sid)
    print(f"Payload del medidor: {payload}")

    # Enviar el mensaje al namespace subscribe, a la sala específica
    print(data)
    await sio.emit("message", data, namespace="/subscribe/", room=payload.owner)
    print(f"📤 Mensaje enviado a sala {payload.owner} en namespace /subscribe/")


@sio.on("disconnect", namespace="/receive/")
async def receive_disconnection(sid):
    print(f"📡 Desconexión de receive: {sid}")
    SessionMeterSocketIORepositoryImpl.delete(sid)


@sio.on("connect", namespace="/subscribe/")
async def subscribe_connection(sid, environ):

    try:
        print(f"📡 Nuevo conexión en subscribe: {sid}")
        token = environ.get("HTTP_ACCESS_TOKEN")
        print(token)

        decoded_token = access_token_user.validate(token)
        print(decoded_token)
        user_payload = UserPayload(**decoded_token)

        SessionUserSocketIORepositoryImpl.add(
            sid, user_payload)

        # Crear la sala con el email del usuario
        await sio.enter_room(sid, user_payload.email, namespace="/subscribe/")
        print(
            f"🔗 Cliente {sid} unido a la sala {user_payload.email} en namespace /subscribe/")

        # Enviar confirmación al cliente
        await sio.emit("joined", {"room": user_payload.email}, room=sid, namespace="/subscribe/")

    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        await sio.disconnect(sid, namespace="/subscribe/")
        print(f"📡 Desconexión: {sid}")
        return


@sio.on("disconnect", namespace="/subscribe/")
async def subscribe_disconnection(sid):
    print(f"📡 Desconexión de subscribe: {sid}")
    try:
        SessionUserSocketIORepositoryImpl.delete(sid)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)
