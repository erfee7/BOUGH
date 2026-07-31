import { ref, watch, nextTick } from 'vue';

export function useAutoResizeTextarea(valueGetter: () => string) {
    const textareaRef = ref<HTMLTextAreaElement | null>(null);

    function adjustHeight() {
        const el = textareaRef.value;
        if (!el) return;
        el.style.height = 'auto'; // Reset height to recalculate accurately
        el.style.height = `${el.scrollHeight}px`;
    }

    // Watch the value so external changes (clearing input, loading edit) trigger resize
    // { immediate: true } ensures it fires on initial mount/load
    watch(valueGetter, () => {
        nextTick(adjustHeight);
    }, { immediate: true });
    
    return {
        textareaRef,
        adjustHeight
    };
}