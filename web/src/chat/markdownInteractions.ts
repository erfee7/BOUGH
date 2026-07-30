export function handleMarkdownDblClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    // Check if the target is an inline code block (not a block code, which is wrapped in <pre>)
    if (target.tagName === 'CODE' && target.parentElement?.tagName !== 'PRE') {
        const selection = window.getSelection();
        if (selection) {
            const range = document.createRange();
            range.selectNodeContents(target);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }
}

export function handleMarkdownCopy(event: ClipboardEvent) {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const container = range.commonAncestorContainer;
    const parentElement = container.nodeType === 3 ? container.parentElement : (container as HTMLElement);
    
    // If the selection is entirely within a KaTeX math element, intercept the copy
    if (parentElement) {
        const katexElement = parentElement.closest('.katex');
        if (katexElement) {
            const annotation = katexElement.querySelector('annotation[encoding="application/x-tex"]');
            if (annotation && event.clipboardData) {
                event.preventDefault(); // Stop default messy copy
                event.clipboardData.setData('text/plain', annotation.textContent || '');
            }
        }
    }
}