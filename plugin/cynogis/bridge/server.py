"""Serveur TCP local (127.0.0.1). Les signaux Qt sont traités dans la boucle d'événements de
QGIS : chaque requête s'exécute sur le THREAD PRINCIPAL."""
from __future__ import annotations

import hmac
import logging

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer, QTcpSocket

from ..core.dispatcher import Dispatcher
from ..core.errors import ErrorCode, ToolError
from .protocol import MAX_MESSAGE_BYTES, Response, decode_request

HOST = "127.0.0.1"
logger = logging.getLogger("cynogis.bridge")

class BridgeServer(QObject):
    def __init__(self, dispatcher: Dispatcher, token: str, parent: QObject | None = None):
        super().__init__(parent)
        self._dispatcher = dispatcher
        self._token = token.encode()
        self._server = QTcpServer(self)
        self._server.newConnection.connect(self._on_new_connection)
        self._buffers: dict[QTcpSocket, bytearray] = {}

    @property
    def port(self) -> int:
        return int(self._server.serverPort())

    def start(self, port: int = 0) -> None:
        """port=0 : le système choisit un port libre (communiqué via le fichier de connexion)."""
        if not self._server.listen(QHostAddress(HOST), port):
            raise RuntimeError(f"écoute impossible sur {HOST}:{port}({self._server.errorString()})")
        logger.info("Pont en écoute sur %s:%d", HOST, self.port)

    def stop(self) -> None:
        for sock in list(self._buffers):
            sock.abort()
            sock.deleteLater()
        self._buffers.clear()
        self._server.close()

    # --- Connexions ----------------------------------------------------------------------
    def _on_new_connection(self) -> None:
        while self._server.hasPendingConnections():
            sock = self._server.nextPendingConnection()
            if sock is None:
                break
            self._buffers[sock] = bytearray()
            sock.readyRead.connect(lambda s=sock: self._on_ready_read(s))
            sock.disconnected.connect(lambda s=sock: self._on_disconnected(s))

    def _on_disconnected(self, sock: QTcpSocket) -> None:
        self._buffers.pop(sock, None)
        sock.deleteLater()

    def _on_ready_read(self, sock: QTcpSocket) -> None:
        buf = self._buffers.get(sock)
        if buf is None:
            return
        buf.extend(bytes(sock.readAll()))
        while (idx := buf.find(b"\n")) >= 0:
            line = bytes(buf[:idx])
            del buf[: idx + 1]
            if line.strip():
                self._send(sock, self._handle_line(line))
        if len(buf) > MAX_MESSAGE_BYTES:
            err = ToolError(ErrorCode.PROTOCOL_ERROR, "Message trop volumineux.")
            self._send(sock, Response.failure(None, err))
            sock.disconnectFromHost()

    # --- Traitement ----------------------------------------------------------------------
    def _handle_line(self, line: bytes) -> Response:
        try:
            request = decode_request(line)
        except ToolError as err:
            return Response.failure(None, err)
        if not hmac.compare_digest(request.token.encode(), self._token):
            logger.warning("Requête refusée : jeton invalide")
            return Response.failure(request.id,
                                    ToolError(ErrorCode.UNAUTHORIZED, "Jeton invalide."))
        logger.debug("→ %s", request.method)
        return self._dispatcher.dispatch(request)

    @staticmethod
    def _send(sock: QTcpSocket, response: Response) -> None:
        if sock.state() == QAbstractSocket.SocketState.ConnectedState:
            sock.write(response.encode())
