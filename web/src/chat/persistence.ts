const STORAGE_KEY = 'bough:local-config';

export interface LocalConfig {
    presetId: string | null;      // Generation preset pointer
    promptId: string | null;      // System prompt pointer
    conversationId: string | null;
}

const DEFAULTS: LocalConfig = { presetId: null, promptId: null, conversationId: null };

export function loadLocalConfig(): LocalConfig {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return { ...DEFAULTS };
        const parsed: unknown = JSON.parse(raw);
        if (typeof parsed !== 'object' || parsed === null) return { ...DEFAULTS };
        const p = parsed as Record<string, unknown>;
        return {
            presetId: typeof p.presetId === 'string' ? p.presetId : null,
            promptId: typeof p.promptId === 'string' ? p.promptId : null,
            conversationId: typeof p.conversationId === 'string' ? p.conversationId : null,
        };
    } catch {
        return { ...DEFAULTS };
    }
}

export function updateLocalConfig(patch: Partial<LocalConfig>): void {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        let current: Record<string, unknown> = {};
        if (raw) {
            try {
                const parsed: unknown = JSON.parse(raw);
                if (typeof parsed === 'object' && parsed !== null) {
                    current = parsed as Record<string, unknown>;
                }
            } catch {
                // Corrupt blob: rebuild from scratch
            }
        }
        current.version = 1;
        Object.assign(current, patch);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
    } catch {
        // Storage unavailable/full: live without persistence, by design.
    }
}