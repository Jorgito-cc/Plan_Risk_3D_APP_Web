import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { Observable, Subject } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

/**
 * Interfaz para los mensajes de movimiento de piezas 3D.
 */
export interface PieceUpdate {
  accion: 'mover' | 'soltar' | 'usuario_unido' | 'usuario_salio';
  pieza_id?: string;
  posicion?: { x: number; y: number; z: number };
  user?: string;
  color?: string;
}

/**
 * Interfaz para la respuesta de crear sala.
 */
export interface SalaColaborativa {
  id: number;
  token: string;
  proyecto: number;
  creador: number | null;
  activa: boolean;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class CollaborationService {
  private http = inject(HttpClient);
  private API = environment.endpoint;

  /** WebSocket connection subject */
  private ws$: WebSocketSubject<PieceUpdate> | null = null;

  /** Observable público para escuchar mensajes entrantes del WebSocket */
  public messages$ = new Subject<PieceUpdate>();

  /** Señal reactiva: ¿estamos conectados a una sala? */
  public isConnected = signal<boolean>(false);

  /** Señal reactiva: token de la sala activa */
  public activeRoomToken = signal<string | null>(null);

  /** Señal reactiva: lista de usuarios conectados */
  public connectedUsers = signal<{ name: string; color: string }[]>([]);

  // ─── API HTTP ───

  /**
   * Crear una nueva sala colaborativa en el backend.
   */
  crearSala(proyectoId: number): Observable<SalaColaborativa> {
    return this.http.post<SalaColaborativa>(
      `${this.API}api/collaboration/crear-sala/`,
      { proyecto_id: proyectoId }
    );
  }

  /**
   * Enviar una invitación por correo electrónico.
   */
  enviarInvitacion(emailDestino: string, enlace: string, nombreProyecto: string): Observable<any> {
    return this.http.post(
      `${this.API}api/collaboration/enviar-invitacion/`,
      {
        email_destino: emailDestino,
        enlace: enlace,
        nombre_proyecto: nombreProyecto
      }
    );
  }

  /**
   * Obtener detalles de la sala (para colaboradores invitados).
   */
  obtenerSala(token: string): Observable<{token: string, proyecto_id: number, glb_model: string | null}> {
    return this.http.get<{token: string, proyecto_id: number, glb_model: string | null}>(
      `${this.API}api/collaboration/sala/${token}/`
    );
  }

  /**
   * Enviar un archivo modelo .glb por correo.
   */
  enviarModeloGLB(emailDestino: string, file: File, nombreProyecto: string): Observable<any> {
    const formData = new FormData();
    formData.append('email_destino', emailDestino);
    formData.append('archivo_glb', file);
    formData.append('nombre_proyecto', nombreProyecto);

    return this.http.post(`${this.API}api/collaboration/enviar-glb/`, formData);
  }

  /**
   * Cerrar una sala colaborativa.
   */
  cerrarSala(token: string): Observable<any> {
    return this.http.post(
      `${this.API}api/collaboration/cerrar-sala/`,
      { token }
    );
  }

  // ─── WebSocket ───

  /**
   * Conectarse a una sala de colaboración vía WebSocket.
   * @param roomToken - UUID de la sala
   * @param userName - Nombre del usuario actual
   * @param userColor - Color asignado al usuario
   */
  connect(roomToken: string, userName: string, userColor: string): void {
    if (this.ws$) {
      this.disconnect();
    }

    // Construir URL del WebSocket (ws:// en dev, wss:// en producción)
    const wsProtocol = this.API.startsWith('https') ? 'wss' : 'ws';
    const wsHost = this.API.replace(/^https?:\/\//, '').replace(/\/$/, '');
    const wsUrl = `${wsProtocol}://${wsHost}/ws/editor/${roomToken}/?user=${encodeURIComponent(userName)}&color=${encodeURIComponent(userColor)}`;

    console.log('🔌 Conectando WebSocket a:', wsUrl);

    this.ws$ = webSocket<PieceUpdate>({
      url: wsUrl,
      openObserver: {
        next: () => {
          console.log('✅ WebSocket conectado a sala:', roomToken);
          this.isConnected.set(true);
          this.activeRoomToken.set(roomToken);
        }
      },
      closeObserver: {
        next: () => {
          console.log('🔌 WebSocket desconectado');
          this.isConnected.set(false);
          this.activeRoomToken.set(null);
          this.connectedUsers.set([]);
        }
      }
    });

    this.ws$.subscribe({
      next: (msg: PieceUpdate) => {
        // Gestionar lista de usuarios conectados
        if (msg.accion === 'usuario_unido' && msg.user && msg.color) {
          const users = this.connectedUsers();
          if (!users.find(u => u.name === msg.user)) {
            this.connectedUsers.set([...users, { name: msg.user!, color: msg.color! }]);
          }
        } else if (msg.accion === 'usuario_salio' && msg.user) {
          this.connectedUsers.set(
            this.connectedUsers().filter(u => u.name !== msg.user)
          );
        }

        // Emitir el mensaje a todos los suscriptores
        this.messages$.next(msg);
      },
      error: (err) => {
        console.error('❌ Error WebSocket:', err);
        this.isConnected.set(false);
      }
    });
  }

  /**
   * Enviar un mensaje de movimiento de pieza al WebSocket.
   */
  sendPieceUpdate(piezaId: string, posicion: { x: number; y: number; z: number }, accion: 'mover' | 'soltar' = 'mover'): void {
    if (this.ws$ && this.isConnected()) {
      this.ws$.next({
        accion,
        pieza_id: piezaId,
        posicion
      });
    }
  }

  /**
   * Desconectarse de la sala.
   */
  disconnect(): void {
    if (this.ws$) {
      this.ws$.complete();
      this.ws$ = null;
    }
    this.isConnected.set(false);
    this.activeRoomToken.set(null);
    this.connectedUsers.set([]);
  }
}
