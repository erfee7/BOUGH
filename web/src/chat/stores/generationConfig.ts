import { defineStore } from 'pinia';
import { ref } from 'vue';
import { CustomParam, GenerationPayload } from '@/types';

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

    return {
        model,
        reasoningEffort,
        customParams,
        parseParamValue,
        buildGeneratePayload,
        addParam,
        removeParam
    };
});