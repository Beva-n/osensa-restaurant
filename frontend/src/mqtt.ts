// frontend/src/lib/mqtt.ts
import mqtt from "mqtt";
import type { MqttClient, IClientOptions } from "mqtt";

/**
 * Vite envs (browser-exposed):
 *  - VITE_MQTT_URL: ws://localhost:9001 (dev) OR wss://<cluster>:8884/mqtt (prod)
 *  - VITE_MQTT_USERNAME / VITE_MQTT_PASSWORD: optional (managed broker)
 *  - VITE_MQTT_PATH: optional, usually /mqtt if not already in URL
 */
const URL  = import.meta.env.VITE_MQTT_URL as string | undefined;
const USER = import.meta.env.VITE_MQTT_USERNAME as string | undefined;
const PASS = import.meta.env.VITE_MQTT_PASSWORD as string | undefined;
const PATH = import.meta.env.VITE_MQTT_PATH as string | undefined;

function getUrl(): string {
    if (URL && URL.trim()) return URL;
    const host = (typeof location !== "undefined" && location.hostname) || "localhost";
    return `ws://${host}:9001`;
}

function buildOptions(): IClientOptions {
    const url = getUrl();
    const isSecure = url.startsWith("wss://");

    const opts: IClientOptions = {
        keepalive: 30,
        reconnectPeriod: 2000,
        connectTimeout: 10_000,
        clean: true,
        protocol: isSecure ? "wss" : "ws",
        rejectUnauthorized: true, // verify TLS when using WSS
    };

    if (PATH) (opts as any).path = PATH; // mqtt.js accepts `path` for ws/wss
    if (USER) opts.username = USER;
    if (PASS) opts.password = PASS;

    return opts;
}

export async function connectMqtt(): Promise<MqttClient> {
    const client = mqtt.connect(getUrl(), buildOptions());

    await new Promise<void>((resolve, reject) => {
        const t = setTimeout(() => reject(new Error("MQTT connect timeout")), 15000);
        client.once("connect", () => { clearTimeout(t); resolve(); });
        client.once("error",  (e) => { clearTimeout(t); reject(e); });
    });

    client.on("reconnect", () => console.info("[MQTT] reconnecting…"));
    client.on("close",     () => console.info("[MQTT] closed"));
    client.on("error",     (e) => console.error("[MQTT] error", e));

    return client;
}
