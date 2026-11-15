import { ref, onMounted, onUnmounted, type Ref } from 'vue';

const UP_THRESHOLD = 56;        // Past this far into a message, Up returns to its top first
const DOWN_TOLERANCE = 8;      // Skips sub-pixel rounding on Down
const BOUNDARY_TOLERANCE = 2;  // Dead zone for the boundary flags
const STICKY_EPSILON = 1;   // Drifting distance to release the following

export function useMessageScroll(
    containerRef: Ref<HTMLElement | null>,
    contentRef: Ref<HTMLElement | null>
) {
    const canScrollUp = ref(false);
    const canScrollDown = ref(false);

    // Tail-following flag. Released only from real scroll events
    let following = false;

    let resizeObserver: ResizeObserver | null = null;

    // State updates
    function updateBoundaryFlags() {
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

    function handleScroll() {
        const container = containerRef.value;
        if (!container) return;
        const maxScrollTop = Math.max(0, container.scrollHeight - container.clientHeight);
        following = container.scrollTop >= maxScrollTop - STICKY_EPSILON;
        updateBoundaryFlags();
    }

    // Content grew/shrank. Instant scroll when following
    function handleContentResize() {
        const container = containerRef.value;
        if (!container) return;
        if (following) {
            container.scrollTo({
                top: container.scrollHeight - container.clientHeight,
                behavior: 'auto'
            });
        }
        updateBoundaryFlags();
    }

    // Measure the top offsets of all message tiles
    function getMessageOffsets(container: HTMLElement): number[] {
        const containerRect = container.getBoundingClientRect();
        const tiles = container.querySelectorAll<HTMLElement>('.message-tile');
        return Array.from(tiles).map(el =>
            el.getBoundingClientRect().top - containerRect.top + container.scrollTop
        );
    }

    function scrollToY(top: number, smooth: boolean = true) {
        containerRef.value?.scrollTo({ top, behavior: smooth ? 'smooth' : 'auto' });
    }

    // Button actions
    function scrollToTop() {
        if (!canScrollUp.value) return;
        scrollToY(0);
    }

    function scrollToBottom(smooth: boolean = true) {
        const container = containerRef.value;
        if (!container) return;
        following = true;
        const maxScrollTop = Math.max(0, container.scrollHeight - container.clientHeight);
        if (maxScrollTop <= 0) return;
        scrollToY(maxScrollTop, smooth);
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

    // Bring a tile fully into view
    function scrollMessageIntoView(messageId: string) {
        const container = containerRef.value;
        if (!container) return;
        const tile = container.querySelector<HTMLElement>(`[data-message-id="${messageId}"]`);
        if (!tile) return;

        const containerTop = container.getBoundingClientRect().top;
        const tileTop = tile.getBoundingClientRect().top - containerTop;
        const tileBottom = tile.getBoundingClientRect().bottom - containerTop;

        if (tileTop < 0) {
            scrollToY(container.scrollTop + tileTop);
        } else if (tileBottom > container.clientHeight) {
            scrollToY(container.scrollTop + tileBottom - container.clientHeight);
        }
    }

    onMounted(() => {
        const container = containerRef.value;
        if (!container) return;

        container.addEventListener('scroll', handleScroll, { passive: true });

        resizeObserver = new ResizeObserver(handleContentResize);
        resizeObserver.observe(container);
        if (contentRef.value) {
            resizeObserver.observe(contentRef.value);
        }
        updateBoundaryFlags(); // No acquire at mount: fresh views start un-followed
    });

    onUnmounted(() => {
        containerRef.value?.removeEventListener('scroll', handleScroll);
        resizeObserver?.disconnect();
    });

    return {
        canScrollUp,
        canScrollDown,
        scrollToTop,
        scrollToBottom,
        scrollPrevMessage,
        scrollNextMessage,
        scrollMessageIntoView
    };
}