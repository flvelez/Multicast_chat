# Implementación de Multicast y Concurrencia en Sistemas Distribuidos

> **Autor:** (tu nombre)  
> **Curso:** (nombre del curso)  
> **Fecha:** (aaaa-mm-dd)  
> **Red virtual usada:** (ZeroTier/Hamachi, ID/red)  
> **Grupo/puerto:** 239.255.0.1:50000

## 1. Introducción
Breve contexto de multicast y concurrencia. Propósito del laboratorio.

## 2. Descripción general del proyecto
Qué hace el programa (chat/heartbeat), arquitectura de alto nivel y nodos.

## 3. Objetivos de la tarea
- Implementar envío/recepción multicast entre múltiples nodos.
- Manejar concurrencia en el procesamiento de mensajes.
- Verificar en una red virtual y capturar tráfico con Wireshark.

## 4. Desarrollo
### 4.1 Implementación
- Lenguaje y versión usados (Python 3.10+).
- Módulos estándar (socket, struct, threading, queue).

### 4.2 Manejo de multicast
- `IP_ADD_MEMBERSHIP`, `IP_MULTICAST_IF`, `IP_MULTICAST_TTL`.
- Grupo administrativo local `239.255.0.0/16` (elegido: 239.255.0.1).

### 4.3 Concurrencia
- Hilos de **recepción** y **procesamiento** (pool `--workers`).
- Heartbeat periódico en hilo dedicado.

### 4.4 Configuración de la red virtual
- (Pantallazo) unión a la red en ZeroTier/Hamachi, IP asignada.
- Tabla con IP y nombre de cada nodo participante.

## 5. Pruebas y Resultados
### 5.1 Pruebas de conectividad
- Topología (n nodos). Casos de envío desde cada nodo.
- Métricas simples: mensajes enviados/recibidos, pérdida (si hubo).

### 5.2 Capturas Wireshark
Incluye imágenes donde se vean:
- Paquetes **IGMP** al unirse al grupo.
- Tráfico **UDP** al destino 239.255.0.1:50000.  
Filtro: `udp && ip.dst==239.255.0.1 && udp.port==50000`.

### 5.3 Observaciones de concurrencia
- Efecto de variar `--workers` y ráfagas de mensajes.
- Captura de consola donde se ve procesamiento concurrente (timestamps).

## 6. Conclusiones
Hallazgos principales y reflexión sobre multicast + concurrencia en redes virtuales.

## 7. Desafíos y soluciones
Problemas encontrados (firewall, TTL, interfaz) y cómo se resolvieron.

## 8. Bibliografía (formato APA)
- Libros/recursos de sistemas distribuidos utilizados.
- Documentación de Python `socket` y artículos sobre IPv4 multicast.
