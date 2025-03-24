from socketio import AsyncServer, ASGIApp

sio = AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = ASGIApp(sio)


# Receive

@sio.on("connect", namespace="/receive/")
async def receive_connection(sid, environ):

    print(f"📡 Nuevo conexión: {sid}")
    token = environ.get("HTTP_ACCESS_TOKEN")

    if not token:
        await sio.disconnect(sid, namespace="/receive/")
        print(f"📡 Desconexión: {sid}")
        return


@sio.on("message", namespace="/receive/")
async def receive_message(sid, data):
    print(f"📩 Mensaje recibido en namespace {sid}: {data}")

    # Process los datos

    # Recibe el token de la cabecera

    await sio.emit("message", data, namespace="/subscribe/")


@sio.on("disconnect", namespace="/receive/")
async def receive_disconnection(sid):
    print(f"📡 Desconexión: {sid}")


# Subscribe
@sio.on("connect", namespace="/subscribe/")
async def subscribe_connection(sid, environ):
    print(f"📡 Nuevo conexión: {sid}")
    token = environ.get("HTTP_ACCESS_TOKEN")
    print(token)
    if not token:
        await sio.disconnect(sid, namespace="/subscribe/")
        print(f"📡 Desconexión: {sid}")
        return


@sio.on("message", namespace="/subscribe/")
async def subscribe_message(sid, data):
    await sio.send(data)
