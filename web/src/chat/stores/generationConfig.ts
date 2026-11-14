import { defineStore } from 'pinia';
import { ref, watch, nextTick } from 'vue';
import { CustomParam, GenerationPayload, GenerationPreset } from '@/types';
import { updateLocalConfig } from '../persistence';

export const useGenerationConfigStore = defineStore('generationConfig', () => {
    // Module-level singleton state (in-memory only for now)
    const model = ref('');
    const reasoningEffort = ref<'none' | 'minimal' | 'low' | 'medium' | 'high' | 'xhigh' | 'max' | null>(null);
    const customParams = ref<CustomParam[]>([]);

   // Preset State Management
    const loadedPresetId = ref<string>('default');
    const isDirty = ref(false);
    let isLoadingPreset = false;

    // Watch for manual changes to mark state as "dirty"
    watch([model, reasoningEffort, customParams], () => {
        if (!isLoadingPreset) {
            isDirty.value = true;
            // If we tweak the "Default" config, it becomes a "Custom" unsaved state
            if (loadedPresetId.value === 'default') {
                loadedPresetId.value = 'custom';
            }
        }
    }, { deep: true });

    // Record the preset pointer; sentinels normalize to null. Boot-apply lives in GenerationConfigBar.
    watch(loadedPresetId, (id) => {
        updateLocalConfig({ presetId: (id === 'default' || id === 'custom') ? null : id });
    });

    function parseParamValue(raw: string): unknown {
        if (raw === '') return '';
        try {
            return JSON.parse(raw);
        } catch {
            return raw;
        }
    }

    function buildGeneratePayload(): GenerationPayload {
        const parameters: Record<string, unknown> = {};
        
        for (const p of customParams.value) {
            if (p.key.trim()) {
                parameters[p.key.trim()] = parseParamValue(p.rawValue);
            }
        }
        
        if (reasoningEffort.value) {
            parameters['reasoning'] = { effort: reasoningEffort.value };
        }
        
        const payload: GenerationPayload = {};
        if (model.value.trim()) {
            payload.model = model.value.trim();
        }
        if (Object.keys(parameters).length > 0) {
            payload.parameters = parameters;
        }
        
        return payload;
    }

    function addParam() {
        customParams.value.push({
            id: crypto.randomUUID(),
            key: '',
            rawValue: ''
        });
    }

    function removeParam(id: string) {
        customParams.value = customParams.value.filter(p => p.id !== id);
    }

    function clearConfig() {
        isLoadingPreset = true;
        model.value = '';
        reasoningEffort.value = null;
        customParams.value = [];
        loadedPresetId.value = 'default';
        isDirty.value = false;
        nextTick(() => { isLoadingPreset = false; });
    }

    function isJsonEqual(a: unknown, b: unknown): boolean {
        if (a === b) return true;
        if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return false;
        if (Array.isArray(a) !== Array.isArray(b)) return false;

        if (Array.isArray(a) && Array.isArray(b)) {
            return a.length === b.length && a.every((item, i) => isJsonEqual(item, b[i]));
        }

        const objA = a as Record<string, unknown>;
        const objB = b as Record<string, unknown>;
        const keysA = Object.keys(objA);
        if (keysA.length !== Object.keys(objB).length) return false;

        return keysA.every(
            key => Object.prototype.hasOwnProperty.call(objB, key) && isJsonEqual(objA[key], objB[key])
        );
    }

    function pickMatch(candidates: GenerationPreset[]): GenerationPreset | null {
        if (candidates.length === 0) return null;
        const current = candidates.find(p => p.id === loadedPresetId.value);
        if (current) return current;

        return candidates.reduce((oldest, p) =>
            Date.parse(p.created_at) < Date.parse(oldest.created_at) ? p : oldest
        );
    }

    const VALID_EFFORTS = ['none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'] as const;

    function applyParameters(params: Record<string, unknown>) {
        if (params.reasoning && typeof params.reasoning === 'object' && 'effort' in params.reasoning) {
            const effort = (params.reasoning as { effort?: unknown }).effort;
            // Validate that the DB value is actually one of our supported options
            if (typeof effort === 'string' && (VALID_EFFORTS as readonly string[]).includes(effort)) {
                reasoningEffort.value = effort as typeof reasoningEffort.value;
            } else {
                reasoningEffort.value = null; // Fallback if DB has an unknown/invalid effort
            }
        } else {
            reasoningEffort.value = null;
        }

        customParams.value = Object.entries(params)
            .filter(([key]) => key !== 'reasoning')
            .map(([key, val]) => ({
                id: crypto.randomUUID(),
                key: key,
                rawValue: typeof val === 'object' ? JSON.stringify(val) : String(val)
            }));
    }

    function loadPreset(preset: GenerationPreset) {
        isLoadingPreset = true;
        loadedPresetId.value = preset.id;
        isDirty.value = false;
        model.value = preset.model || '';
        applyParameters(preset.parameters || {});

        nextTick(() => { isLoadingPreset = false; });
    }

    async function loadFromCreationData(
        creationData: { source?: string; model?: string; parameters?: Record<string, unknown> } | null | undefined,
        presets: GenerationPreset[]
    ) {
        if (!creationData || creationData.source !== 'model') return;

        const targetModel = typeof creationData.model === 'string' ? creationData.model : '';
        const targetParams = (creationData.parameters && typeof creationData.parameters === 'object') ? creationData.parameters : {};

        // Tier 1: Exact match (model + parameters) -> clean preset state
        const exactMatch = targetModel ? pickMatch(presets.filter(p => p.model === targetModel && isJsonEqual(p.parameters || {}, targetParams))) : null;
        if (exactMatch) {
            loadPreset(exactMatch);
            return;
        }

        // Tier 2: Model-only match -> load preset cleanly first, then let watcher mark params dirty
        const modelMatch = targetModel ? pickMatch(presets.filter(p => p.model === targetModel)) : null;
        if (modelMatch) {
            loadPreset(modelMatch);
            await nextTick();
            applyParameters(targetParams);
            return;
        }

        // Tier 3: No match -> clear to Default first, then let watcher flip to Custom + dirty
        clearConfig();
        await nextTick();
        model.value = targetModel;
        applyParameters(targetParams);
    }

    function buildPresetData(name: string) {
        const parameters: Record<string, unknown> = {};
        
        for (const p of customParams.value) {
            if (p.key.trim()) {
                parameters[p.key.trim()] = parseParamValue(p.rawValue);
            }
        }
        if (reasoningEffort.value) {
            parameters['reasoning'] = { effort: reasoningEffort.value };
        }
        
        return {
            name: name.trim(),
            model: model.value.trim() || null,
            parameters: parameters
        };
    }

    function handlePresetDeleted(id: string) {
        if (loadedPresetId.value === id) {
            loadedPresetId.value = 'custom';
        }
    }

    return {
        model,
        reasoningEffort,
        customParams,
        loadedPresetId,
        isDirty,
        parseParamValue,
        buildGeneratePayload,
        addParam,
        removeParam,
        clearConfig,
        loadPreset,
        loadFromCreationData,
        buildPresetData,
        handlePresetDeleted
    };
});