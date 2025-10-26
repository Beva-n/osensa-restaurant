import mqtt from 'mqtt';

export async function connectMqtt() {

    const url = `ws://${location.hostname}:9001`;
    const client = mqtt.connect(url, { reconnectPeriod: 1000 });

    await new Promise<void>((resolve, reject) => {
        client.on('connect', () => resolve());
        client.on('error', (e) => reject(e));
    });

    return client;
}
