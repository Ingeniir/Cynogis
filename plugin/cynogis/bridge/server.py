"""Serveur TCP local (127.0.0.1). Les signaux Qt sont traités dans la boucle d'événements de
QGIS : chaque requête s'exécute sur le THREAD PRINCIPAL."""
from __future__ import annotations

import hmac
import logging

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer, QTcpSocket

from ..core.cleanup import CleanupStep, run_cleanup_steps
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
        self._stopping = False

    @property
    def port(self) -> int:
        return int(self._server.serverPort())

    def start(self, port: int = 0) -> None:
        """Démarre une nouvelle instance du pont."""
        if self._stopping:
            raise RuntimeError(
                "Impossible de redémarrer une instance du pont déjà arrêtée "
                "ou en cours d'arrêt."
            )

        if not self._server.listen(QHostAddress(HOST), port):
            raise RuntimeError(
                f"Écoute impossible sur {HOST}:{port} "
                f"({self._server.errorString()})"
            )

        logger.info("Pont en écoute sur %s:%d", HOST, self.port)

    def stop(self) -> None:
        """Interdit les nouvelles requêtes et tente toutes les fermetures.

        Les sockets dont le nettoyage échoue restent référencées pour
        permettre une nouvelle tentative.
        """
        self._stopping = True

        def stop_socket(sock: QTcpSocket) -> None:
            sock.abort()
            sock.deleteLater()
            self._buffers.pop(sock, None)

        steps: list[CleanupStep] = [
            ("fermeture du serveur d'écoute", self._server.close),
        ]

        for index, sock in enumerate(list(self._buffers), start=1):
            steps.append((
                f"fermeture de la connexion {index}",
                lambda sock=sock: stop_socket(sock),
            ))

        failures = run_cleanup_steps(steps)

        if failures:
            labels = ", ".join(label for label, _error in failures)
            raise RuntimeError(
                f"Arrêt réseau du pont incomplet : {labels}"
            ) from failures[0][1]

    # --- Connexions ----------------------------------------------------------------------
    def _on_new_connection(self) -> None:
        if self._stopping:
            return

        while self._server.hasPendingConnections():
            sock = self._server.nextPendingConnection()
            if sock is None:
                break
            self._buffers[sock] = bytearray()
            sock.readyRead.connect(lambda s=sock: self._on_ready_read(s))
            sock.disconnected.connect(lambda s=sock: self._on_disconnected(s))

    def _on_disconnected(self, sock: QTcpSocket) -> None:
        if self._stopping:
            return

        self._buffers.pop(sock, None)
        sock.deleteLater()

    def _on_ready_read(self, sock: QTcpSocket) -> None:
        if self._stopping:
            return

        buf = self._buffers.get(sock)
        if buf is None:
            return

        buf.extend(bytes(sock.readAll()))

        while (idx := buf.find(b"\n")) >= 0:
            if self._stopping:
                return

            line = bytes(buf[:idx])
            del buf[: idx + 1]

            if line.strip():
                response = self._handle_line(line)

                if self._stopping:
                    return

                self._send(sock, response)

        if len(buf) > MAX_MESSAGE_BYTES:
            err = ToolError(
                ErrorCode.PROTOCOL_ERROR,
                "Message trop volumineux.",
            )
            self._send(sock, Response.failure(None, err))
            self._buffers.pop(sock, None)
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

        if self._stopping:
            return Response.failure(
                request.id,
                ToolError(
                    ErrorCode.BUSY,
                    "Le pont Cynogis est en cours d'arrêt."
                )
            )

        logger.debug("→ %s", request.method)
        return self._dispatcher.dispatch(request)

    @staticmethod
    def _send(sock: QTcpSocket, response: Response) -> None:
        if sock.state() == QAbstractSocket.SocketState.ConnectedState:
            sock.write(response.encode())
