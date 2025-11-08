# Multicast + Concurrency Demo (UDP)

Este laboratorio implementa **multicast y concurrencia** usando Python.
Funciona en Linux/macOS/Windows y en redes virtuales como ZeroTier u Hamachi.

## 1) Requisitos
- Python 3.10 o superior.
- Estar en la misma red virtual (ZeroTier/Hamachi) con tus compañeros.
- Conocer la **IP de tu adaptador virtual** (por ejemplo, `25.x.x.x` en Hamachi o `10.x.x.x` en ZeroTier).
- Permitir UDP en firewall para el puerto elegido (por defecto `50000`).

## 2) Instalación
No requiere librerías externas. Solo clona/descarga esta carpeta.

## 3) Uso básico
En **cada máquina** (mínimo 2 máquinas) ejecuta:

```bash
python multicast_chat.py --iface <IP_DE_TU_ADAPTADOR> --name <TU_NOMBRE>
```

Ejemplo:
```bash
# IP del adaptador ZeroTier/Hamachi de tu equipo
python multicast_chat.py --iface 10.147.17.23 --name Franklin
```

Escribe un mensaje y presiona **ENTER** para enviarlo por multicast al grupo `239.255.0.1:50000`.
Cada nodo también envía **heartbeats** cada 5s.

### Parámetros útiles
- `--group 239.255.0.1` : grupo multicast (IPv4 administrativamente local).
- `--port 50000`        : puerto UDP.
- `--iface 10.x.x.x`    : **IP del adaptador virtual** para unirte/enviar por esa interfaz.
- `--name Franklin`     : nombre de tu nodo (por defecto el hostname).
- `--ttl 1`             : alcance de salto multicast (1 = solo LAN/SDN).
- `--workers 4`         : hilos concurrentes que procesan mensajes.
- `--no_heartbeat`      : desactiva heartbeats.

## 4) Pruebas sugeridas
1. Ejecuta el programa en **al menos 3 nodos** en la red virtual.
2. Envía mensajes desde cada nodo y verifica su recepción en los demás.
3. Cambia `--workers` a 1 y 8 para observar la **concurrencia** en el procesamiento.
4. Genera carga: pega varias líneas rápidamente o usa:
   ```bash
   yes "carga" | head -n 50 | python multicast_chat.py --iface <IP> --name Cargador
   ```
5. Interrumpe un nodo con `Ctrl+C` y vuelve a levantarlo para observar recuperación.

## 5) Capturas con Wireshark
- Filtro para ver el **join IGMP**: `igmp`
- Filtro para ver datos al grupo: `udp && ip.dst==239.255.0.1 && udp.port==50000`
- Muestra **cabeceras IP/UDP**, TTL, longitud y marca un paquete. Exporta una captura corta (PCAP) si lo piden.

## 6) Solución de problemas
- **No recibo nada**: revisa que todos usen el **mismo grupo/puerto** y que `--iface` sea la **IP del adaptador** virtual.
- **Firewall**: permite UDP/50000 en el SO.
- **TTL**: si haces routing entre subredes virtuales, aumenta `--ttl 2`.
- **Windows**: ejecuta PowerShell/CMD como usuario normal (no requiere admin).

---

© 2025
