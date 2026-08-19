<template>
    <div class="message-details">
        <!-- Generation in progress -->
        <div v-if="status === 'pending' || status === 'streaming'" class="empty-details">
            Generating... Metadata will be available upon completion.
        </div>

        <!-- Warning for edited messages -->
        <div v-else-if="creationData?.source === 'user'" class="empty-details">
            Message edited by user. Metadata is not available.
        </div>

        <!-- Normal stats layout -->
        <template v-else>
            <!-- Model -->
            <div class="detail-row" v-if="model">
                <span class="detail-label">Model</span>
                <span class="detail-value">{{ model }}</span>
            </div>

            <!-- Parameters (Smart GUI) -->
            <div class="detail-row" v-if="parameterChips.length > 0">
                <span class="detail-label">Parameters</span>
                <div class="param-chips">
                    <span v-for="chip in parameterChips" :key="chip.label" class="param-chip">
                        {{ chip.label }}: {{ chip.value }}
                    </span>
                </div>
            </div>

            <!-- Tokens -->
            <div class="detail-row" v-if="promptTokens !== null || completionTokens !== null">
                <span class="detail-label">Tokens</span>
                <div class="token-breakdown">
                    <span v-if="promptTokens !== null">In: {{ promptTokens }}</span>
                    <span v-if="completionTokens !== null">
                        Out: {{ completionTokens }}
                        <span v-if="reasoningTokens > 0" class="sub-token">(Reasoning: {{ reasoningTokens }})</span>
                    </span>
                </div>
            </div>

            <!-- Generation Time & Speed -->
            <div class="detail-row" v-if="generationTime !== null">
                <span class="detail-label">Speed</span>
                <div class="speed-breakdown">
                    <span>{{ generationTime.toFixed(2) }}s</span>
                    <span v-if="throughput !== null">{{ throughput.toFixed(2) }} tok/s</span>
                </div>
            </div>

            <!-- Cost -->
            <div class="detail-row" v-if="cost !== null">
                <span class="detail-label">Cost</span>
                <span class="detail-value">
                    ${{ formattedCost }}
                    <span v-if="isByok" class="byok-badge"
                          title="Billed directly by the upstream provider via your own API key">
                        BYOK
                    </span>
                </span>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
    creationData?: any,
    metadata?: any,
    status?: string
}>();

const model = computed(() => props.creationData?.model);

// Smart GUI for arbitrary parameters
const parameterChips = computed(() => {
    const params = props.creationData?.parameters;
    if (!params || typeof params !== 'object' || Object.keys(params).length === 0) {
        return [];
    }
    return Object.entries(params).map(([key, value]) => {
        // Prettify label (e.g., "top_p" -> "Top P", "temperature" -> "Temperature")
        let label = key.replace(/_/g, ' ');
        label = label.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        
        // Format value (trim trailing zeros for numbers)
        let val: string;
        if (value === null) {
            val = 'null';
        } else if (typeof value === 'number' && !Number.isInteger(value)) {
            val = String(parseFloat(value.toFixed(2)));
        } else if (typeof value === 'object') {
            val = JSON.stringify(value);
        } else {
            val = String(value);
        }
        return { label, value: val };
    });
});

const promptTokens = computed(() => props.metadata?.prompt_tokens ?? null);
const completionTokens = computed(() => props.metadata?.completion_tokens ?? null);
const reasoningTokens = computed(() => props.metadata?.completion_tokens_details?.reasoning_tokens ?? 0);

const isByok = computed(() => props.metadata?.is_byok === true);
const cost = computed(() => {
    // BYOK: real spend is the upstream charge (paid directly via user's key).
    // OR's `cost` is 0 here. Fall back to `cost` if cost_details is unexpectedly missing.
    if (isByok.value) {
        return props.metadata?.cost_details?.upstream_inference_cost ?? props.metadata?.cost ?? null;
    }
    // Non-BYOK: OR's `cost` is the post-discount amount the user actually paid OR.
    return props.metadata?.cost ?? null;
});
const formattedCost = computed(() => {
    if (cost.value === null) return '0';
    // Show 6 decimal places for precise LLM costs
    return cost.value.toFixed(6);
});

// Time & Throughput
const generationTime = computed(() => props.metadata?.server_metrics?.generation_time ?? null);
const throughput = computed(() => {
    if (generationTime.value !== null && generationTime.value > 0 && completionTokens.value !== null) {
        return completionTokens.value / generationTime.value;
    }
    return null;
});
</script>

<style scoped>
.message-details {
    position: absolute;
    bottom: 100%;
    left: 57px; /* Offset slightly from the left edge */
    margin-bottom: 8px;
    
    background: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 12px 16px;
    font-size: 13px;
    color: var(--text-secondary);
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    /* Give it more space to breathe */
    min-width: 260px;
    max-width: 360px; 
    
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    z-index: 10;
    display: grid;
    grid-template-columns: auto 1fr; /* Label column hugs the longest label; values share one edge */
    align-items: center;
    gap: 8px 12px; /* row column */
}

.detail-row {
    display: contents;
}

.detail-label {
    font-weight: 600;
    color: var(--text-muted);
    font-size: 12px;
    letter-spacing: normal;
}

.detail-value {
    color: var(--text-primary);
    font-family: monospace;
    /* Ensure long model names wrap properly instead of overflowing */
    overflow-wrap: anywhere;
    word-break: break-all;
}

.empty-details {
    grid-column: 1 / -1;
}

.param-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.param-chip {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 2px 8px;
    font-size: 12px;
    color: var(--accent-blue);
}

.byok-badge {
    display: inline-block;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    color: var(--accent-blue);
    border-radius: var(--radius-sm);
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 600;
    margin-left: 6px;
    vertical-align: middle;
    cursor: help;
}

/* Hang the reasoning token as a visual sub-detail of "Out:" */
.token-breakdown {
    padding-left: 1.2em; /* Roughly matches "In: " / "Out: " prefix width */
    text-indent: -1.2em;
}

.token-breakdown, .speed-breakdown {
    display: inline; /* Continuous text: wraps as one piece instead of flex items */
    color: var(--text-primary);
    font-family: monospace;
}

.token-breakdown span + span,
.speed-breakdown span + span {
    margin-left: 16px; /* Replaces the former flex gap */
}

.sub-token {
    color: var(--text-muted);
    font-size: 11px;
    margin-left: 4px;
}

@media (max-width: 768px) {
    .message-details {
        left: 0;
        right: auto;         /* Let it size to content instead of stretching */
        min-width: 0;
        max-width: 100%;     /* Hard cap at tile width */
        width: fit-content;  /* Hug content up to the max-width cap */
    }
}
</style>