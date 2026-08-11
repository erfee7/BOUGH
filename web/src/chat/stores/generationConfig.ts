import { defineStore } from 'pinia';
import { ref } from 'vue';
import { CustomParam, GenerationPayload, GenerationPreset } from '@/types';

export const useGenerationConfigStore = defineStore('generationConfig', () => {
    // Module-level singleton state (in-memory only for now)
    const model = ref('');
    const reasoningEffort = ref<'none' | 'minimal' | 'low' | 'medium' | 'high' | 'xhigh' | 'max' | null>(null);
    const customParams = ref<CustomParam[]>([]);

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
        model.value = '';
        reasoningEffort.value = null;
        customParams.value = [];
    }

    const VALID_EFFORTS = ['none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'] as const;

    function loadPreset(preset: GenerationPreset) {
        model.value = preset.model || '';
        const params = preset.parameters || {};
        
        if (params.reasoning && typeof params.reasoning === 'object' && 'effort' in params.reasoning) {
            const effort = params.reasoning.effort;
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

    return {
        model,
        reasoningEffort,
        customParams,
        parseParamValue,
        buildGeneratePayload,
        addParam,
        removeParam,
        clearConfig,
        loadPreset,
        buildPresetData
    };
});