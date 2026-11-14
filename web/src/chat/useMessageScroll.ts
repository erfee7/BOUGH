import { ref, onMounted, onUnmounted, type Ref } from 'vue';

const UP_THRESHOLD = 56;
const DOWN_TOLERANCE = 8;
const BOUNDARY_TOLERANCE = 2;

export function useMessageScroll(
    containerRef: Ref<HTMLElement | null>,
    contentRef: Ref<HTMLElement | null>
) {
    const canScrollUp = ref(false);
    const canScrollDown = ref(false);

    function updateScrollState() {
        const container = containerRef.value;
        if (!container) {
            canScrollUp.value = false;
            canScrollDown.value = false;
            return;
        }
        const maxScrollTop = Math.max(0, container.scrollHeight - container.clientHeight);
        canScrollUp.value = container.scrollTop > BOUNDARY_TOLERANCE;
        canScrollDown.value = container.scrollTop < maxScrollTop - BOUNDARY_TOLERANCE;
    }

    function getMessageOffsets(container: HTMLElement): number[] {
        const containerRect = container.getBoundingClientRect();
        const tiles = container.querySelectorAll<HTMLElement>('.message-tile');
        return Array.from(tiles).map(el =>
            el.getBoundingClientRect().top - containerRect.top + container.scrollTop
        );
    }

    function scrollToY(top: number) {
        containerRef.value?.scrollTo({ top, behavior: 'smooth' });
    }

    function scrollToTop() {
        if (!canScrollUp.value) return;
        scrollToY(0);
    }

    function scrollToBottom() {
        const container = containerRef.value;
        if (!container || !canScrollDown.value) return;
        scrollToY(container.scrollHeight - container.clientHeight);
    }

    function scrollPrevMessage() {
        const container = containerRef.value;
        if (!container || !canScrollUp.value) return;

        const current = container.scrollTop;
        const offsets = getMessageOffsets(container);

        let target: number | undefined;
        for (let i = offsets.length - 1; i >= 0; i--) {
            if (offsets[i] < current - UP_THRESHOLD) {
                target = offsets[i];
                break;
            }
        }

        scrollToY(target ?? 0);
    }

    function scrollNextMessage() {
        const container = containerRef.value;
        if (!container || !canScrollDown.value) return;

        const current = container.scrollTop;
        const maxScrollTop = container.scrollHeight - container.clientHeight;
        const offsets = getMessageOffsets(container);

        const target = offsets.find(y => y > current + DOWN_TOLERANCE);
        scrollToY(target ?? maxScrollTop);
    }

    let resizeObserver: ResizeObserver | null = null;

    onMounted(() => {
        const container = containerRef.value;
        if (!container) return;

        container.addEventListener('scroll', updateScrollState, { passive: true });

        resizeObserver = new ResizeObserver(updateScrollState);
        resizeObserver.observe(container);
        if (contentRef.value) {
            resizeObserver.observe(contentRef.value);
        }

        updateScrollState();
    });

    onUnmounted(() => {
        containerRef.value?.removeEventListener('scroll', updateScrollState);
        resizeObserver?.disconnect();
    });

    return {
        canScrollUp,
        canScrollDown,
        scrollToTop,
        scrollToBottom,
        scrollPrevMessage,
        scrollNextMessage
    };
}