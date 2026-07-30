import { Message } from '../types';

/**
 * Stable comparison helper for messages.
 * Sorts chronologically by created_at, falling back to UUID string comparison to break ties.
 */
export function compareMessages(a: Message, b: Message): number {
    const timeA = new Date(a.created_at).getTime();
    const timeB = new Date(b.created_at).getTime();
    
    if (timeA !== timeB) {
        return timeA - timeB;
    }
    
    // Fallback to string comparison for stable ordering
    return a.id.localeCompare(b.id);
}

/**
 * Walks backwards from leafId to root, returning the ordered path.
 * If leafId is missing, falls back to the globally most recent message.
 */
export function getActivePath(messages: Message[], leafId: string | null): Message[] {
    if (messages.length === 0) return [];
    
    if (!leafId) {
        const sorted = [...messages].sort(compareMessages);
        leafId = sorted[sorted.length - 1].id;
    }
    
    const path: Message[] = [];
    let currentMessage = messages.find(m => m.id === leafId);
    
    while (currentMessage) {
        path.unshift(currentMessage);
        const parentId = currentMessage.parent_id;
        if (!parentId) break;
        currentMessage = messages.find(m => m.id === parentId);
    }
    
    return path;
}

/**
 * Finds siblings sharing the same parent_id, ordered stably by created_at.
 */
export function getSiblingInfo(messageId: string, messages: Message[]): { count: number, currentIndex: number } {
    const targetMsg = messages.find(m => m.id === messageId);
    if (!targetMsg || !targetMsg.parent_id) return { count: 1, currentIndex: 0 };
    
    const siblings = messages
        .filter(m => m.parent_id === targetMsg.parent_id)
        .sort(compareMessages);
        
    const currentIndex = siblings.findIndex(m => m.id === messageId);
    return { count: siblings.length, currentIndex };
}

/**
 * Recursively finds the deepest, newest leaf in a subtree.
 * Used for the sibling-switch descend rule.
 */
export function getMostRecentDescendantLeaf(messageId: string, messages: Message[]): string {
    const children = messages.filter(m => m.parent_id === messageId);
    
    if (children.length === 0) {
        return messageId; // It's a leaf
    }
    
    const sortedChildren = [...children].sort(compareMessages);
    const mostRecentChild = sortedChildren[sortedChildren.length - 1];
    
    return getMostRecentDescendantLeaf(mostRecentChild.id, messages);
}