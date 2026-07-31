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
    if (range.collapsed) return; // Nothing selected
    
    const container = (range.commonAncestorContainer.nodeType === 3 
        ? range.commonAncestorContainer.parentElement 
        : range.commonAncestorContainer) as HTMLElement | null;
        
    if (!container) return;

    // Only intercept if we are inside an md-editor preview
    const previewContainer = container.closest('.md-editor-preview');
    if (!previewContainer) return;

    let resultString = '';
    let hasMath = false;

    // Walks the DOM, yielding text nodes and math elements (ignoring text inside math)
    const walker = document.createTreeWalker(
        previewContainer,
        NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
        {
            acceptNode(node) {
                if (node.nodeType === Node.TEXT_NODE) {
                    // Ignore text nodes inside KaTeX, we handle the whole formula at once
                    if (node.parentElement && node.parentElement.closest('.katex')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
                if (node.nodeType === Node.ELEMENT_NODE) {
                    if ((node as HTMLElement).classList.contains('katex')) {
                        return NodeFilter.FILTER_ACCEPT;
                    }
                    // We accept block elements to preserve paragraph breaks in mixed selections
                    const display = window.getComputedStyle(node as HTMLElement).display;
                    if (display === 'block' || display === 'list-item' || display === 'table-cell') {
                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
                return NodeFilter.FILTER_SKIP;
            }
        }
    );

    while (walker.nextNode()) {
        const node = walker.currentNode;
        // Extract exact highlighted substring from raw text nodes
        if (node.nodeType === Node.TEXT_NODE) {
            if (range.intersectsNode(node)) {
                let text = node.textContent || '';
                const start = (node === range.startContainer) ? range.startOffset : 0;
                const end = (node === range.endContainer) ? range.endOffset : text.length;
                resultString += text.substring(start, end);
            }
        // Extract LaTeX if it's a math block, else insert newlines to preserve formatting
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;
            if (range.intersectsNode(el)) {
                if (el.classList.contains('katex')) {
                    const annotation = el.querySelector('annotation[encoding="application/x-tex"]');
                    if (annotation) {
                        hasMath = true;
                        // Check if it's display math to use $$ vs $
                        const isDisplay = el.classList.contains('katex-display') || 
                                          (el.parentElement && el.parentElement.classList.contains('katex-display')) ||
                                          (el.closest('.math-block') != null);
                        
                        // Strip only leading/trailing newlines, preserving spaces (like \ )
                        const latex = (annotation.textContent || '').replace(/^[\r\n]+/, '').replace(/[\r\n]+$/, '');
                        
                        if (isDisplay) {
                            resultString += `\n$$${latex}$$\n`;
                        } else {
                            resultString += `$${latex}$`;
                        }
                    }
                } else {
                    // Block element (like <p> or <li>): preserve formatting if it doesn't contain the start of the selection
                    if (!el.contains(range.startContainer) && !resultString.endsWith('\n')) {
                        resultString += '\n';
                    }
                }
            }
        }
    }

    // Only intercept the copy action if we actually found math in the selection
    if (!hasMath) return;

    event.preventDefault();
    
    if (event.clipboardData) {
        // Clean up excessive newlines caused by block elements wrapping math
        const finalString = resultString.replace(/\n{3,}/g, '\n\n').replace(/^\n+/, '').replace(/\n+$/, '');
        event.clipboardData.setData('text/plain', finalString);
    }
}