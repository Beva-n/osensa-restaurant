export const newId = () =>
    (crypto as any).randomUUID?.() || Math.random().toString(36).slice(2);

export const short = (s: string) => s.slice(0, 8);
