import { writable } from 'svelte/store';

export type PrepItem = { name: string; id: string };
export type TableState = { ready: string[]; preparing: PrepItem[] };

export const tables = writable<Record<number, TableState>>({
    1: { ready: [], preparing: [] },
    2: { ready: [], preparing: [] },
    3: { ready: [], preparing: [] },
    4: { ready: [], preparing: [] },
});
